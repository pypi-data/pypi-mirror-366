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
from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional

from eopf.accessor.abstract import EOAccessor
from eopf.accessor.netcdf_accessors import EONetCDFAccessor
from eopf.common.constants import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.common.json_utils import decode_all_attrs
from eopf.exceptions import StoreNotOpenError
from eopf.exceptions.errors import EOStoreProductAlreadyExistsError
from eopf.formatting.decorators import (
    formatable_method,
    reverse_formatable_method,
    unformatable_method,
)
from eopf.product import EOContainer, EOProduct
from eopf.store import EOProductStore
from eopf.store.abstract import StorageStatus
from eopf.store.store_factory import EOStoreFactory

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_object import EOObject

from eopf.logging import EOLogging


@EOStoreFactory.register_store("netcdf")
class EONetCDFStore(EOProductStore):
    """
    Store representation to access NetCDF format of the given URL.

    Parameters
    ----------
    url: str
        path url or the target store

    Attributes
    ----------
    url: str
        path url or the target store
    """

    URL_VALIDITY_DESCRIPTION = "filename with .nc or .nc.zip extension"
    PRODUCT_VALIDITY_DESCRIPTION = "File with .nc extension of file with .nc.zip extension"
    EXTENSION = ".nc"

    def load(self, name: str = "", **kwargs: Dict[str, Any]) -> EOProduct | EOContainer:
        """ "
        TBD
        """
        return EOProduct("")

    # docstr-coverage: inherited
    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        super().__init__(url=url, *args, **kwargs)
        # Define the whole module LOGGER, sub logger of eopf.store
        self.LOGGER = EOLogging().get_logger("eopf.store.netcdf")
        self._sub_accessor: Optional[EONetCDFAccessor] = None
        self._path_obj = None

    # docstr-coverage: inherited
    @unformatable_method()
    def __delitem__(self, key: str) -> None:
        del self.sub_accessor[key]

    # docstr-coverage: inherited
    @formatable_method()
    def __getitem__(self, key: str) -> "EOObject":
        item = self.sub_accessor[key]
        item.attrs.update(decode_all_attrs(item.attrs))
        return item

    # docstr-coverage: inherited
    @reverse_formatable_method()
    def __setitem__(self, key: str, value: "EOObject") -> None:
        self.sub_accessor[key] = value

    # docstr-coverage: inherited
    def __len__(self) -> int:
        return len(self.sub_accessor)

    # docstr-coverage: inherited
    def close(self, cancel_flush: bool = False) -> None:
        if self.status is StorageStatus.OPEN:
            self.sub_accessor.close()
            self._sub_accessor = None
        super().close(cancel_flush=cancel_flush)

    # docstr-coverage: inherited
    def open(self, mode: OpeningMode | str = OpeningMode.OPEN, **kwargs: Any) -> "EOProductStore":
        mode = OpeningMode.cast(mode)
        if mode == OpeningMode.CREATE and self.guess_can_read(self.url, **kwargs):
            raise EOStoreProductAlreadyExistsError(
                f"Product {self.url} already exists and open mode doesn't allow overwriting",
            )
        self._sub_accessor = EONetCDFAccessor(self.url)
        if self._sub_accessor is None:
            raise Exception(f"Unable to create netcdf accessor on {self.url}")
        self._sub_accessor.open(mode=mode, **kwargs)
        super().open(mode)
        return self

    # docstr-coverage: inherited
    @unformatable_method()
    def is_group(self, path: str) -> bool:
        return self.sub_accessor.is_group(path)

    # docstr-coverage: inherited
    @unformatable_method()
    def is_variable(self, path: str) -> bool:
        return self.sub_accessor.is_variable(path)

    def is_product(self, path: str) -> bool:
        return (self.url / (path + self.EXTENSION)).isdir()

    # docstr-coverage: inherited
    @unformatable_method()
    def iter(self, path: str) -> Iterator[str]:
        return self.sub_accessor.iter(path)

    @property
    def sub_accessor(self) -> EOAccessor:
        if self.status is StorageStatus.CLOSE or self._sub_accessor is None:
            raise StoreNotOpenError("Store must be open before access to it")
        return self._sub_accessor

    # docstr-coverage: inherited
    def write_attrs(self, group_path: str, attrs: MutableMapping[str, Any] = {}) -> None:
        return self.sub_accessor.write_attrs(group_path, attrs)

    # docstr-coverage: inherited
    @staticmethod
    def guess_can_read(file_path: str | AnyPath, **kwargs: Any) -> bool:
        tmp_path = AnyPath.cast(file_path, kwargs=kwargs)
        if tmp_path.suffixes is not None and ".nc" in tmp_path.suffixes and tmp_path.suffix in [".nc", ".zip"]:
            if tmp_path.suffix == ".zip":
                if not tmp_path.isdir():
                    return False
            else:
                if not tmp_path.isfile():
                    return False
        else:
            return False
        # No reason found not to be able to read it
        return True

    @staticmethod
    def is_valid_url(file_path: str | AnyPath, **kwargs: Any) -> bool:
        tmp_path = AnyPath.cast(file_path, **kwargs.get("storage_options", {}))
        return tmp_path.suffixes is not None and ".nc" in tmp_path.suffixes and tmp_path.suffix in [".nc", ".zip"]
