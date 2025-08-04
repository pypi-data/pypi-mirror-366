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
import ast
import collections.abc
import importlib
import json
import re
from abc import ABC, abstractmethod
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

import numpy as np
import xarray as xr
from jinja2 import Template
from xarray import DataTree

from eopf.common import file_utils
from eopf.config.config import EOConfiguration
from eopf.exceptions import MissingConfigurationParameterError
from eopf.exceptions.errors import MissingArgumentError, TemplateMissingError
from eopf.logging import EOLogging

EOConfiguration().register_requested_parameter(
    "template_folder",
    "eopf/product/templates/jinja_template",
    description="Path to the template folder",
    param_is_optional=True,
)


class EOPFAbstractTemplateFactory(ABC):

    @abstractmethod
    def get_template(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def register_template(self, *args: Any, **kwargs: Any) -> Any:
        pass


class EOPFTemplateFactory(EOPFAbstractTemplateFactory):
    FILENAME_RECO = "filename_pattern"
    TYPE_RECO = "product_type"
    RECO = "recognition"

    def __init__(self, default_templates: bool = True) -> None:
        self.LOGGER = EOLogging().get_logger("eopf.template_factory")
        self.template_set: set[str] = set()
        if default_templates:
            self._load_default_template()

    def _load_default_template(self) -> None:
        """

        :return:
        """
        try:
            path_directory = Path(EOConfiguration().template_folder)
            for template_path in path_directory.glob("*.jinja"):
                self._register_template_internal(str(template_path))
        except MissingConfigurationParameterError:
            # template has not been provided in configuration
            pass
        for resource in importlib.metadata.entry_points(group="eopf.store.template_folder"):
            resources_path_dir = importlib.resources.files(resource.value)
            for template_file in resources_path_dir.iterdir():
                if template_file.is_file():
                    with importlib.resources.as_file(template_file) as file:
                        if file.suffix == ".jinja":
                            self._register_template_internal(str(file))

    def get_template(
        self,
        file_path: Optional[str] = None,
        product_type: Optional[str] = None,
        context_overcharge: Dict[str, Any] = {},
    ) -> Optional[Dict[str, Any]]:
        """
        :param file_path: file path if provided uses regex pattern matching to get the template
        :param product_type: if no path provided will try with the product type
        :return:
        the template

        :exception:
        MissingArgumentError if no file_name or product type provided
        TemplateMissingError if not template is found
        """
        if product_type:
            recognised = product_type
            reco = self.TYPE_RECO
        elif file_path:
            recognised = file_path
            reco = self.FILENAME_RECO
        else:
            raise MissingArgumentError("Must provide either file_path or product_type.")

        for json_template_path in self.template_set:
            json_template_data = EOPFTemplateFactory.load_jinja_template(json_template_path)
            if self.guess_can_read(json_template_data, recognised, reco):
                if len(context_overcharge) > 0:
                    json_template_data = EOPFTemplateFactory.load_jinja_template(json_template_path, context_overcharge)
                self.LOGGER.debug(f"Found {json_template_path} for file {file_path} and product type {product_type}")
                return json_template_data

        raise TemplateMissingError(f"No template was found for product: {file_path} and product_type {product_type}")

    @staticmethod
    def process_dict_root_attrs(d: Dict[str, Any]) -> Dict[str, Any] | None:
        """
        Process a dictionary by handling 'required', 'value', and 'dtype' attributes.

        Parameters
        ----------
        d : Dict[str, Any]
            The dictionary to process.

        Returns
        -------
        Dict[str, Any] | None
            Processed dictionary or None if the 'required' attribute is False.
        """
        if isinstance(d, dict):
            # Check if the dict has the required structure
            if "required" in d and "value" in d and "dtype" in d:
                # If 'required' is True, replace the dict with the 'value'
                if d["required"]:
                    return d["value"]
                else:
                    return None
            # If the dict does not match the specific structure, recurse into its values
            else:
                # Recurse into its values
                new_dict = {}
                for k, v in d.items():
                    processed_value = EOPFTemplateFactory.process_dict_root_attrs(v)
                    if processed_value is not None:
                        new_dict[k] = processed_value
                return new_dict
        elif isinstance(d, list):
            # If we encounter a list, apply the function to each element
            return [
                item for item in (EOPFTemplateFactory.process_dict_root_attrs(item) for item in d) if item is not None
            ]
        else:
            # If the value is neither a dict nor a list, return it as is
            return d

    @staticmethod
    def update_dict_recursively(
        original_dict: Dict[str, Any],
        dict_used_to_update: Mapping[Any, Any],
    ) -> Dict[str, Any]:
        """
        Recursively update a dictionary with another dictionary's values.

        Parameters
        ----------
        original_dict : dict
            The original dictionary to update.
        dict_used_to_update : dict
            The dictionary with updates.

        Returns
        -------
        dict
            The updated dictionary.
        """
        for k, v in dict_used_to_update.items():
            if isinstance(v, collections.abc.Mapping):
                original_dict[k] = EOPFTemplateFactory.update_dict_recursively(original_dict.get(k, {}), v)
            else:
                original_dict[k] = v
        return original_dict

    @staticmethod
    def load_jinja_template(jinja_template_path: str, context_overcharge: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Load and render a Jinja template with a given context, then process the root attributes.

        Parameters
        ----------
        jinja_template_path : str
            The path to the Jinja template file.
        context_overcharge : dict, optional
            Additional context to merge with the template's context.

        Returns
        -------
        Dict[str, Any]
            The rendered template as a dictionary.
        """
        with open(jinja_template_path, "r") as fd:
            template = Template(fd.read())

        context = EOPFTemplateFactory.get_context_template(jinja_template_path)
        context = EOPFTemplateFactory.update_dict_recursively(context, context_overcharge)
        rendered = template.render(context)
        rendered_json = json.loads(rendered)
        for attr_dictionary in ["stac_discovery", "other_metadata"]:
            rendered_json["data"]["/"]["attrs"][attr_dictionary] = EOPFTemplateFactory.process_dict_root_attrs(
                rendered_json["data"]["/"]["attrs"][attr_dictionary],
            )
        return rendered_json

    @staticmethod
    def get_context_template(jinja_template_path: str) -> Dict[str, Any]:
        """
        Extract the context dictionary from a Jinja template file.

        Parameters
        ----------
        jinja_template_path : str
            The path to the Jinja template file.

        Returns
        -------
        Dict[str, Any]
            The context dictionary extracted from the template.
        """
        lines = []
        with open(jinja_template_path, "r") as file:
            lines = file.readlines()

        # Detect the "context" line and its indentation
        context_start_line = 0
        context_indent = 0
        for i, line in enumerate(lines):
            if '"context": {' in line:
                context_start_line = i
                context_indent = len(line) - len(line.lstrip())
                break

        # Find the closing bracket with the same indentation
        context_end_line = 0
        for i in range(context_start_line + 1, len(lines)):
            line = lines[i]
            current_indent = len(line) - len(line.lstrip())
            if current_indent == context_indent and "}" in line:
                context_end_line = i
                break

        # Extract the context part
        context_part = lines[context_start_line : context_end_line + 1]
        context_str = "".join(context_part).rstrip(",\n")  # Remove trailing comma and newline

        # Load the extracted part as a dictionary
        context_dict = json.loads(f"{{{context_str}}}")
        return context_dict

    @staticmethod
    def guess_can_read(json_template_data: Dict[str, Any], recognised: str, recogniton_key: str) -> bool:
        """
        Determine if a given string matches a recognition pattern in the template data.

        Parameters
        ----------
        json_template_data : Dict[str, Any]
            The JSON template data containing recognition patterns.
        recognised : str
            The string to check against the recognition pattern.
        recognition_key : str
            The key in the template data where the recognition pattern is stored.

        Returns
        -------
        bool
            True if the string matches the recognition pattern, False otherwise.
        """
        pattern = json_template_data.get("recognition", {}).get(recogniton_key)
        if pattern:
            return re.match(pattern, recognised) is not None
        return False

    def _register_template_internal(self, store_class: str) -> None:
        """
        Internal placeholder
        :param store_class:
        :return:
        """
        self.template_set.add(store_class)

    def register_template(self, store_class: str) -> None:
        """
        Can be call by user to add custom templates other then the defaults
        :param store_class: A path to a json file
        :return:
        """
        self._register_template_internal(store_class)
        # In case someone register from outside
        self._verify_templates()

    def _verify_templates(self) -> None:
        """
        Verify the integrity of loaded templates
        :return:
        """
        # Verify that we don't have two time the same product type
        product_types_availables = []
        for json_template_path in self.template_set:
            json_template_data = file_utils.load_json_file(json_template_path)
            product_type = json_template_data.get("recognition", {}).get(self.TYPE_RECO)
            if product_type in product_types_availables:
                self.LOGGER.warning(
                    f"Found multiple templates for product type {product_type} for example in {json_template_path}",
                )
            else:
                product_types_availables.append(product_type)

    def create_from_tempate(self, data_variables: Dict[str, Any]) -> DataTree:
        """
        Builds a DataTree object from a dictionary of data variables.

        Args:
            data_variables (Dict[str, Any]): Dictionary with data variables and attributes.

        Returns:
            DataTree: DataTree object containing the dataset.
        """
        # Initialize the root DataTree node
        root_attrs = data_variables["data"]["/"]["attrs"]

        root: DataTree = DataTree(name="root")
        root.attrs = root_attrs

        # Function to create DataTree nodes recursively
        def create_tree(parent: DataTree, path: str, content: Dict[str, Any]) -> None:
            parts = path.strip("/").split("/")
            for i, part in enumerate(parts):
                # Check if the part already exists as a child
                existing_child = next((child for value, child in parent.children.items() if child.name == part), None)
                if existing_child:
                    parent = existing_child
                else:
                    # If this is the last part, add the data
                    if i == len(parts) - 1:
                        attrs = content.get("attrs", {})
                        data_vars = content.get("data_vars", {})
                        coords = content.get("coords", {})

                        # Create datasets for coords and data_vars
                        coord_data = {}
                        for coord_name, coord_info in coords.items():
                            dtype = np.dtype(coord_info["attrs"]["dtype"])
                            coord_data[coord_name] = xr.DataArray(
                                data=EOPFTemplateFactory.create_nd_array(coord_info["dims"].values(), dtype),
                                dims=coord_info["dims"].keys(),
                                attrs=coord_info["attrs"],
                            )

                        data_var_data = {}
                        for var_name, var_info in data_vars.items():
                            dtype = np.dtype(var_info["attrs"]["dtype"])
                            data_var_data[var_name] = xr.DataArray(
                                data=EOPFTemplateFactory.create_nd_array(var_info["dims"].values(), dtype),
                                dims=var_info["dims"].keys(),
                                attrs=var_info["attrs"],
                            )

                        # Combine coords and data_vars into a dataset
                        dataset = xr.Dataset(data_vars=data_var_data, coords=coord_data, attrs=attrs)

                        # Add the dataset to the current node
                        DataTree(name=part, dataset=dataset)
                    else:
                        # Create a new child node if it doesn't exist
                        new_child: DataTree = DataTree(name=part)
                        parent = new_child

        # Start the recursive creation of the tree
        for path, content in data_variables["data"].items():
            if path != "/":
                create_tree(root, path, content)

        return root

    @staticmethod
    def get_attrs_by_short_name(template: Dict[str, Any], short_name: str) -> Dict[str, Any]:
        """
        Retrieve attributes by the short name from the template.

        Parameters
        ----------
        template : Dict[str, Any]
            The template containing the data structure.
        short_name : str
            The short name to search for.

        Returns
        -------
        Dict[str, Any]
            The attributes dictionary corresponding to the given short name.
            Returns an empty dictionary if no match is found.
        """
        for group, group_data in template["data"].items():
            if group != "/":
                for var, var_data in group_data["data_vars"].items():
                    if var_data["attrs"]["short_name"] == short_name:
                        return var_data["attrs"]
        return {}

    def create_nd_array(shape: List[Union[str, ast.AST]], dtype: np.dtype[Any]) -> np.ndarray[Any, Any]:
        """
        Create an n-dimensional array with the specified shape and data type.

        Parameters
        ----------
        shape : list of str or ast.AST
            The shape of the array as a list of strings. Each string is evaluated to determine the dimension size.
        dtype : np.dtype
            The data type of the array.

        Returns
        -------
        np.ndarray
            The created n-dimensional array.
        """
        # Evaluate each element in the shape list to an integer
        evaluated_shape = [
            int(ast.literal_eval(dim)) if isinstance(dim, str) else int(cast(ast.Constant, dim).value) for dim in shape
        ]

        # Convert all elements to integers if they are not already
        shape_tuple = tuple(int(dim) for dim in evaluated_shape)

        # Create an array with the specified shape
        array = np.full(shape_tuple, np.nan, dtype=dtype)
        return array
