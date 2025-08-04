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
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Optional, Type, TypeAlias, Union

from eopf.common.constants import EOPF_CPM_PATH
from eopf.common.file_utils import AnyPath, load_json_file
from eopf.config.config import EOConfiguration
from eopf.exceptions.errors import (
    MappingDefinitionError,
    MappingMissingError,
    MappingRegistrationError,
    MissingArgumentError,
    RecognitionFunctionNotDefinedError,
)
from eopf.logging import EOLogging

FILENAME_RECO = "filename_pattern"
FUNCTION_RECO = "function_uid"
PRODUCT_TYPE_REGOCNITION = "product_type"
VERSION_RECOGNITION = "processing_version"
MAPPING_RECOGNITION_SECTION = "recognition"
MAPPING_FILE_PATTERN = "*.json"
MappingContentType: TypeAlias = dict[str, Any]

EOConfiguration().register_requested_parameter(
    name="mapping__folder",
    default_value="store/mapping/",
    param_is_optional=False,
    description="path to the folder where mappings are stored",
)


@dataclass()
class MapDescription:
    """Class to define the description of a mapping"""

    path: AnyPath
    product_type: str
    processing_version: str

    def __init__(self, path: AnyPath, product_type: str, processing_version: str):
        self.path = path
        self.product_type = product_type
        self.processing_version = processing_version

    def __eq__(self, other: Any) -> bool:
        return other and self.path == other.path and self.processing_version == other.processing_version

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.product_type, self.processing_version))


class EOProductRecognition(ABC):

    @abstractmethod
    def guess_can_read(self, product_path: AnyPath) -> bool:
        """
        Function that should contain the code for a mapping to recognize a given input product.
        """


