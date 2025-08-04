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
from typing import Any, Callable, Optional, Type

from eopf.common.file_utils import AnyPath
from eopf.exceptions.errors import EOStoreFactoryNoRegisteredStoreError
from eopf.store import EOProductStore


class EOStoreFactory:
    product_formats: dict[str, Type[EOProductStore]] = dict()

    def __new__(cls, *args: Any, **kwargs: Any) -> None:
        raise TypeError("EOStoreFactory can not be instantiated : static class !!")

    @classmethod
    def register_store(cls, product_format: str) -> Callable[[Type[EOProductStore]], Type[EOProductStore]]:
        def inner_register(wrapped: Type[EOProductStore]) -> Type[EOProductStore]:
            cls.product_formats[product_format] = wrapped
            return wrapped

        return inner_register

    @classmethod
    def get_product_store_by_file(
        cls,
        file_path: AnyPath,
        storage_options: Optional[dict[str, Any]] = None,
    ) -> Type[EOProductStore]:
        """
        Get the store able to read this file, file need to exist
        Parameters
        ----------
        file_path

        Returns
        -------

        """
        for store_type in cls.product_formats.values():
            if store_type.guess_can_read(file_path):
                return store_type
        raise EOStoreFactoryNoRegisteredStoreError(f"No registered store compatible with : {file_path}")

    @classmethod
    def get_product_store_by_filename(cls, file_path: str) -> Type[EOProductStore]:
        """
        Get the store able to read this filename, this is a simple dummy test on the filename
        Parameters
        ----------
        file_path

        Returns
        -------

        """
        for store_type in cls.product_formats.values():
            if store_type.is_valid_url(file_path):
                return store_type
        raise EOStoreFactoryNoRegisteredStoreError(f"No registered store compatible with filename : {file_path}")

    @classmethod
    def get_product_store_by_format(cls, item_format: str) -> Type[EOProductStore]:
        if item_format in cls.product_formats.keys():
            return cls.product_formats[item_format]
        raise EOStoreFactoryNoRegisteredStoreError(f"No registered store with format : {item_format}")

    @classmethod
    def get_product_stores_available(cls) -> dict[str, Type[EOProductStore]]:
        out_dict = {}
        for mapping in cls.product_formats.keys():
            out_dict[f"{mapping}"] = cls.product_formats[mapping]
        return out_dict

    @classmethod
    def check_product_store_available(cls, item_format: str) -> bool:
        return item_format in cls.product_formats.keys()
