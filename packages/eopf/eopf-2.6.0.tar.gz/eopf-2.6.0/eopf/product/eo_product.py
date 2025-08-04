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
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
    cast,
)
from warnings import warn

# TODO replace by something in compute or common utils
from deepdiff import DeepDiff
from xarray.core.datatree import DataTree

from eopf import EOConfiguration
from eopf.common.constants import (
    DEEP_DIFF_IGNORE_TYPE_IN_GROUPS,
    EOPF_CATEGORY_ATTR,
    EOPF_CPM_PATH,
    EOPRODUCT_CATEGORY,
    ROOT_PATH_DATATREE,
    SHORT_NAME,
)
from eopf.exceptions import InvalidProductError
from eopf.exceptions.errors import EOPathError
from eopf.exceptions.warnings import EOPFDeprecated, NoMappingFile
from eopf.logging import EOLogging
from eopf.product.conveniences import get_default_file_name_no_extension
from eopf.product.eo_group import EOGroup
from eopf.product.eo_variable import EOVariable
from eopf.product.rendering import renderer
from eopf.product.utils.eopath_utils import is_absolute_eo_path, product_relative_path
from eopf.store.mapping_manager import EOPFAbstractMappingManager, EOPFMappingManager

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_object import EOObject
    from eopf.product.eo_validation import ValidationMode

EOConfiguration().register_requested_parameter(
    "product__create_mask",
    False,
    description="Activate mask creation",
)


