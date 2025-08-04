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
import copy
from pathlib import Path
from typing import Any, Dict, Optional

import xarray as xr
from overrides import overrides

from eopf import EOContainer, EOLogging, EOProduct
from eopf.common.file_utils import AnyPath
from eopf.store.mapping_manager import EOPFAbstractMappingManager
from eopf.store.s2converters.convert_s02msi_l1ab_safe import S02MSIL1ABProductConversion
from eopf.store.s2converters.convert_s02msi_tile_safe import (
    open_s2msi_tile_safe_product,
)
from eopf.store.safe import EOSafeInit

# mypy: disable-error-code="union-attr"


def recursive_update(
    d1: dict[Any, Any],
    d2: dict[Any, Any],
    mode_for_dict: str = "merge",
    mode_for_list: str = "replace",
    mode_for_set: str = "replace",
) -> None:
    """
    Recursively updates dictionary `d1` with values from `d2`,
    allowing separate modes for handling dictionaries, lists, and sets.

    Arguments:
    - d1: The destination dictionary to update.
    - d2: The source dictionary to update from.
    - mode_for_dict: The update mode for dictionaries (default: "replace"):

        * "replace": Overwrite existing keys.
        * "add": Add only new keys.
        * "merge": Recursively merge keys.

    - mode_for_list: The update mode for lists (default: "replace"):

        * "replace": Overwrite existing lists.
        * "merge": Concatenate lists.

    - mode_for_set: The update mode for sets (default: "replace"):

        * "replace": Overwrite existing sets.
        * "merge": Union of sets.

    Returns:
    - The updated dictionary `d1`.
    """
    for key, value in d2.items():
        if key in d1:
            if isinstance(value, dict) and isinstance(d1[key], dict):
                if mode_for_dict == "merge":
                    recursive_update(
                        d1[key],
                        copy.copy(value),
                        mode_for_dict=mode_for_dict,
                        mode_for_list=mode_for_list,
                        mode_for_set=mode_for_set,
                    )
                elif mode_for_dict == "replace":
                    d1[key] = value
                elif mode_for_dict == "add":
                    pass  # Keep existing keys, do nothing
            elif isinstance(value, list) and isinstance(d1[key], list):
                if mode_for_list == "merge":
                    d1[key].extend(value)
                elif mode_for_list == "replace":
                    d1[key] = copy.copy(value)
            elif isinstance(value, set) and isinstance(d1[key], set):
                if mode_for_set == "merge":
                    d1[key].update(value)
                elif mode_for_set == "replace":
                    d1[key] = copy.copy(value)
            else:
                if isinstance(d1[key], (list, dict, set)):
                    # We try to update a dict, set or list with something not compatible, keep initial value
                    # logger.warning(f"Cannot update data of type {type(d1[key])} with data of type {type(value)}")
                    pass
                else:
                    d1[key] = value  # For non-iterable types, always replace
        else:
            d1[key] = copy.deepcopy(value)  # Add new keys from d2


def decode_datasets(dtree: xr.DataTree) -> None:
    for ds_path, ds in dtree.to_dict().items():
        try:
            dtree[ds_path] = xr.decode_cf(ds)
        except ValueError:
            pass


class SentinelToolBoxSafeInit(EOSafeInit):
    """
    Bind the sentinel toolbox converter to the SafeStore

    .. code-block:: JSON

            "init_function": {
                   "module" : "eopf.store.sentineltoolbox_bindings",
                   "class" : "SentinelToolBoxSafeInit"
            },

    """

    def init_container(
        self,
        url: AnyPath,
        name: str,
        attrs: Dict[str, Any],
        product_type: str,
        processing_version: str,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> EOContainer:
        raise NotImplementedError("Container mode not implement in this init class")

    @overrides
    def init_product(
        self,
        url: AnyPath,
        name: str,
        attrs: Dict[str, Any],
        product_type: str,
        processing_version: str,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        metadata_only: bool = False,
        **eop_kwargs: Any,
    ) -> EOProduct:
        if metadata_only:
            return EOProduct(name, attrs=attrs)
        else:
            if product_type in ("S02MSIL1A", "S02MSIL1B", "S02MSIL1C", "S02MSIL2A"):

                if product_type in ("S02MSIL1A", "S02MSIL1B"):
                    convertor_l1ab = S02MSIL1ABProductConversion(
                        safe_product_path=Path(url.path),
                        product_level=product_type[-3:],  # type: ignore
                    )  # , output_product_type = "DataTree")
                    # you can pass args:
                    # detector_ids=("d01", ...), band_names=("b01", ...) to limit to some detectors/bands
                    dtree = convertor_l1ab.convert_s2msi_l1_safe_product()
                elif product_type in ("S02MSIL1C", "S02MSIL2A"):
                    # these converters do not decode data by default because it was used to convert safe to zarr
                    # and in memory datatree was not used. So it was useless to decode then encode data

                    dtree = open_s2msi_tile_safe_product(Path(url.path), product_level=product_type[-3:])

                    # In CPM, EOSafeStore can be used to open safe path and manipulate EOProduct directly after
                    # so we need to support this case by explicitly decoding variables
                    # TODO: call next line only if eopf conf mask_and_scale=True
                    decode_datasets(dtree)

                else:
                    raise NotImplementedError(product_type)

                # Update dtree attrs (metadata) with values coming from mappings.
                # that means that every change done in mapping is directly visible in final product
                # that approach allow to migrate (if necessary) metadata extraction to mapping progressively
                # and transparently for user
                recursive_update(dtree.attrs, attrs)
            else:
                # load sentineltoolbox only if required
                from sentineltoolbox import eopf_interface

                logger = EOLogging().get_logger("eopf.store.sentineltoolbox")
                logger.info(f"Using sentineltoolbox to load {url}")
                dtree = eopf_interface.convert_safe_to_datatree(url, product_type=product_type, attrs=attrs, name=name)

            return EOProduct.from_datatree(dtree)