class EOPFAbstractProductRecognitionFactory(ABC):
    @abstractmethod
    def get_recognition_function(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def register_recognition_function(self, *args: Any, **kwargs: Any) -> Any:
        pass


class EOPFProductRecognitionFactory(EOPFAbstractProductRecognitionFactory):
    function_uids: dict[str, Type[EOProductRecognition]] = dict()

    @classmethod
    def register_recognition_function(
        cls,
        *args: str,
    ) -> Callable[[Type[EOProductRecognition]], Type[EOProductRecognition]]:
        def inner_register(wrapped: Type[EOProductRecognition]) -> Type[EOProductRecognition]:
            for mapping in args:
                cls.function_uids[mapping] = wrapped
            return wrapped

        return inner_register

    @classmethod
    def get_recognition_function(  # type: ignore
        cls,
        function_uid: Optional[str] = None,
    ) -> Type[EOProductRecognition]:
        if function_uid is not None:
            if function_uid in cls.function_uids:
                return cls.function_uids[function_uid]
            raise RecognitionFunctionNotDefinedError(
                f"Recognition function with uid : {function_uid} is not registered in the RecognitionFactory",
            )


@EOPFProductRecognitionFactory.register_recognition_function("regexp_recognition")
class EORegexpProductRecognition(EOProductRecognition):
    """
    Example of a class with a product recognition function
    """

    def __init__(self) -> None:
        pass

    def guess_can_read(self, product_path: AnyPath) -> bool:
        """
        Example function that checks if the product name matches a filename pattern
        """
        filename_pattern = "S3._OL_1_ERR.*SEN3|S03OLCERR.*"
        product_name = product_path.path.split("/")[-1]
        return re.match(filename_pattern, product_name) is not None


@EOPFProductRecognitionFactory.register_recognition_function("rec_S02MSIL1C_PSD15")
class EOS02MSIL1CPSD15Recognition(EOProductRecognition):
    """
    Product recognition function for S02MSIL1C PSD15
    """

    def __init__(self) -> None:
        pass

    def guess_can_read(self, product_path: AnyPath) -> bool:
        """
        Recognize L2A as defined by PSD 15
        """
        # the recognition is done based on the namespaces in MTD_MSIL2A.xml
        mtd_msil1c_path = product_path / "MTD_MSIL1C.xml"
        if mtd_msil1c_path.exists():
            from lxml import etree

            with mtd_msil1c_path.open() as xml_fobj:
                xml_str = xml_fobj.read()

            tree = etree.fromstring(xml_str)
            if "psd-15" in tree.tag:
                return True
            else:
                return False
        else:
            raise KeyError(f"Can not recognise product {product_path}")


@EOPFProductRecognitionFactory.register_recognition_function("rec_S02MSIL1C_PSD14")
class EOS02MSIL1CPSD14Recognition(EOProductRecognition):
    """
    Product recognition function for S02MSIL1C PSD14
    """

    def guess_can_read(self, product_path: AnyPath) -> bool:
        """
        Recognize L2A as defined by PSD 14
        """
        # the recognition is done based on the namespaces in MTD_MSIL2A.xml
        mtd_msil1c_path = product_path / "MTD_MSIL1C.xml"
        if mtd_msil1c_path.exists():
            from lxml import etree

            with mtd_msil1c_path.open() as xml_fobj:
                xml_str = xml_fobj.read()

            tree = etree.fromstring(xml_str)
            if "psd-14" in tree.tag:
                return True
            else:
                return False
        else:
            raise KeyError(f"Can not recognise product {product_path}")


@EOPFProductRecognitionFactory.register_recognition_function("rec_S02MSIL2A_PSD14")
class EOS02MSIL2APSD14Recognition(EOProductRecognition):
    """
    Example of a class with a product recognition function
    """

    def guess_can_read(self, product_path: AnyPath) -> bool:
        """
        Recognize L2A as defined by PSD 14
        """
        # the recognition is done based on the namespaces in MTD_MSIL2A.xml
        mtd_msil2a_path = product_path / "MTD_MSIL2A.xml"
        if mtd_msil2a_path.exists():
            from lxml import etree

            with mtd_msil2a_path.open() as xml_fobj:
                xml_str = xml_fobj.read()

            tree = etree.fromstring(xml_str)
            if "psd-14" in tree.tag:
                return True
            else:
                return False
        else:
            raise KeyError(f"Can not recognise product {product_path}")


@EOPFProductRecognitionFactory.register_recognition_function("rec_S02MSIL2A_PSD15")
class EOS02MSIL2APSD15Recognition(EOProductRecognition):
    """
    Example of a class with a product recognition function
    """

    def __init__(self) -> None:
        pass

    def guess_can_read(self, product_path: AnyPath) -> bool:
        """
        Recognize L2A as defined by PSD 15
        """
        # the recognition is done based on the namespaces in MTD_MSIL2A.xml
        mtd_msil2a_path = product_path / "MTD_MSIL2A.xml"
        if mtd_msil2a_path.exists():
            from lxml import etree

            with mtd_msil2a_path.open() as xml_fobj:
                xml_str = xml_fobj.read()

            tree = etree.fromstring(xml_str)
            if "psd-15" in tree.tag:
                return True
            else:
                return False
        else:
            raise KeyError(f"Can not recognise product {product_path}")


class EOPFAbstractMappingFactory(ABC):
    @abstractmethod
    def get_mapping(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def register_mapping(self, *args: Any, **kwargs: Any) -> Any:
        pass


class EOPFMappingFactory(EOPFAbstractMappingFactory):
    """
    Class allowing the matching of legacy products with mappings
    """

    # Initialize the product recognition factory
    my_pr_factory = EOPFProductRecognitionFactory()

    def __init__(self, mapping_path: Optional[Union[AnyPath, str]] = "default", **kwargs: Any) -> None:
        """
        Initialization of mapping set from a folder

        Parameters
        ----------
        mapping_path : Optional[Union[AnyPath, str]]
            path to the mapping folder/file
        kwargs: Any
            kwargs related to AnyPath

        """
        self._logger = EOLogging().get_logger("eopf.mapping_factory")
        self.mapping_set: set[MapDescription] = set()
        if mapping_path == "default":
            # use the default mappings
            dir_path = EOPF_CPM_PATH / EOConfiguration().get("mapping__folder")
            self.register_mapping(dir_path)
        elif mapping_path is not None:
            # use mappings under a dir provided by user
            path = AnyPath.cast(mapping_path, kwargs=kwargs)
            self.register_mapping(path)
        else:
            # allow the user to have an empty mapping_set
            pass

    def _register_dir(self, mapping_dir: AnyPath) -> None:
        """
        Register all mappings from a directory given by mapping_dir parameter

        Parameters
        ----------
        mapping_dir : AnyPath
            path to the mapping folder

        Raises
        ----------
        FileNotFoundError
        MappingMissingError
        MappingRegistrationError
        """
        if not mapping_dir.isdir():
            raise FileNotFoundError(f"Given mapping_dir is not a directory: {str(mapping_dir)}")
        try:
            map_paths = mapping_dir.glob(MAPPING_FILE_PATTERN)
            if len(map_paths) == 0:
                raise MappingRegistrationError(
                    f"No file inside the mapping_dir {str(mapping_dir)} "
                    f"match the required mapping pattern: {MAPPING_FILE_PATTERN}",
                )

            for map_path in map_paths:
                self._register_file(map_path)
        except Exception as err:
            raise MappingRegistrationError(f"{err}")

    def _register_file(self, map_path: AnyPath) -> None:
        """
        Register a mapping given at location given by map_path

        Parameters
        ----------
        map_path : AnyPath
            path to the mapping

        Raises
        ----------
        FileNotFoundError
        MappingRegistrationError
        MappingDefinitionError
        """
        if not map_path.isfile():
            raise FileNotFoundError(f"Given map_path is not a file: {str(map_path)}")
        try:
            json_data = load_json_file(map_path)
            if MAPPING_RECOGNITION_SECTION not in json_data:
                raise MappingDefinitionError(
                    f"Map at: {str(map_path)}; does not have the mandatory recognition section",
                )
            file_name_pattern_present = FILENAME_RECO in json_data[MAPPING_RECOGNITION_SECTION]
            recognition_function_present = FUNCTION_RECO in json_data[MAPPING_RECOGNITION_SECTION]
            if not file_name_pattern_present and not recognition_function_present:
                raise MappingDefinitionError(
                    f"Map at: {str(map_path)}; doest not have any product recognition method specified",
                )

            if PRODUCT_TYPE_REGOCNITION not in json_data[MAPPING_RECOGNITION_SECTION]:
                raise MappingDefinitionError(
                    f"Map at: {str(map_path)}; doest not have any product_type defined",
                )

            if VERSION_RECOGNITION not in json_data[MAPPING_RECOGNITION_SECTION]:
                raise MappingDefinitionError(
                    f"Map at: {str(map_path)}; does not have any processing_version defined",
                )

            map_description = MapDescription(
                path=map_path,
                product_type=json_data[MAPPING_RECOGNITION_SECTION][PRODUCT_TYPE_REGOCNITION],
                processing_version=json_data[MAPPING_RECOGNITION_SECTION][VERSION_RECOGNITION],
            )
            self.mapping_set.add(map_description)
        except Exception as err:
            raise MappingRegistrationError(f"Can not register map at {str(map_path)} due to: {err}")

    def get_mapping(
        self,
        product_path: Optional[str | AnyPath] = None,
        product_type: Optional[str] = None,
        processing_version: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[MappingContentType]:
        """
        Get the mapping contents associated with a product at product_path

        Parameters
        ----------
        product_path : str | AnyPath
            path to the product
        kwargs: Any
            kwargs relative to AnyPath

        Raises
        ----------
        MappingMissingError

        Returns
        ----------
        mapping contents Optional[MappingContentType]
        """
        if product_path is not None:
            product_path = AnyPath.cast(product_path, kwargs=kwargs)
        for mapping_description in self.mapping_set:
            if product_path is not None:
                mapping_content = load_json_file(mapping_description.path)
                if self.guess_can_read(mapping_content, product_path):
                    self._logger.debug(f"Found {mapping_description.path} for product {product_path}")
                    return mapping_content
            elif (product_type is not None) and (processing_version is not None):
                if (product_type == mapping_description.product_type) and (
                    processing_version == mapping_description.processing_version
                ):
                    mapping_content = load_json_file(mapping_description.path)
                    self._logger.debug(
                        f"Found {mapping_description.path} for product_type {product_type}"
                        f" with processing_version {processing_version}",
                    )
                    return mapping_content
            else:
                raise MissingArgumentError(
                    "One must provider the product_path or the product_type and processing_version",
                )

        raise MappingMissingError(f"No mapping was found for product: {product_path}")

    def guess_can_read(
        self,
        mapping_content: MappingContentType,
        product_path: str | AnyPath,
        **kwargs: Any,
    ) -> bool:
        """
        Determine if a product given at product_path matches the current map contents given as mapping_content

        Parameters
        ----------
        mapping_content: MappingContentType
            the contents of the mapping
        product_path : str | AnyPath
            path to the product
        kwargs: Any
            kwargs relative to AnyPath

        Returns
        ----------
        bool
        """
        product_path = AnyPath.cast(product_path, kwargs=kwargs)
        try:
            if FILENAME_RECO in mapping_content[MAPPING_RECOGNITION_SECTION]:
                filename_pattern = mapping_content[MAPPING_RECOGNITION_SECTION][FILENAME_RECO]
                return re.match(filename_pattern, product_path.basename) is not None
            elif FUNCTION_RECO in mapping_content[MAPPING_RECOGNITION_SECTION]:
                function_uid = mapping_content[MAPPING_RECOGNITION_SECTION][FUNCTION_RECO]
                recognition_cls = self.my_pr_factory.get_recognition_function(function_uid)
                return recognition_cls().guess_can_read(product_path)
            else:
                return False
        except Exception:
            return False

    def register_mapping(self, path: str | AnyPath, **kwargs: Any) -> None:
        """
        Method to register new mappings

        Parameters
        ----------
        path : str | AnyPath
            path to the mappings
        kwargs: Any
            kwargs relative to AnyPath
        """
        path = AnyPath.cast(path, kwargs=kwargs)
        if path.isdir():
            self._register_dir(path)
        else:
            # should be a file
            self._register_file(path)
