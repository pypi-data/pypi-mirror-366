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
from typing import Callable, Optional, Type

from eopf.accessor import EOAccessor
from eopf.exceptions import AccessorNotDefinedError
from eopf.logging.log import EOLogging


class EOAccessorFactory:
    accessor_ids: dict[str, Type[EOAccessor]] = dict()
    accessor_types: set[Type[EOAccessor]] = set()

    @classmethod
    def register_accessor(cls, *args: str) -> Callable[[Type[EOAccessor]], Type[EOAccessor]]:
        def inner_register(wrapped: Type[EOAccessor]) -> Type[EOAccessor]:
            cls.accessor_types.add(wrapped)
            for mapping in args:
                cls.accessor_ids[mapping] = wrapped
            return wrapped

        return inner_register

    @classmethod
    def get_accessor_class(
        cls,
        file_path: str,
        accessor_id: Optional[str] = None,
    ) -> Type[EOAccessor]:
        if accessor_id is not None:
            if accessor_id in cls.accessor_ids:
                return cls.accessor_ids[accessor_id]
            raise AccessorNotDefinedError(f"No registered accessor with format : {accessor_id}")
        for accessor_type in cls.accessor_types:
            if accessor_type.guess_can_read(file_path):
                return accessor_type
        raise AccessorNotDefinedError(f"No registered accessor compatible with : {file_path}")

    @classmethod
    def list_accessors(cls) -> dict[str, str]:
        out_dict = {}
        logger = EOLogging().get_logger(name="eopf.accessor.factory")
        for mapping in cls.accessor_ids.keys():
            logger.info(f"{mapping}:{cls.accessor_ids[mapping]}")
            out_dict[f"{mapping}"] = f"{cls.accessor_ids[mapping]}"
        for accessor in cls.accessor_types:
            logger.info(f"{accessor}")
        return out_dict
