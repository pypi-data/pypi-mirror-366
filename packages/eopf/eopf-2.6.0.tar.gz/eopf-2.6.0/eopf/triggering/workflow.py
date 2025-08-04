#
# Copyright (C) 2025 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import gc
import os.path
import re
from collections import defaultdict
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, List, Mapping, Optional, Sequence, Tuple, Type, cast

from xarray import DataTree
from zarr.errors import GroupNotFoundError

from eopf import EOConfiguration, EOContainer, EOProduct, EOZarrStore, OpeningMode
from eopf.common import dtree_utils
from eopf.common.dtree_utils import open_datatree
from eopf.common.file_utils import AnyPath
from eopf.common.functions_utils import parse_flag_expr
from eopf.common.temp_utils import EOTemporaryFolder
from eopf.computing import EOProcessingUnit
from eopf.computing.abstract import (
    AuxiliaryDataFile,
    DataType,
    MappingAuxiliary,
    MappingDataType,
)
from eopf.daskconfig import DaskContext
from eopf.daskconfig.dask_cluster_monitor import ClusterState, DaskClusterMonitor
from eopf.exceptions.error_handling import ERROR_POLICY_MAPPING, ErrorPolicy
from eopf.exceptions.errors import (
    DaskMonitorCriticalError,
    EOStoreInvalidPathError,
    MissingConfigurationParameterError,
    StoreLoadFailure,
    TriggerInvalidWorkflow,
)
from eopf.logging import EOLogging
from eopf.product.eo_validation import ValidationMode
from eopf.qualitycontrol.eo_qc_processor import EOQCProcessor
from eopf.store import EOProductStore
from eopf.triggering.interfaces import (
    EOADFStoreParserResult,
    EOInputProductParserResult,
    EOIOParserResult,
    EOOutputProductParserResult,
    EOQCTriggeringConf,
    PathType,
)


class Graph:
    """Class to represent a graph of Processing units"""

    def __init__(self, nb_vertices: int) -> None:
        self._graph: defaultdict[Any, Any] = defaultdict(list)  # dictionary containing adjacency List
        self.V = nb_vertices  # Number of vertices

    @property
    def graph(self) -> defaultdict[Any, Any]:
        return self._graph

    def add_edge(self, u: int, v: int) -> None:
        """Function to add an edge to graph"""

        self._graph[u].append(v)

    def is_root(self, u: int) -> bool:
        """
        It is a root if it has no parent
        """
        return len(self._graph[u]) == 0

    def is_leaf(self, u: int) -> bool:
        """
        It is a leaf if no one reference it in it's parent
        """
        return not any(u in v for v in self._graph.values())

    def topological_sort_util(self, v: int, visited: List[Any], stack: List[Any]) -> None:
        """A recursive function used by topological sort"""

        # Mark the current node as visited.
        visited[v] = True

        # Recur for all the vertices adjacent to this vertex
        for i in self._graph[v]:
            if visited[i] is False:
                self.topological_sort_util(i, visited, stack)

        # Push current vertex to stack which stores result
        stack.insert(0, v)

    def topological_sort(self) -> List[Any]:
        """The function to do Topological Sort. It uses recursive ``togopologicalSortUtil()``"""

        # Mark all the vertices as not visited
        visited = [False] * self.V
        stack: List[Any] = []

        # Call the recursive helper function to store Topological
        # Sort starting from all vertices one by one
        for i in range(self.V):
            if visited[i] is False:
                self.topological_sort_util(i, visited, stack)

        # reverse the order to get the processing units righ execution order
        stack.reverse()
        return stack

    def has_cyclic_dependency(self) -> bool:
        # Colors to mark the status of each vertex during DFS
        WHITE = 0  # Not visited
        GRAY = 1  # Visited but not finished
        BLACK = 2  # Finished

        def dfs(v: int) -> None:
            nonlocal has_cycle
            visited[v] = GRAY

            for neighbor in self._graph[v]:
                if visited[neighbor] == WHITE:
                    dfs(neighbor)
                elif visited[neighbor] == GRAY:
                    has_cycle = True

            visited[v] = BLACK

        # Initialize visited array
        visited = [WHITE] * self.V
        has_cycle: bool = False

        # Start DFS from each unvisited node
        for node in range(self.V):
            if visited[node] == WHITE:
                dfs(node)

        return has_cycle