class EOProduct(EOGroup):
    """A EOProduct contains EOGroups (and through them, their EOVariables),
    linked to its EOProductStore (if existing).

    Read and write both dynamically or on demand to the EOProductStore.
    It can be used in a dictionary like manner with relative and absolute paths.
    It has personal attributes and both personal and inherited coordinates.

    Parameters
    ----------
    name: str
        name of this product
    storage_driver: Union[str, EOProductStore], optional
        a EOProductStore or a string to create to a EOZarrStore
    attrs: dict[str, Any], optional
        global attributes of this product

    See Also
    --------
    """

    MANDATORY_FIELD = ("measurements",)

    _TYPE_ATTR_STR = "product_type"

    @classmethod
    def init_product(cls, product_name: str, **kwargs: Any) -> "EOProduct":

        product = EOProduct(product_name, **kwargs)

        # TODO : open the product ?
        for group_name in product.MANDATORY_FIELD:
            product[group_name] = EOGroup(group_name)
        return product

    def __init__(
        self,
        name: str,
        attrs: Optional[MutableMapping[str, Any]] = None,
        product_type: Optional[str] = None,
        processing_version: Optional[str] = None,
        strict: bool = False,
        mapping_manager: Optional[EOPFAbstractMappingManager] = None,
        parent: Optional["EOObject"] = None,
        eo_path: Optional["str"] = None,
        short_names: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialise an EOProduct

        Parameters
        ----------
        name: str
        attrs: Optional[MutableMapping[str, Any]]
        product_type Optional[str]
        processing_version Optional[str]
        strict: bool
        mapping_manager: Optional[EOPFAbstractMappingManager]
        kwargs: Any
        """
        self._logger = EOLogging().get_logger("eopf.product.eo_product")
        # Internal short_names, should not be modified by other function than the dedicated setter function,
        # that's why it's a mapping proxy
        self.__short_names: Mapping[str, str] = MappingProxyType(dict())
        self.eo_path: Optional[str] = eo_path
        self._mapping_manager = mapping_manager if mapping_manager is not None else EOPFMappingManager()
        EOGroup.__init__(self, attrs=attrs, name=name, parent=parent)

        # set user given short_names
        if short_names is not None:
            self.short_names = MappingProxyType(short_names)

        # incoming attrs doesn't have the product:type tag
        if self.product_type is None and product_type is not None:
            self.product_type = product_type
        if self.processing_version is None and processing_version is not None:
            self.processing_version = processing_version
        self._strict = strict
        self._mission_specific: Optional[str] = None
        if "storage" in kwargs or "storage_driver" in kwargs:
            self._logger.warning("The EOProduct has no store attached since version 2.0.0")
            warn(
                "The EOProduct has no store attached since version 2.0.0",
                EOPFDeprecated,
            )

        self._declare_as_product()

    def __eq__(self, other: Any) -> bool:
        """
        Checks if this EOProduct instance is equal to another instance.

        Parameters:
        other (Any): The object to compare with this EOProduct instance.

        Returns:
        bool: True if the objects are equal, False otherwise.
        """
        # Check if the other object is an instance of EOProduct
        if not isinstance(other, EOProduct):
            return False

        # Compare EOProduct attributes
        if DeepDiff(
            self.attrs,
            other.attrs,
            ignore_order=True,
            ignore_type_in_groups=DEEP_DIFF_IGNORE_TYPE_IN_GROUPS,
            exclude_paths=[
                "root['stac_discovery']['id']",
                "root['other_metadata']['history']",
                "root['other_metadata']['processing_history']",
            ],
        ):  # True when DeepDiff returns not empty dict
            return False

        # Check if the EOProduct has the same EOGroup structure
        if set([key for key in self.keys()]) != set([key for key in other.keys()]):
            return False

        # Compare each EOGroup
        for group_key in self.keys():
            if self[group_key] != other[group_key]:
                return False

        return True

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __deepcopy__(self, memo: dict[int, Any]) -> "EOProduct":
        new_instance: EOProduct = EOProduct(
            self.name,
            copy.deepcopy(self.attrs),
            self.product_type if self.product_type is not None else "",
            self.processing_version if self.processing_version is not None else "",
            self._strict,
            self._mapping_manager,
        )
        self.copy_tree(new_instance)
        memo[id(self)] = new_instance
        new_instance.short_names = self.short_names
        return new_instance

    def __contains__(self, key: Any) -> bool:
        key = self.short_names.get(key, key)
        if is_absolute_eo_path(key):
            key = product_relative_path(self.path, key)
        return super().__contains__(key)

    def __delitem__(self, key: str) -> None:
        # Support short name to path conversion
        key = self.short_names.get(key, key)
        if key[0] == "/":
            self.__delitem__(key[1:])
        else:
            super().__delitem__(key)

    def __getitem__(self, key: str) -> "EOObject":
        # Support short name to path conversion
        key = self.short_names.get(key, key)
        return super().__getitem__(key)

    def __setitem__(self, key: str, value: "EOObject") -> None:
        # Support short name to path conversion
        key = self.short_names.get(key, key)
        super().__setitem__(key, value)

    def get_default_file_name_no_extension(self, mission_specific: Optional[str] = None) -> str:
        """
        get the default filename using the convention :
        - Take product:type or internal product_type (8 characters, see #97)
        - Add "_"
        - Take start_datetime as YYYYMMDDTHHMMSS
        - Add "_"
        - Take end_datetime and start_datetime and calculate the difference in seconds (between 0000 to 9999)
        - Add "_"
        - Take the last character of "platform"  (A or B)
        - Take sat:relative_orbit (between 000 and 999)
        - Add "_"
        - Take product:timeliness_category: if it is NRT or 24H or STC, add "T";  if it is NTC, add "S"
        - Generate CRC on 3 characters
        if mission specific provided :
        - Add "_"
        - Add <mission_specific>
        """
        if mission_specific is None and self.mission_specific is not None:
            mission_specific = self.mission_specific
        return get_default_file_name_no_extension(self.product_type, self.attrs, mission_specific=mission_specific)

    def is_valid(self, validation_mode: Optional["ValidationMode"] = None) -> bool:
        """Check if the product is a valid eopf product

        Returns
        -------
        bool

        See Also
        --------
        EOProduct.validate"""
        from eopf.product import eo_product_validation

        flag, anomalies = eo_product_validation.is_valid_product(self, validation_mode=validation_mode)
        return flag

    def validate(self, validation_mode: Optional["ValidationMode"] = None) -> None:
        """check if the product is a valid eopf product, raise an error if is not a valid one

        Raises
        ------
        InvalidProductError
            If the product not follow the harmonized common data model

        See Also
        --------
        EOProduct.is_valid
        """
        if not self.is_valid(validation_mode=validation_mode):
            raise InvalidProductError(f"Invalid product {self} with mode {str(validation_mode)}")

    # docstr-coverage: inherited
    @property
    def path(self) -> str:
        return "/"

    # docstr-coverage: inherited
    @property
    def product(self) -> "EOProduct":
        return self

    # docstr-coverage: inherited
    @property
    def relative_path(self) -> Iterable[str]:
        return []

    @property
    def product_type(self) -> Optional[str]:
        """
        Retrieve product_type, None if not set

        Returns
        -------
        from attribute ["stac_discovery"]["properties"]["product:type"]
        """
        try:
            return self.attrs["stac_discovery"]["properties"]["product:type"]
        except KeyError:
            return None

    @product_type.setter
    def product_type(self, intype: str) -> None:
        """
        Set product_type

        Parameters
        ----------
        inversion: str
        """
        self.attrs.setdefault("stac_discovery", {}).setdefault("properties", {})["product:type"] = intype

    @property
    def processing_version(self) -> Optional[str]:
        """
        Retrieve processing_version

        Returns
        -------
        from attribute ["stac_discovery"]["properties"]["processing:version"]
        """
        try:
            return self.attrs["stac_discovery"]["properties"]["processing:version"]
        except KeyError:
            return None

    @processing_version.setter
    def processing_version(self, inversion: str) -> None:
        """
        Set processing_version

        Parameters
        ----------
        inversion: str
        """
        self.attrs.setdefault("stac_discovery", {}).setdefault("properties", {})["processing:version"] = inversion

    def set_type_and_version(self, product_type: str, processing_version: str) -> None:
        """
        Set product_type and processing_version. Retrieve short_names and dump to the EOVariables

        Parameters
        ----------
        product_type: str
        processing_version: str

        """

        self.attrs.setdefault("stac_discovery", {}).setdefault("properties", {})["product:type"] = product_type
        self.attrs.setdefault("stac_discovery", {}).setdefault("properties", {})[
            "processing:version"
        ] = processing_version

        if len(self.short_names) == 0:
            # shortnames where never set -> generate the shortnames
            self.short_names = MappingProxyType(
                self._get_short_names_from_mappings(product_type=product_type, processing_version=processing_version),
            )

    @property
    def attrs(self) -> dict[str, Any]:
        self.update_short_names()
        return self._attrs

    @attrs.setter
    def attrs(self, new_attrs: dict[str, Any]) -> None:
        self._attrs = new_attrs
        self.update_short_names()

    @property
    def mission_specific(self) -> Optional[str]:
        return self._mission_specific

    @mission_specific.setter
    def mission_specific(self, amission_specific: str) -> None:
        self._mission_specific = amission_specific

    @property
    def short_names(self) -> Mapping[str, str]:
        """
        Get the shortnames if available for the product type else empty mapping

        MappingProxyType --> To modify this you have to use the setter method and can't modify it inplace

        Returns
        -------

        """
        self.update_short_names()
        return MappingProxyType(self.__short_names)

    @short_names.setter
    def short_names(self, short_names: Mapping[str, str]) -> None:
        """
        Set EOProduct short_names and dumps them in variables

        Parameters
        -------
        short_names:  dict[str, str]

        Returns
        -------
        """
        self.__short_names = short_names
        self._dump_short_names_to_variables()
        self._populate_asset_with_shortnames()

    def update_short_names(self) -> None:
        # update shortnames from variables
        updated = dict(self.__short_names)
        updated.update(EOProduct._get_short_names_from_variables(self))
        self.__short_names = MappingProxyType(updated)
        self._populate_asset_with_shortnames()

    def _get_short_names_from_mappings(self, product_type: str, processing_version: str) -> dict[str, str]:
        """
        Retrieve short_names from mapping based on product_type

        Parameters
        ----------
        product_type: str
        processing_version: str
            version of product_type

        Returns
        -------
        short names dictionary dict[str, str]
        """

        eop_short_names: dict[str, str] = dict()
        if product_type not in ["", " ", "\x00"]:

            mapping_short_names = self._mapping_manager.parse_shortnames(
                product_type=product_type,
                processing_version=processing_version,
            )
            if mapping_short_names is None:
                self._logger.warning(
                    NoMappingFile(
                        f"No mapping for product_type: {product_type} processing_version: {processing_version}",
                    ),
                )
                warn(
                    NoMappingFile(
                        f"No mapping for product_type: {product_type} processing_version: {processing_version}",
                    ),
                )
                return eop_short_names

            if self.eo_path is None or self.eo_path == "/":
                for short_name, abs_path in mapping_short_names:
                    eop_short_names[short_name] = abs_path
            else:
                eop_path = PurePosixPath(self.eo_path)
                for short_name, abs_path in mapping_short_names:
                    try:
                        rel_path = PurePosixPath(abs_path).relative_to(eop_path)
                        eop_short_names[short_name] = str(rel_path)
                    except ValueError:
                        pass

        return eop_short_names

    def _dump_short_names_to_variables(self) -> None:
        """
        Dump the shortnames directly to the corresponding variable attributes. Missing variables are
        simply ignored.
        """

        for key in self.short_names:
            eo_var = self.get(key)
            # TMP FIX: untill the update of short_names
            if eo_var is None:
                eo_var = self.get(key.strip("/"))
            if eo_var is not None:
                eo_var.attrs[SHORT_NAME] = key

    @staticmethod
    def _get_short_names_from_variables(group: EOGroup) -> dict[str, str]:
        short_names = dict()
        for _, var in group.variables:
            if SHORT_NAME in var.attrs:
                short_names[str(var.attrs[SHORT_NAME])] = var.path
        for _, sub_group in group.groups:
            short_names.update(EOProduct._get_short_names_from_variables(group=sub_group))
        return short_names

    def _clean_short_names_in_variables(self, group: EOGroup | None = None) -> None:
        """
        Remove any 'short_name' attribute in variables

        :param group: current group to clean, replaced by this EOProduct if None
        """
        cur_group = self if group is None else group
        for _, var in cur_group.variables:
            var.attrs.pop(SHORT_NAME, None)

        for _, sub_group in cur_group.groups:
            self._clean_short_names_in_variables(group=sub_group)

    def update_variables_short_names(self) -> None:
        """
        Update short names attribute in variables
        Simplest way is to remove everything and add them back
        """
        self._clean_short_names_in_variables()
        self._dump_short_names_to_variables()

    def _populate_asset_with_shortnames(self) -> None:
        asset_dic = self._attrs.setdefault("stac_discovery", {}).setdefault("assets", {})
        if not isinstance(asset_dic, dict):
            raise ValueError(f"Assets in STAC is a dict not a {type(asset_dic)}")
        short_names = self.__short_names
        # Shortname in asset but no longer available in product shortnames
        # Note that this will remove any external asset !!!
        # But this should not happen
        invalid_shortnames = []
        for asset_key, asset_value in asset_dic.items():
            if asset_key not in short_names.keys():
                invalid_shortnames.append(asset_key)
        for invalid in invalid_shortnames:
            asset_dic.pop(invalid)
        for shortname_key, shortname_value in short_names.items():
            asset_dic[shortname_key] = {"href": shortname_value, "title": shortname_key}

    def _declare_as_product(self) -> None:
        self._attrs.setdefault("other_metadata", dict()).setdefault(EOPF_CATEGORY_ATTR, EOPRODUCT_CATEGORY)

    # docstr-coverage: inherited
    def _add_local_variable(self, name: str = "", data: Any = None, new_eo: bool = True, **kwargs: Any) -> "EOVariable":
        if self._strict:
            raise InvalidProductError("Products can't directly store variables.")
        else:
            return super()._add_local_variable(name, data, **kwargs)

    def _init_similar(self) -> "EOProduct":
        attrs = {k: v for (k, v) in self.attrs.items() if k != "_ARRAY_DIMENSIONS"}
        return EOProduct(self.name, attrs=attrs)

    @property
    def is_root(self) -> "bool":
        """
        Is this object a root of the data tree ?
        """
        return True

    def _repr_html_(self, prettier: bool = True) -> str:
        """Returns the html representation of the current product displaying the tree.

        Parameters
        ----------
        prettier: str
            Flag for using SVG as label for each Product, Group, Variable, Attribute.
        """

        css_file = EOPF_CPM_PATH / "product/templates/static/css/style.css"

        with css_file.open(mode="r") as css:
            css_content = css.read()

        css_str = f"<style>{css_content}</style>\n"
        rendered_template = renderer("product.html", product=self, prettier=prettier)
        final_str = css_str + rendered_template

        return final_str

    def subset(
        self,
        region: tuple[int, int, int, int],
        reference: Optional[str] = "",
    ) -> "EOProduct":
        return cast(EOProduct, super().subset(region, reference))

    def to_datatree(self) -> DataTree:
        """
        Converts the current object into a DataTree.

        Returns
        -------
        DataTree
            The constructed DataTree object representing the current object.
        """
        dt: DataTree = DataTree(name=self.name)

        # Ensuring self.attrs is of type Dict[Hashable, Any]
        if not isinstance(self.attrs, dict):
            raise TypeError("self.attrs must be a dictionary")
        dt.attrs = {k: v for k, v in self.attrs.items()}  # Creating a new dictionary of type Dict[Hashable, Any]

        for obj in self.walk():
            if isinstance(obj, EOVariable) and obj.data is not None:
                dt[str(obj.path)] = obj.data
            else:
                dt[str(obj.path)] = DataTree(name=obj.name)

            if not isinstance(obj.attrs, dict):
                raise TypeError("obj.attrs must be a dictionary")
            dt[str(obj.path)].attrs.update(
                {k: v for k, v in obj.attrs.items()},
            )  # Ensuring obj.attrs is of type Dict[Hashable, Any]

        # temporary fix see issue 608
        for path in dt.to_dict():
            for data_var in dt[path].data_vars:
                xda = dt[path][str(data_var)]
                if "coordinates" in xda.attrs:
                    del xda.attrs["coordinates"]

        return dt

    @classmethod
    def from_datatree(cls, datatree: DataTree) -> "EOProduct":
        """
        Creates an instance of the class from a given DataTree.

        Parameters
        ----------
        datatree : DataTree
            The DataTree object from which to create the class instance.

        Returns
        -------
        cls
            An instance of the class representing the given DataTree.
        """
        attrs_with_str_keys: Dict[str, Any] = {
            str(k): v for k, v in datatree.attrs.items()
        }  # Convert the dictionary to have only string keys
        mutable_attrs: MutableMapping[str, Any] = attrs_with_str_keys  # Now cast it to MutableMapping[str, Any]

        eoproduct = cls(name=str(datatree.name), attrs=mutable_attrs)
        for obj in datatree.subtree:
            if obj.path == ROOT_PATH_DATATREE:
                continue
            try:
                eoproduct[obj.path]
            except (EOPathError, KeyError):
                eoproduct[obj.path] = EOGroup(Path(obj.path).name, attrs=obj.attrs)
            else:
                eoproduct[obj.path].attrs.update(obj.attrs)
            for var_name in obj.variables:
                if var_name not in obj.coords:
                    variable = obj[var_name]
                    eoproduct[obj.path][var_name] = EOVariable(name=var_name, data=variable)  # type: ignore
        return eoproduct
