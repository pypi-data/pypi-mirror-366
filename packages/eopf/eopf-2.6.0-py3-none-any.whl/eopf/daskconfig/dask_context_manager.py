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
import importlib
from enum import Enum
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

import cloudpickle
import dask.config
from dask.distributed import Client
from distributed import get_client, performance_report
from importlib_metadata import PackageNotFoundError

from eopf.daskconfig import auto_gc_plugin, failure_monitor_plugin
from eopf.daskconfig.auto_gc_plugin import AutoGCPlugin
from eopf.daskconfig.failure_monitor_plugin import FailureMonitorPlugin
from eopf.exceptions import TriggeringConfigurationError
from eopf.exceptions.errors import DaskClusterNotFound
from eopf.logging.log import EOLogging

if TYPE_CHECKING:
    pass

# https://github.com/dask/distributed/issues/8695

cloudpickle.register_pickle_by_value(auto_gc_plugin)
cloudpickle.register_pickle_by_value(failure_monitor_plugin)


class ClusterType(Enum):
    LOCAL = "local"
    SSH = "ssh"
    KUBERNETES = "kubernetes"
    PBS = "pbs"
    SGE = "sge"
    LSF = "lsf"
    SLURM = "slurm"
    YARN = "yarn"
    GATEWAY = "gateway"
    ADDRESS = "address"
    CUSTOM = "custom"


def get_enum_from_value(value: str) -> ClusterType:
    for member in ClusterType:
        if member.value == value:
            return member
    raise ValueError("Value not found in the enum")