@dataclass
class WorkFlowUnitDescription:
    """Dataclass used to wrap EOProcessingUnit for triggering execution"""

    active: bool
    """ Is the unit activated """
    processing_unit: EOProcessingUnit
    """Wrapped EOProcessingUnit"""
    inputs: dict[str, str]
    """ Description of the inputs to use::

        "inputs": {
                    "processing_unit_input_name" : "I/O input id" | "source_processing_unit_name.outputname"
                   }

    """
    adfs: dict[str, str]
    """ Description of the input adfs to use::

        "adfs": {
                    "adf_input_name" : "I/O adf id"
                   }

    """
    outputs: dict[str, str]
    """ Description of the outputs to write::

        "outputs": { "processing_unit_output_name" : {"id" : "I/O id"} }

    """
    parameters: dict[str, Any]
    """all kwargs to use a execution time"""

    step: int
    """ Step integer number, just for information """

    validate: bool
    """ bool to enable/disable validation if activated in the triggering """

    @property
    def identifier(self) -> Any:
        return self.processing_unit.identifier


@dataclass
class OutputStoreStatus:
    store_instance: Optional[EOProductStore]
    store_params: dict[str, Any]
    store_class: Type[EOProductStore]
    dirpath: AnyPath
    product_name: str


class EOProcessorWorkFlow:
    """

    It is used when the workflow is a list of processing units.
    Input EOProcessingUnits are sorted at init time to be sure that the
    execution can be done in the correct order.
    """

    CACHE_OUTPUT = "cache"

    def __init__(
        self,
        identifier: Any = "",
        workflow_units: Sequence[WorkFlowUnitDescription] = [],
    ) -> None:
        self._logger = EOLogging().get_logger("eopf.triggering.workflow")
        self._requested_io_outputs: dict[str, list[str]] = {}
        self._requested_io_inputs: dict[str, list[str]] = {}
        self._requested_io_adfs: dict[str, list[str]] = {}
        # reorder units
        processing_units_names = [workflow_unit.identifier for workflow_unit in workflow_units if workflow_unit.active]
        if len(set(processing_units_names)) != len(processing_units_names):
            raise TriggerInvalidWorkflow("Twice the same unit identifier in the workflow !!!!")

        punits_indices, indexed_unit_workflow, output_of_units_dict = self._preprocess_mandatory(workflow_units)
        self._punits_indices = punits_indices
        self._processing_units_graph = Graph(len(self._punits_indices))
        self._processing_units_weak_graph = Graph(len(self._punits_indices))
        # create vertices of the processing_units_graph
        for workflow_unit in workflow_units:
            if not workflow_unit.active:
                break

            # create the input/output dependency graph
            for unit_input_name, input_product_id in workflow_unit.inputs.items():
                # input id is either an I/O Id or <source_process_uni>.<outputid>
                pu_id = input_product_id.split(".")[0]
                if pu_id in processing_units_names:
                    self._processing_units_graph.add_edge(
                        self._punits_indices[workflow_unit.identifier],
                        self._punits_indices[pu_id],
                    )
                    self._processing_units_weak_graph.add_edge(
                        self._punits_indices[workflow_unit.identifier],
                        self._punits_indices[pu_id],
                    )
                elif input_product_id in output_of_units_dict:
                    for unit_id in output_of_units_dict[input_product_id]:
                        if unit_id != workflow_unit.identifier:
                            self._processing_units_graph.add_edge(
                                self._punits_indices[workflow_unit.identifier],
                                self._punits_indices[unit_id],
                            )
                else:
                    # create the list of products that will be requested in io section
                    if unit_input_name in workflow_unit.processing_unit.get_mandatory_input_list(
                        **workflow_unit.parameters,
                    ):
                        self._requested_io_inputs[input_product_id] = self._requested_io_inputs.get(
                            input_product_id,
                            [],
                        )
                        self._requested_io_inputs.get(input_product_id, []).append(
                            f"{workflow_unit.identifier}.{unit_input_name}",
                        )
            # create the list of adfs that will be requested in io section
            for adf_name, adf_id in workflow_unit.adfs.items():
                if adf_name in workflow_unit.processing_unit.get_mandatory_adf_list(**workflow_unit.parameters):
                    self._requested_io_adfs[adf_id] = self._requested_io_adfs.get(adf_id, [])
                    self._requested_io_adfs[adf_id].append(f"{workflow_unit.identifier}.{adf_name}")
            # create the list of outputs that will be provided
            for output_name, output_id in workflow_unit.outputs.items():
                if output_id == EOProcessorWorkFlow.CACHE_OUTPUT:
                    break
                self._requested_io_outputs[output_id] = self._requested_io_outputs.get(output_id, [])
                self._requested_io_outputs[output_id].append(f"{workflow_unit.identifier}.{output_name}")

        if self._processing_units_graph.has_cyclic_dependency():
            raise TriggerInvalidWorkflow("Workflow has cyclic dependencies, only acyclic allowed")
        order = self._processing_units_graph.topological_sort()
        self._logger.debug(f"Dependency graph : {self._processing_units_graph.graph}")
        self._workflow = [indexed_unit_workflow[o] for o in order]

    def _preprocess_mandatory(
        self,
        workflow_units: Sequence[WorkFlowUnitDescription],
    ) -> Tuple[dict[Any, int], dict[int, WorkFlowUnitDescription], dict[str, list[str]]]:
        index = 0
        punits_indices = {}
        indexed_unit_workflow = {}
        output_of_units_dict: dict[str, list[str]] = {}
        # Build some infos and validate mandatory inputs of units
        for workflow_unit in workflow_units:
            if not workflow_unit.active:
                break
            punits_indices[workflow_unit.identifier] = index
            indexed_unit_workflow[index] = workflow_unit
            index += 1
            mandatory_input_list = workflow_unit.processing_unit.get_mandatory_input_list(
                **workflow_unit.parameters,
            )
            if not all(elem in workflow_unit.inputs.keys() for elem in mandatory_input_list):
                raise TriggerInvalidWorkflow(
                    f"Missing mandatory input for {workflow_unit.identifier} : {mandatory_input_list}",
                )
            mandatory_adf_list = workflow_unit.processing_unit.get_mandatory_adf_list(
                **workflow_unit.parameters,
            )
            if not all(elem in workflow_unit.adfs.keys() for elem in mandatory_adf_list):
                raise TriggerInvalidWorkflow(
                    f"Missing mandatory adf input for {workflow_unit.identifier} : {mandatory_adf_list}",
                )
            for output in workflow_unit.outputs.items():
                output_of_units_dict.setdefault(output[1], [])
                output_of_units_dict[output[1]].append(workflow_unit.identifier)
        return punits_indices, indexed_unit_workflow, output_of_units_dict

    def run_workflow(
        self,
        io_config: EOIOParserResult,
        dask_context: DaskContext | None,
        eoqc: Optional[EOQCTriggeringConf],
    ) -> None:

        # If datatree option then deactivate validation
        if bool(EOConfiguration().triggering__use_datatree):
            self._logger.info("Datatree mode activated, deactivating validation")
            EOConfiguration()["triggering.validate_run"] = False

        # i/o config
        inputs_io_products: dict[str, EOInputProductParserResult] = {p.id: p for p in io_config.input_products}
        inputs_io_adfs: dict[str, EOADFStoreParserResult] = {p.id: p for p in io_config.adfs}
        output_io_products: dict[str, EOOutputProductParserResult] = {p.id: p for p in io_config.output_products}

        # Validate the workflow consistency
        self.validate_workflow(
            inputs_io_adfs,
            inputs_io_products,
            output_io_products,
        )

        # Instance EOQCProcessor
        if eoqc is not None:
            self._logger.debug("Instanciating EOQCProcessor")
            _eoqc_processor: EOQCProcessor = EOQCProcessor(
                config_folders=cast("List[AnyPath | str]", eoqc.config_folders),
                parameters=eoqc.parameters,
                update_attrs=eoqc.update_attrs,
                report_path=eoqc.report_path,
            )
        else:
            _eoqc_processor = EOQCProcessor()

        # Open input products
        io_opened_products: Mapping[str, DataType | Iterable[DataType]] = self.open_input_products(
            inputs_io_products,
        )
        # List ADFs
        io_interpreted_adf = self.list_input_adfs(inputs_io_adfs)

        self._logger.info("Starting workflow run")
        self._run(
            inputs=io_opened_products,
            adfs=io_interpreted_adf,
            output_io_products=output_io_products,
            eoqc_processor=_eoqc_processor,
            dask_context=dask_context,
            validate=EOConfiguration().triggering__validate_run,
            validation_mode=parse_flag_expr(EOConfiguration().triggering__validate_mode, ValidationMode),
        )

        # End of computation part
        self._logger.info("Computation finished and output products written !")

    def _run(
        self,
        inputs: MappingDataType,
        output_io_products: Mapping[str, EOOutputProductParserResult],
        eoqc_processor: EOQCProcessor,
        validate: bool,
        validation_mode: ValidationMode,
        dask_context: DaskContext | None,
        adfs: Optional[MappingAuxiliary] = None,
        **kwargs: Any,
    ) -> None:
        """

        Parameters
        ----------
        inputs : MappingDataType
            Input dictionary
        adfs : Optional[MappingAuxiliary]
            Input ADF dictionary
        kwargs :
            Any other parameters

        Returns
        -------
         MappingDataType : Dictionary of the various internal outputs mapped to payload I/O identifier
         Output keys are constructed as:
            {unit_description.identifier}.{processing_unit_output_name}.{output_payload_io_id}

        """
        # Error policy
        try:
            error_policy_handler: ErrorPolicy = ERROR_POLICY_MAPPING[EOConfiguration().triggering__error_policy]()
        except KeyError:
            raise TriggerInvalidWorkflow(f"Error policy {EOConfiguration().triggering__error_policy} is not valid")

        if EOConfiguration().triggering__dask_monitor__enabled:
            dask_monitor = DaskClusterMonitor()
        else:
            dask_monitor = None

        store_instances: dict[str, List[OutputStoreStatus]] = {}
        available_products: dict[str, DataType | Iterable[DataType]] = dict(inputs)
        available_store_instances: dict[str, List[OutputStoreStatus]] = {}
        if adfs is not None:
            available_adfs: dict[str, AuxiliaryDataFile] = {adf.name: adf for adf in adfs.values()}
        else:
            available_adfs = {}

        try:
            for unit_description in self._workflow:
                if not unit_description.active:
                    self._logger.info(f"{unit_description.processing_unit.identifier} is not activated")
                    break
                try:
                    # check cluster health
                    if dask_monitor is not None:
                        cluster_state = dask_monitor.check()
                        if (
                            EOConfiguration().triggering__dask_monitor__cancel
                            and parse_flag_expr(EOConfiguration().triggering__dask_monitor__cancel_state, ClusterState)
                            == cluster_state
                        ):
                            self._logger.error(f"Cluster is in error state ! {[s.name for s in cluster_state]}")
                            raise DaskMonitorCriticalError(
                                f"Cluster is in error state ! {[s.name for s in cluster_state]}",
                            )

                    self._logger.info(f"Available product {available_products.keys()}")
                    unit_outputs: MappingDataType = self.run_processing_unit(
                        available_adfs,
                        available_products,
                        available_store_instances,
                        unit_description,
                        validate,
                        validation_mode,
                    )
                    self._handle_unit_outputs(
                        available_products,
                        available_store_instances,
                        eoqc_processor,
                        output_io_products,
                        store_instances,
                        unit_description,
                        unit_outputs,
                    )
                    del unit_outputs
                    gc.collect()
                except Exception as e:
                    error_policy_handler.handle(e)
        finally:
            # No longer needed at this point
            self._logger.info("Exited the loop")
            available_products.clear()
            available_store_instances.clear()
            try:
                # Close the store, cancel if failures detected
                self._close_store_instances(store_instances, cancel_flush=len(error_policy_handler.errors) != 0)
            except Exception as e:
                error_policy_handler.handle(e)
            error_policy_handler.finalize()

        return None

    def _handle_unit_outputs(
        self,
        available_products: dict[str, DataType | Iterable[DataType]],
        available_store_instances: dict[str, List[OutputStoreStatus]],
        eoqc_processor: EOQCProcessor,
        output_io_products: Mapping[str, EOOutputProductParserResult],
        store_instances: dict[str, List[OutputStoreStatus]],
        unit_description: WorkFlowUnitDescription,
        unit_outputs: MappingDataType,
    ) -> None:
        for output_payload_regex, output_payload_id in unit_description.outputs.items():
            matched: bool = False
            for output_name in unit_outputs.keys():
                if re.match(output_payload_regex, output_name):
                    self._logger.info(
                        f"Matched {output_payload_id} with {unit_description.identifier}.{output_name}",
                    )
                    matched = True
                    if output_payload_id == EOProcessorWorkFlow.CACHE_OUTPUT:
                        if EOConfiguration().get("triggering__create_temporary", True):
                            output_payload_id = f"{unit_description.identifier}.{output_name}"
                            # special cache mode
                            output_io_param = EOOutputProductParserResult(
                                store_class=EOZarrStore,
                                store_params={},
                                id=output_payload_id,
                                type=PathType.Folder,
                                store_type="zarr",
                                path=EOTemporaryFolder().get_uuid_subfolder(),
                                opening_mode=OpeningMode.CREATE,
                                apply_eoqc=False,
                            )
                        else:
                            self._logger.warning(
                                "Requested CACHE writing but triggering__create_temporary==False, discarded",
                            )
                            break
                    else:
                        output_io_param = output_io_products[output_payload_id]

                    available_store_instances[f"outputs.{output_payload_id}"] = available_store_instances.get(
                        f"outputs.{output_payload_id}",
                        [],
                    )
                    current_output = unit_outputs[output_name]
                    if not isinstance(current_output, (EOProduct, EOContainer, DataTree)) and isinstance(
                        current_output,
                        Iterable,
                    ):
                        self._logger.debug(f"Iterable found in {output_name}")

                        store_instances[f"{unit_description.identifier}.{output_name}.{output_payload_id}"] = []
                        for eo_data in current_output:
                            if isinstance(eo_data, (EOProduct, EOContainer, DataTree)):
                                store_instance = self._write_single_output(
                                    eo_data,
                                    eoqc_processor,
                                    output_io_param.store_class,
                                    output_io_param.store_params,
                                    output_io_param.id,
                                    output_io_param.type,
                                    output_io_param.path,
                                    output_io_param.opening_mode,
                                    output_io_param.apply_eoqc,
                                )
                                store_instances[
                                    f"{unit_description.identifier}.{output_name}.{output_payload_id}"
                                ].append(store_instance)
                                available_store_instances[f"outputs.{output_payload_id}"].append(
                                    store_instance,
                                )
                            else:
                                raise TriggerInvalidWorkflow(
                                    f"Output {output_name} contains invalid data : "
                                    f"{type(eo_data)} {type(current_output)}",
                                )
                    elif isinstance(current_output, (EOProduct, EOContainer, DataTree)):
                        store_instance = self._write_single_output(
                            current_output,
                            eoqc_processor,
                            output_io_param.store_class,
                            output_io_param.store_params,
                            output_io_param.id,
                            output_io_param.type,
                            output_io_param.path,
                            output_io_param.opening_mode,
                            output_io_param.apply_eoqc,
                        )
                        store_instances[f"{unit_description.identifier}.{output_name}.{output_payload_id}"] = [
                            store_instance,
                        ]
                        available_store_instances[f"outputs.{output_payload_id}"].append(store_instance)
                    else:
                        raise TriggerInvalidWorkflow(f"Output {output_name} is not a valid output DataType")
            if not matched:
                self._logger.warning(
                    f"{output_payload_regex} haven't match with any of {unit_description.identifier} outputs, "
                    f"available outputs : {unit_outputs.keys()}",
                )
        if not self._processing_units_weak_graph.is_leaf(self._punits_indices[unit_description.identifier]):
            for unit_output in unit_outputs.items():
                available_products[f"{unit_description.identifier}.{unit_output[0]}"] = unit_output[1]

    def _close_store_instances(
        self,
        store_instances: dict[str, list[OutputStoreStatus]],
        cancel_flush: bool = False,
    ) -> None:
        for output_unit_id, store_results in store_instances.items():
            self._logger.info(f"Closing id : {output_unit_id}")
            self._logger.debug(f"Closing Stores: {store_results}")
            for store_result in store_results:
                if store_result.store_instance is not None and store_result.store_instance.is_open():
                    store_result.store_instance.close(cancel_flush=cancel_flush)
                    store_result.store_instance = None
                    gc.collect()
            store_results.clear()
        store_instances.clear()
        gc.collect()

    def run_processing_unit(
        self,
        available_adfs: dict[str, AuxiliaryDataFile],
        available_products: dict[str, DataType | Iterable[DataType]],
        available_store_instances: dict[str, List[OutputStoreStatus]],
        unit_description: WorkFlowUnitDescription,
        validate: bool,
        validation_mode: ValidationMode,
    ) -> MappingDataType:
        unit_inputs: dict[str, Any] = {}
        for prod_name, prod_id in unit_description.inputs.items():
            self._logger.debug(f"Requesting : {prod_id} in {available_store_instances}")
            try:
                if f"outputs.{prod_id}" in available_store_instances:
                    output_product_statuses = available_store_instances[f"outputs.{prod_id}"]
                    self._logger.info(f"Reusing previous outputs : {output_product_statuses}")
                    if len(output_product_statuses) > 1:
                        unit_inputs[prod_name] = []
                        for prod_tuple in available_store_instances[f"outputs.{prod_id}"]:
                            if isinstance(prod_tuple, OutputStoreStatus):
                                if prod_tuple.store_instance is not None and prod_tuple.store_instance.is_open():
                                    self._logger.info(
                                        f"Previous store {prod_tuple.store_instance} is not closed, closing it",
                                    )
                                    prod_tuple.store_instance.close()
                                    prod_tuple.store_instance = None
                                unit_inputs[prod_name].append(
                                    self._open_product(
                                        store_params=prod_tuple.store_params,
                                        store_class=prod_tuple.store_class,
                                        product_anypath=prod_tuple.dirpath,
                                        product_id=prod_tuple.product_name,
                                    ),
                                )
                            else:
                                raise TriggerInvalidWorkflow("Not a tuple found un output product dict")
                    else:
                        prod_tuple = available_store_instances[f"outputs.{prod_id}"][0]
                        if prod_tuple.store_instance is not None and prod_tuple.store_instance.is_open():
                            self._logger.info(f"Previous store {prod_tuple.store_instance} is not closed, closing it")
                            prod_tuple.store_instance.close()
                            prod_tuple.store_instance = None

                        unit_inputs[prod_name] = self._open_product(
                            store_params=prod_tuple.store_params,
                            store_class=prod_tuple.store_class,
                            product_anypath=prod_tuple.dirpath,
                            product_id=prod_tuple.product_name,
                        )

                else:
                    unit_inputs[prod_name] = available_products[prod_id]
            except KeyError as e:
                if prod_name in unit_description.processing_unit.get_mandatory_input_list(
                    **unit_description.parameters,
                ):
                    raise TriggerInvalidWorkflow(
                        f"Missing input in pointers list : {e} for ProcessingUnit {unit_description.identifier}",
                    )
        unit_adfs = {}
        for adf_name, adf_id in unit_description.adfs.items():
            try:
                unit_adfs[adf_name] = available_adfs[adf_id]
            except KeyError as e:
                if adf_id in unit_description.processing_unit.get_mandatory_adf_list(**unit_description.parameters):
                    raise TriggerInvalidWorkflow(
                        f"Missing input adf in payload : {e} for ProcessingUnit {unit_description.identifier}",
                    )
        self._logger.debug(
            f"RUN {unit_description.processing_unit.identifier} with input {unit_inputs.keys()}, "
            f"adf {unit_adfs.keys()} and parameters {unit_description.parameters}",
        )
        if not validate or not unit_description.validate:
            unit_outputs = unit_description.processing_unit.run_validating(
                inputs=unit_inputs,
                adfs=unit_adfs,
                validation_mode=ValidationMode.STRUCTURE,
                **unit_description.parameters,
            )
        else:
            unit_outputs = unit_description.processing_unit.run_validating(
                inputs=unit_inputs,
                adfs=unit_adfs,
                validation_mode=validation_mode,
                **unit_description.parameters,
            )
        if not isinstance(unit_outputs, dict):
            raise TriggerInvalidWorkflow(f"ProcessingUnit {unit_description.identifier} has not output a dict")
        return unit_outputs

    def list_input_adfs(
        self,
        inputs_io_adfs: dict[str, EOADFStoreParserResult],
    ) -> dict[str, AuxiliaryDataFile]:
        """
        Convert ADF definition from TT to ADF structures
        Parameters
        ----------
        processing_workflow
        inputs_io_adfs

        Returns
        -------
        io_interpreted_adf
        """
        io_interpreted_adf: dict[str, AuxiliaryDataFile] = {}
        for adf in inputs_io_adfs.values():
            adf_id = adf.id
            new_adf = AuxiliaryDataFile(name=adf_id, path=adf.path, store_params=adf.store_params)
            if not new_adf.path.exists() and adf_id in self._requested_io_adfs:
                raise TriggerInvalidWorkflow(
                    f"{adf_id} adf is requested for {self._requested_io_adfs[adf_id]}" f" but is not able to open it",
                )
            io_interpreted_adf[adf_id] = new_adf
            self._logger.info(f"Adding ADF : {new_adf}")
        return io_interpreted_adf

    def open_input_products(
        self,
        inputs_io_products: Mapping[str, EOInputProductParserResult],
    ) -> MappingDataType:
        """
        Open the input products defined in the TT
        Parameters
        ----------

        inputs_io_products : TT products infos

        Returns
        -------
        input products mapping
        """
        io_opened_products: dict[str, DataType | Iterable[DataType]] = {}
        for input_product in inputs_io_products.values():
            self._logger.info(f"Opening product : {input_product}")
            input_product_anypath: AnyPath = input_product.path
            self._logger.debug(f"{input_product_anypath.__repr__()}")
            product_id = input_product.id
            input_type = input_product.type
            store_params = input_product.store_params
            store_class = input_product.store_class

            product_path_list = [input_product_anypath]
            if input_type == PathType.Regex:
                if "regex" not in store_params:
                    raise KeyError("missing regex param in store_params for regex selection")
                product_path_list = input_product_anypath.glob(store_params["regex"])
                if "multiplicity" in store_params:
                    if store_params["multiplicity"] == "exactly_one":
                        if len(product_path_list) != 1:
                            raise TriggerInvalidWorkflow(
                                f"Requested a single product for {product_id}, found {len(product_path_list)}",
                            )
                    elif store_params["multiplicity"] == "at_least_one":
                        if len(product_path_list) == 0:
                            raise TriggerInvalidWorkflow(f"Requested at least one product for {product_id}, found 0")
                    elif store_params["multiplicity"] == "more_than_one":
                        if len(product_path_list) < 2:
                            raise TriggerInvalidWorkflow(
                                f"Requested more than one product for {product_id}, found {len(product_path_list)}",
                            )
                    elif store_params["multiplicity"].isdigit():
                        number_of_res = int(store_params["multiplicity"])
                        if len(product_path_list) < number_of_res:
                            raise TriggerInvalidWorkflow(
                                f"Requested at least {number_of_res} product for {product_id},"
                                f" found {len(product_path_list)}",
                            )
                    else:
                        raise TriggerInvalidWorkflow(
                            "Unknown multiplicity value : exactly_one, at_least_one,"
                            " more_than_one or a digit requested",
                        )
            elif input_type == PathType.Folder:
                product_path_list = input_product_anypath.ls()
            try:
                if len(product_path_list) == 0:
                    raise TriggerInvalidWorkflow(f"No product found for : {input_product} !!!!")
                if len(product_path_list) > 1:
                    io_opened_products[product_id] = []
                    for p in product_path_list:
                        product = self._open_product(store_params, store_class, p, product_id)
                        # Ignore type as it seems mypy doesn't detect that it is a list
                        io_opened_products[product_id].append(product)  # type: ignore
                else:
                    self._logger.info(f"Opening {product_path_list}")
                    io_opened_products[product_id] = self._open_product(
                        store_params,
                        store_class,
                        product_path_list[0],
                        product_id,
                    )
            except (
                StoreLoadFailure,
                EOStoreInvalidPathError,
                TriggerInvalidWorkflow,
                GroupNotFoundError,
            ) as err:
                if product_id in self._requested_io_inputs:
                    raise TriggerInvalidWorkflow(
                        f"{product_id} input is requested for {self._requested_io_inputs[product_id]}"
                        f" but we are not able to open it",
                    ) from err
        return MappingProxyType(io_opened_products)

    def _open_product(
        self,
        store_params: dict[str, Any],
        store_class: Type[EOProductStore],
        product_anypath: AnyPath,
        product_id: str,
    ) -> DataType:
        # DataTree prevails in case of zarr store and datatree activated
        self._logger.info(f"Input read : {product_anypath} with params {store_params}")
        self._logger.debug(f"Datatree flag : {bool(EOConfiguration().triggering__use_datatree)}")
        if bool(EOConfiguration().triggering__use_datatree):
            if store_class == EOZarrStore:
                product: DataType = open_datatree(product_anypath, product_id)
            else:
                tmp_product: EOProduct | EOContainer = (
                    store_class(url=product_anypath)
                    .open(**store_params)
                    .load(
                        product_id,
                    )
                )
                if isinstance(tmp_product, EOContainer):
                    raise TriggerInvalidWorkflow("EOContainer not supported in datatree conversion")
                product = tmp_product.to_datatree()
        else:
            product = store_class(url=product_anypath).open(**store_params).load(product_id)
        return product

    def validate_workflow(
        self,
        inputs_io_adfs: Mapping[str, EOADFStoreParserResult],
        inputs_io_products: Mapping[str, EOInputProductParserResult],
        output_io_products: Mapping[str, EOOutputProductParserResult],
    ) -> None:
        """
        Validate that the workflow is ok to be run, if not raise TriggerInvalidWorkFlow
        Parameters
        ----------
        inputs_io_adfs
        inputs_io_products
        output_io_products

        Returns
        -------
        None

        Raises
        ------
        TriggerInvalidWorkflow
        """
        # Do some verification
        for requested_input, units_requesting in self._requested_io_inputs.items():
            if requested_input not in inputs_io_products:
                raise TriggerInvalidWorkflow(
                    f"{requested_input} input is requested for {units_requesting}"
                    f" but is not available in I/O configuration",
                )
        for requested_adf, units_requesting in self._requested_io_adfs.items():
            if requested_adf not in inputs_io_adfs:
                raise TriggerInvalidWorkflow(
                    f"{requested_adf} adf input is requested for {units_requesting}"
                    f" but is not available in I/O adf configuration",
                )
        for requested_output, units_requesting in self._requested_io_outputs.items():
            if requested_output not in output_io_products:
                raise TriggerInvalidWorkflow(
                    f"{requested_output} output is requested for {units_requesting}"
                    f" but is not available in I/O configuration",
                )
            if len(units_requesting) > 1 and output_io_products[requested_output].type != PathType.Folder:
                raise TriggerInvalidWorkflow(
                    f"{requested_output} output is requested multiple times for {units_requesting}"
                    f" but is not a folder type",
                )
        # verify conf
        try:
            EOConfiguration().validate_mandatory_parameters(throws=True)
        except MissingConfigurationParameterError as e:
            raise TriggerInvalidWorkflow("Missing EOConfiguration params to run the TaskTable") from e

    def _write_single_output(
        self,
        eo_data: DataType,
        eoqc_processor: EOQCProcessor,
        store_class: Type[EOProductStore],
        store_params: dict[str, Any],
        output_id: str,
        output_type: PathType,
        output_path: AnyPath,
        opening_mode: OpeningMode,
        apply_eoqc: bool,
    ) -> OutputStoreStatus:

        self._logger.info(
            f"In single product write {output_id} of type {output_type} in {output_path} "
            f"with param {store_params}: {eo_data.name}",
        )

        if bool(EOConfiguration().triggering__use_datatree):
            if isinstance(eo_data, DataTree):
                if store_class == EOZarrStore:
                    if output_type == PathType.Folder:
                        if EOConfiguration().triggering__use_default_filename:
                            product_name = dtree_utils.get_default_file_name_datatree(eo_data)
                        else:
                            product_name = eo_data.name + ".zarr" if eo_data.name is not None else ""
                        dirpath_anypath: AnyPath = output_path
                    else:
                        dirpath_anypath = output_path.dirname()
                        product_name = output_path.basename
                    if not dirpath_anypath.exists():
                        dirpath_anypath.mkdir()

                    self._logger.info(
                        f"Writing Datatree {product_name} to {dirpath_anypath}/{product_name} "
                        f"with params {store_params}",
                    )
                    dtree_utils.write_datatree(
                        eo_data,
                        dirpath_anypath / product_name,
                        mode=opening_mode.value.file_opening_mode,
                        **store_params,
                    )
                    return OutputStoreStatus(
                        None,
                        store_params,
                        store_class,
                        dirpath_anypath / product_name,
                        product_name,
                    )
                else:
                    eo_product = EOProduct.from_datatree(eo_data)
            else:
                self._logger.warning(
                    "Output product is not a DataTree, product will not be written with xarray.",
                )
                self._logger.warning(
                    f"Product type: {type(eo_data)}",
                )
                eo_product = cast(EOProduct, eo_data)
        else:
            eo_product = cast(EOProduct, eo_data)
        if output_type == PathType.Folder:
            if EOConfiguration().triggering__use_default_filename:
                product_name = eo_product.get_default_file_name_no_extension()
            else:
                product_name = eo_product.name if eo_product.name is not None else ""
            dirpath_anypath = output_path
        else:
            dirpath_anypath = output_path.dirname()
            product_name = output_path.basename
        if not dirpath_anypath.exists():
            dirpath_anypath.mkdir()
        if store_class == EOZarrStore:
            store_params.setdefault("delayed_writing", True)
            store_params.setdefault("delayed_consolidate", True)
        output_store = store_class(url=dirpath_anypath).open(mode=opening_mode, **store_params)
        # This will write the product
        self._logger.info(
            f"Writing eoproduct {product_name} to {dirpath_anypath}/{(product_name + output_store.EXTENSION)} "
            f"with params {store_params}",
        )
        if EOConfiguration().has_value("dask__export_graphs"):
            folder = AnyPath.cast(EOConfiguration().dask__export_graphs)
            self._logger.info(f"EOVariables Dask graphs export requested in {folder}")
            folder.mkdir(exist_ok=True)
            eo_product.export_dask_graph(folder)
        # Apply qualitycontrol if requested
        if apply_eoqc and isinstance(eo_product, EOProduct):
            eoqc_processor.check(eo_product)
        # Effectively write it down
        output_store[product_name] = eo_product

        return OutputStoreStatus(
            output_store,
            store_params,
            store_class,
            dirpath_anypath / (os.path.splitext(product_name)[0] + output_store.EXTENSION),
            output_id,
        )