class DaskContext:
    """Representation of a dask context used to run
    dask with the correct configuration.

    Parameters
    ----------
    cluster_type: type of cluster to use
        can be one of:

            * **None**: don't create a new cluster, just connect to one
            * **local**: configure a :py:class:`~dask.distributed.LocalCluster`
            * **ssh**: configure a :py:func:`~dask.distributed.SSHCluster`
            * **kubernetes**: configure a :py:class:`~dask_kubernetes.KubeCluster`
            * **pbs**: configure a :py:class:`~dask_jobqueue.PBSCluster`
            * **sge**: configure a :py:class:`~dask_jobqueue.SGECluster`
            * **lsf**: configure a :py:class:`~dask_jobqueue.LSFCluster`
            * **slurm**: configure a :py:class:`~dask_jobqueue.SLURMCluster`
            * **slurm**: configure a :py:class:`~dask_jobqueue.SLURMCluster`
            * **yarn**: configure a :py:class:`~dask_yarn.YarnCluster`
            * **gateway**: configure a :py:class:`~dask_gateway.GatewayCluster`
            * **address**: to pass simple cluster address in the addr parameter
            * **custom**: to use Custom cluster class specified by following element in **cluster_config** element.

                - **module**: python path to module containing custom cluster
                - **cluster**: cluster class name
    address: str
        only for **str** cluster_type, specified cluster address to join.
    cluster_config: dict
        key value pairs of parameters to give to the cluster constructor
    client_config: dict
        element to configure :py:class:`~dask.distributed.Client`
    performance_report_file : Optional[str]
        path to report file
    """

    def __init__(
        self,
        cluster_type: Optional[ClusterType] = None,
        address: Optional[str] = None,
        cluster_config: Optional[dict[str, Any]] = None,
        client_config: Optional[dict[str, Any]] = None,
        dask_config: Optional[dict[str, Any]] = None,
        performance_report_file: Optional[Union[str, Path]] = None,
    ) -> None:
        self._cluster_type: Optional[ClusterType] = cluster_type
        self._cluster: Optional[Any] = None
        self._logger = EOLogging().get_logger("eopf.daskconfig.dask_context_manager")
        self._client: Optional[Client] = None
        self._performance_report_file = performance_report_file
        self._performance_report: Optional[performance_report] = None
        # See https://distributed.dask.org/en/latest/diagnosing-performance.html
        if self._performance_report_file:
            self._performance_report = performance_report(filename=self._performance_report_file)
            self._logger.info(f"Performance report file requested : {self._performance_report_file}")

        self._client_config: dict[str, Any] = client_config if client_config else {}
        self._cluster_config: dict[str, Any] = cluster_config if cluster_config else {}
        self._dask_config: dict[str, Any] = dask_config if dask_config else {}
        self._dask_config_set: Optional[dask.config.set] = None
        self._logger.info(
            f"Initialising an {cluster_type} cluster with client conf : {self._client_config} "
            f",cluster config {self._cluster_config} and dask config {self._dask_config}",
        )

        # detect any other client, this might cause conflict on the cluster
        try:
            client = get_client()
            # if a client exist log its infos
            if client is not None:
                self._logger.warning(f"A Dask client is already active: {id(client)} : {client}")
        except Exception:
            self._logger.debug("No Dask client active, proceeding")

        # need to setup dask config before instance clusters and so on
        if len(self._dask_config) != 0:
            self._logger.debug(f"Setting dask config : {self._dask_config}")
            self._dask_config_set = dask.config.set(self._dask_config)
            self._dask_config_set.__enter__()

        if address is not None and "address" not in self._client_config:
            self._client_config["address"] = address

        setup_dict: dict[ClusterType | None, Callable[[], None]] = {
            ClusterType.LOCAL: self._setup_local_cluster,
            ClusterType.SSH: self._setup_ssh_cluster,
            ClusterType.KUBERNETES: self._setup_kubernetes_cluster,
            ClusterType.PBS: self._setup_pbs_cluster,
            ClusterType.SGE: self._setup_sge_cluster,
            ClusterType.LSF: self._setup_lsf_cluster,
            ClusterType.SLURM: self._setup_slurm_cluster,
            ClusterType.YARN: self._setup_yarn_cluster,
            ClusterType.GATEWAY: self._setup_gateway_cluster,
            ClusterType.ADDRESS: self._setup_adress_cluster,
            ClusterType.CUSTOM: self._setup_custom_cluster,
            None: self._setup_none_cluster,
        }

        # setup cluster
        if self._cluster_type not in setup_dict.keys():
            raise TriggeringConfigurationError("Unhandled dask context cluster type")
        # Setup the cluster
        setup_dict[self._cluster_type]()

        self._logger.info(f"DASK Cluster : {str(self._cluster)}")

    def _setup_none_cluster(self) -> None:
        # No cluster type provided try address
        self._cluster_type = ClusterType.ADDRESS
        self._setup_adress_cluster()

    def _setup_adress_cluster(self) -> None:
        if "address" not in self._client_config:
            raise TriggeringConfigurationError(
                "address parameter or in client config " "is mandatory for STR cluster connexion",
            )

    def _setup_yarn_cluster(self) -> None:
        try:
            from dask_yarn import YarnCluster

            self._cluster = YarnCluster(**self._cluster_config)
        except ModuleNotFoundError:
            raise PackageNotFoundError("Package dask_yarn should be installed.")

    def _setup_slurm_cluster(self) -> None:
        try:
            from dask_jobqueue import SLURMCluster

            self._cluster = SLURMCluster(**self._cluster_config)
        except ModuleNotFoundError:
            raise PackageNotFoundError("Package dask_jobqueue should be installed.")

    def _setup_lsf_cluster(self) -> None:
        try:
            from dask_jobqueue import LSFCluster

            self._cluster = LSFCluster(**self._cluster_config)
        except ModuleNotFoundError:
            raise PackageNotFoundError("Package dask_jobqueue should be installed.")

    def _setup_sge_cluster(self) -> None:
        try:
            from dask_jobqueue import SGECluster

            self._cluster = SGECluster(**self._cluster_config)
        except ModuleNotFoundError:
            raise PackageNotFoundError("Package dask_jobqueue should be installed.")

    def _setup_pbs_cluster(self) -> None:
        try:
            from dask_jobqueue import PBSCluster

            self._cluster = PBSCluster(**self._cluster_config)
        except ModuleNotFoundError:
            raise PackageNotFoundError("Package dask_jobqueue should be installed.")

    def _setup_kubernetes_cluster(self) -> None:
        try:
            from dask_kubernetes import KubeCluster

            self._cluster = KubeCluster(**self._cluster_config)
        except ModuleNotFoundError:
            raise PackageNotFoundError("Package dask_kubernetes should be installed.")

    def _setup_ssh_cluster(self) -> None:
        from dask.distributed import SSHCluster

        self._cluster = SSHCluster(**self._cluster_config)

    def _setup_local_cluster(self) -> None:
        """
        Starts a local cluster. Options from dask documentation
        https://distributed.dask.org/en/latest/api.html#distributed.LocalCluster:
        name=None, n_workers=None, memory_limit: str, float, int, or None, default “auto”,
        threads_per_worker=None, processes=None, loop=None, start=None, host=None,
        ip=None, scheduler_port=0, silence_logs=30, dashboard_address=':8787', worker_dashboard_address=None,
        diagnostics_port=None, services=None, worker_services=None, service_kwargs=None, asynchronous=False,
        security=None, protocol=None, blocked_handlers=None, interface=None, worker_class=None,
        scheduler_kwargs=None, scheduler_sync_interval=1, **worker_kwargs

        """
        from dask.distributed import LocalCluster

        self._cluster = LocalCluster(**self._cluster_config)

    def _setup_custom_cluster(self) -> None:
        module_name: str = "NotFound"
        try:
            module_name = self._cluster_config.pop("module")
            cluster_class_name = self._cluster_config.pop("cluster")
            cluster = getattr(importlib.import_module(module_name), cluster_class_name)(
                **self._cluster_config,
            )
            self._cluster = cluster
        except ModuleNotFoundError:
            raise ModuleNotFoundError(f"Module {module_name} not found, corresponding package should be installed")

    def _setup_gateway_cluster(self) -> None:
        try:
            from dask_gateway import Gateway
            from dask_gateway.auth import get_auth

            # setup gateway Auth
            # one of ("kerberos", "jupŷterhub", "basic") or a python pass to the auth class
            auth_kwargs = self._cluster_config.pop("auth", {})
            n_workers = self._cluster_config.pop("n_workers", None)
            auth_type = auth_kwargs.pop("type")
            dask.config.set(gateway__auth__kwargs=auth_kwargs)
            auth = get_auth(auth_type)
            # setup gateway
            gateway_url = self._cluster_config.pop("address")
            gateway = Gateway(address=gateway_url, auth=auth)
            # reuse existing cluster ?
            previous_cluster_name = self._cluster_config.pop("reuse_cluster", None)
            if previous_cluster_name is not None:
                available_clusters = gateway.list_clusters()
                if any(previous_cluster_name == cluster.name for cluster in available_clusters):
                    self._logger.info(f"Reusing previous cluster {previous_cluster_name}")
                    self._logger.debug(
                        f"Previous cluster status page : {gateway_url}/clusters/{previous_cluster_name}/status",
                    )
                    cluster = gateway.connect(previous_cluster_name)
                else:
                    raise DaskClusterNotFound(f"Previous cluster not found on the gateway : {previous_cluster_name}")
            else:
                self._logger.info(f"Creating new cluster with config {self._cluster_config}")
                cluster = gateway.new_cluster(**self._cluster_config)
            # scale the cluster
            if n_workers is not None:
                if isinstance(n_workers, int):
                    cluster.scale(n_workers)
                elif isinstance(n_workers, dict):
                    cluster.adapt(
                        minimum=n_workers["minimum"],
                        maximum=n_workers["maximum"],
                        active=n_workers.get("active", True),
                    )
            self._cluster = cluster
        except ModuleNotFoundError:
            raise PackageNotFoundError("Package dask_gateway should be installed.")

    def __del__(self) -> None:
        if self._client is not None:
            self._client.close()
        if self._cluster is not None:
            self._cluster.close()
        if self._dask_config_set is not None:
            self._dask_config_set.__enter__()
        self._cluster = None
        self._client = None
        self._dask_config_set = None
        self._performance_report = None

    def __enter__(self) -> "DaskContext":
        self._logger.debug("Starting dask client and cluster")

        if self._cluster is not None:
            self._cluster.__enter__()
            self._logger.debug(f"Starting dask cluster : {id(self._cluster)}")
            self._client = Client(address=self._cluster, **self._client_config)
        else:
            self._logger.debug(f"No cluster created at init(), using Client({self._client_config})")
            self._client = Client(**self._client_config)
        self._logger.info(f"Dask Client : {str(self._client)}")
        self._logger.debug(f"Starting dask client : {id(self._client)}")
        self._client.register_plugin(FailureMonitorPlugin(), name="failure-monitor")
        self._client.register_plugin(AutoGCPlugin(), name="auto-gc")
        self._client.__enter__()
        self._logger.info(f"Dask dashboard address: {self._client.dashboard_link}")
        if self._performance_report:
            self._performance_report.__enter__()
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self._logger.debug(f"Stopping dask client and cluster {self}")
        if self._performance_report:
            self._performance_report.__exit__(*args, **kwargs)

        if self._client is not None:
            self._logger.debug(f"Stopping dask client : {id(self._client)}")
            self._logger.debug(f"processing : {self._client.processing()}")
            self._client.__exit__(*args, **kwargs)
            sleep(5)

        if self._cluster is not None:
            self._logger.debug(f"Stopping dask cluster : {id(self._cluster)}")
            self._cluster.__exit__(*args, **kwargs)
            sleep(5)

        if self._dask_config_set is not None:
            self._dask_config_set.__exit__(*args, **kwargs)

        self._client = None
        self._cluster = None
        self._dask_config_set = None

    @property
    def cluster(self) -> Any:
        if self._cluster is None:
            raise ValueError("No dask cluster !!!")
        return self._cluster

    @property
    def client(self) -> Client:
        if self._client is None:
            raise ValueError("No dask client !!!")
        return self._client

    def __str__(self) -> str:
        return f"cluster : {self.cluster}, client : {self.client}"
