import os
import re
from logging import Logger
from typing import Any, Callable, Dict, List, Optional

import dask.array as da
import numpy as np
from pydantic import BaseModel, field_validator

from eopf import EOConfiguration, EOLogging
from eopf.common.constants import EOPF_CPM_PATH
from eopf.common.file_utils import AnyPath, load_json_file
from eopf.common.functions_utils import get_all_paths_in_dict, nested_dict_from_paths
from eopf.product.eo_group import EOGroup
from eopf.product.eo_product import EOProduct
from eopf.product.eo_validation import (
    MANDATORY_TOP_ATTR_CATEGORY,
    AnomalyDescriptor,
    AttributeModel,
    ModelValidationMode,
    ValidationMode,
    append_to_anomalies,
    check_stac_validity,
    validate_attrs_list,
    validate_attrs_schema,
)
from eopf.product.eo_variable import EOVariable

EOConfiguration().register_requested_parameter(
    name="model__folder",
    default_value=os.path.join(EOPF_CPM_PATH.path, "product", "models"),
    param_is_optional=True,
    description="path to the folder where pydantic models are stored",
)

# Definition of mandatory and optional elements
MANDATORY_GROUPS = ("measurements",)
OPTIONAL_GROUPS = ("quality", "conditions")

MANDATORY_VARIABLE_ATTRS = ("long_name", "short_name", "dtype")
OPTIONAL_VARIABLE_ATTRS = (
    "units",
    "standard_name",
    "flag_masks",
    "flag_values",
    "flag_meanings",
    "scale_factor",
    "add_offset",
    "valid_min",
    "valid_max",
    "fill_value",
    "coordinates",
    "dimensions",
)


# ------------------------------------ EOPRODUCT validation rules ------------------------------------

# ---------- Summary of the workflow for product validation

#   * Whatever the input product, we apply the following:
#     - A "generic validation" which checks that all mandatory
#       elements are present + some basic rules
#     (e.g. a group cannot be empty,...)
#     - A metadata validation (to validate STAC metadata + other metadata)


# ---------- Validation rules for EOGroup:

#   - An EOGroup cannot be empty (must contain at least one sub group or variable)
#   - An EOGroup cannot contain other elements than EOGroups, EOVariables and attributes
#   (this rule is already verified through the setitem method of the EOProduct)
#   - Mandatory groups: measurements
#   - Possible groups: quality and conditions
#   - It is possible to have two groups
#   - Group attributes can be empty

# ---------- Validation rules for EOVariables:

#   - No scalar variables (= no scalar with empty dimensions + no scalar with dimensions “one”)
#   - Variable attributes cannot be empty (mandatory variables required)
#   - Mandatory variable attributes: long_name, short_name
#   - Possible variable attributes: units, standard_name, flag_masks, flag_values, flag_meanings, scale_factor,
#     add_offset, valid_min,
#     valid_max, fill_value, coordinates, dimensions

# ---------- Validation for top-level attributes in an EOPRoduct

# * STAC metadata:
#   - Generic validation:
# 	    . Mandatory STAC extensions in stac_extensions list: eopf, stac base 1.1.0
#       . Verify list of extensions : if one is missing or not used in the properties
#       . Validate against extensions schemas listed
#   - If the schema is available in the CPM install it will use it else it will download it

# * Other metadata:
# 	- Generic validation: No particular restrictions
#   - Template validation: other metadata should respect the template


def is_valid_product(
    product: EOProduct,
    validation_mode: Optional[ValidationMode] = None,
) -> tuple[bool, List[AnomalyDescriptor]]:
    """
    Returns a boolean indicating the validity of the product
    And the list of anomalies

    Parameters
    ----------
        product (EOProduct): input EOProduct
        validation_mode (str): selected validation mode: possible values:
            - STRUCTURE : only verify structure
            - STAC : STAC attr validation
            - MODEL : validate against pydantic model
    Returns
    -------
        Boolean indicating whether a product is valid
        List of anomalies, empty if none found
    """
    logger = EOLogging().get_logger("eopf.product.validation")
    validation_mode = validation_mode if validation_mode is not None else ValidationMode.STRUCTURE

    anomalies: List[AnomalyDescriptor] = []
    checks_to_do: dict[ValidationMode, List[Callable[[Any, List[AnomalyDescriptor], Logger], None]]] = {
        ValidationMode.STRUCTURE: [check_eoproduct_validity],
        ValidationMode.STAC: [check_stac_validity],
        ValidationMode.MODEL: [check_product_model_validity],
        ValidationMode.NONE: [],
    }

    # try:
    for m in ValidationMode:
        if m in validation_mode:
            for check in checks_to_do[m]:
                check(product, anomalies, logger)
    return len(anomalies) == 0, anomalies


############################################
#   Structure validation part
############################################


def check_eoproduct_validity(
    product: EOProduct,
    out_anomalies: List[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """
    Check if the input product has a valid format.
    A generic EOProduct validation is applied for all products.
    What's more, if the product type is defined, a product validation based on the templates data structure
    is also applied.

    Parameters
    ----------
        product (EOProduct): input EOProduct
        validation_mode (str): selected validation mode: possible values
    """
    # ----------------- Generic checks
    # Check the mandatory and possible top-level groups
    if any(key not in product for key in MANDATORY_GROUPS):
        append_to_anomalies(
            out_anomalies,
            "STRUCTURE",
            f"Mandatory groups {MANDATORY_GROUPS} not present in the current product",
            logger,
        )
    if any(key not in OPTIONAL_GROUPS for key in [opt_key for opt_key in product if opt_key not in MANDATORY_GROUPS]):
        append_to_anomalies(
            out_anomalies,
            "STRUCTURE",
            f"Optional groups must be in the list: {OPTIONAL_GROUPS}",
            logger,
        )
    # Check mandatory attribute categories exist in the EOProduct
    if any(key not in product.attrs for key in MANDATORY_TOP_ATTR_CATEGORY):
        append_to_anomalies(
            out_anomalies,
            "STRUCTURE",
            f"Missing top-level attribute category from the mandatory list: {MANDATORY_TOP_ATTR_CATEGORY}",
            logger,
        )
    # Check that top-level groups are not empty
    for group_name, group in product.groups:
        if len(list(group)) == 0:
            append_to_anomalies(out_anomalies, "STRUCTURE", f"Group {group.path} cannot be empty", logger)
    # Generic check of the product structure
    for group in [group_data[1] for group_data in list(product.groups)]:
        check_group_validity(group, out_anomalies, logger)


def check_group_validity(group: EOGroup, out_anomalies: List[AnomalyDescriptor], logger: Optional[Logger]) -> None:
    """
    Check if the input group has a valid format. Only a generic validation is done
    (the structure and the rules are verified).
    Parameters
    ----------
        group (EOGroup): input EOGroup
    """
    eoproduct_elem_list = [group[0] for group in list(group.groups)] + [var[0] for var in list(group.variables)]

    for sub_group in [group_data[1] for group_data in list(group.groups)]:
        # Check that subgroups are not empty
        if len(list(sub_group)) == 0:
            delimiter = "/"
            append_to_anomalies(
                out_anomalies,
                "STRUCTURE",
                f"Group {delimiter.join(list(sub_group.relative_path) + [sub_group.name], )} cannot be empty",
                logger,
            )
    for elem_name in eoproduct_elem_list:
        # Check variable format validity
        if isinstance(group[elem_name], EOGroup):
            check_group_validity(group[elem_name], out_anomalies, logger)  # type: ignore

        # Check subgroup format validity
        elif isinstance(group[elem_name], EOVariable):
            check_variable_validity(group[elem_name], out_anomalies, logger)  # type: ignore


def check_variable_validity(
    variable: EOVariable,
    out_anomalies: List[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """
    Check if the input variable has a format matching the template

    Parameters
    ----------
        variable (EOVariable): input EOVariable
    """

    # ---------- Generic checks
    if variable.data.size == 0:
        append_to_anomalies(out_anomalies, "STRUCTURE", f"Data of EOVariable {variable.path} cannot be a empty", logger)
    if variable.data.size == 1:
        append_to_anomalies(
            out_anomalies,
            "STRUCTURE",
            f"Data of EOVariable {variable.path} cannot be a scalar",
            logger,
        )
    # Check variable attributes
    attr_list = list(variable.attrs.keys())

    # Check the mandatory and optional variable attributes
    for mandat_attr in MANDATORY_VARIABLE_ATTRS:
        if mandat_attr not in attr_list:
            append_to_anomalies(
                out_anomalies,
                "STRUCTURE",
                f"Mandatory attribute {mandat_attr} not present in {variable.name} variable attributes",
                logger,
            )
    # This needs to be simplified
    for attr in [opt_attr for opt_attr in attr_list if opt_attr not in MANDATORY_VARIABLE_ATTRS]:
        if attr not in OPTIONAL_VARIABLE_ATTRS:
            append_to_anomalies(
                out_anomalies,
                "STRUCTURE",
                f"""{variable.path}/{attr} not in optional variable attributes list:"""
                f"""{list(OPTIONAL_VARIABLE_ATTRS)}""",
                logger,
            )
    # Check if standard_name has unknown value
    if "standard_name" in attr_list and str(variable.attrs["standard_name"]).lower() == "unknown":
        append_to_anomalies(
            out_anomalies,
            "STRUCTURE",
            f"{variable.path}/standard_name has invalid 'unknown' value",
            logger,
        )


def check_coherent_dimension_product(
    product: EOProduct,
    out_anomalies: List[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    dim_info = {}

    def check_group(group: EOGroup) -> None:
        for variable_name, variable in group.variables:

            # Check repeated dims in a variable (should not happen in xarray)
            if len(set(variable.dims)) != len(variable.dims):
                append_to_anomalies(
                    out_anomalies,
                    "STRUCTURE",
                    f"Repeated dimension names in variable '{variable.name}' at node '{group.path}'",
                    logger,
                )

            for dim in variable.dims:
                length = variable.sizes[dim]
                coords = variable.coords.get(dim, None)

                if dim not in dim_info:
                    dim_info[dim] = {
                        "length": length,
                        "coords": coords,
                        "coord_attrs": coords.attrs if coords is not None else None,
                        "group_path": group.path,
                        "variable": variable_name,
                    }
                else:
                    ref = dim_info[dim]

                    if length != ref["length"]:
                        append_to_anomalies(
                            out_anomalies,
                            "STRUCTURE",
                            f"Inconsistent length for dimension '{dim}': "
                            f"expected {ref['length']} from {ref['group_path']}/{ref['variable']}, "
                            f"found {length} at node '{group.path}' variable '{variable_name}'",
                            logger,
                        )

                    # Check presence of coordinates
                    if (coords is None) != (ref["coords"] is None):
                        append_to_anomalies(
                            out_anomalies,
                            "STRUCTURE",
                            f"Inconsistent presence of coordinates for dimension '{dim}' "
                            f"at node '{group.path}' variable '{variable_name}' compared "
                            f"to {ref['group_path']}/{ref['variable']}",
                            logger,
                        )

                    # Check coordinate equality
                    if coords is not None and ref["coords"] is not None:
                        if not coords.equals(ref["coords"]):
                            append_to_anomalies(
                                out_anomalies,
                                "STRUCTURE",
                                f"Inconsistent coordinates for dimension '{dim}' "
                                f"at node '{group.path}' variable '{variable_name}' compared "
                                f"to {ref['group_path']}/{ref['variable']}",
                                logger,
                            )

        # Recurse into children
        for group_name, group_value in group.groups:
            check_group(group_value)

    check_group(product)


############################################
#   Product Contract validation part
############################################


class EOVariableModel(BaseModel):
    dtype: Optional[str] = None
    dims: Optional[List[str]] = None
    attrs: Optional[Dict[str, "AttributeModel"]] = None
    # Will retain a jsonschema
    attrs_schema: Optional[Dict[str, Any]] = None
    required: bool = True

    @field_validator("dtype", mode="before")
    def normalize_dtype(cls, v: Any) -> Optional[str]:
        return np.dtype(v).name if isinstance(v, (np.dtype, type)) else str(v) if v is not None else None


class EOProductModel(BaseModel):
    product_type_regex: str = ".*"
    variables: Optional[Dict[str, "EOVariableModel"]] = None
    attrs: Optional[Dict[str, "AttributeModel"]] = None
    # Will retain a jsonschema
    attrs_schema: Optional[Dict[str, Any]] = None
    required: bool = True


def validate_product_against_model(
    product: EOProduct,
    model: EOProductModel,
    mode: ModelValidationMode,
    out_anomalies: list[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    if model.product_type_regex != ".*":
        if product.product_type is None:
            append_to_anomalies(
                out_anomalies,
                "MODEL",
                "Input product type is None",
                logger,
            )
        elif not re.fullmatch(model.product_type_regex, product.product_type):
            append_to_anomalies(
                out_anomalies,
                "MODEL",
                f"Wrong product type detected on product {product.product_type} "
                f"doesn't match {model.product_type_regex} on product {product.name}",
                logger,
            )
    var_list = []
    for var in product.walk():
        if isinstance(var, EOVariable):
            var_list.append(var.path)
            if model.variables is not None and var.path in model.variables:
                validate_variable(var, model.variables[var.path], mode, out_anomalies, logger)

            elif mode == "EXACT":
                append_to_anomalies(
                    out_anomalies,
                    "MODEL",
                    f"Variable {var.path} not found in model but is in {product.name}",
                    logger,
                )
    if mode == "EXACT" or mode == "AT_LEAST":
        if model.variables is not None:
            for var_path, var_constraint in model.variables.items():
                if var_path not in var_list and var_constraint.required:
                    append_to_anomalies(
                        out_anomalies,
                        "MODEL",
                        f"Variable {var_path} not found in product {product.name} but defined in model",
                        logger,
                    )
    validate_attrs_schema(product, model.attrs_schema, mode, out_anomalies, logger)
    validate_attrs_list(product, model.attrs, mode, out_anomalies, logger)


def validate_variable(
    variable: EOVariable,
    model: EOVariableModel,
    mode: ModelValidationMode,
    out_anomalies: list[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    if model.dtype is not None and str(variable.dtype) != model.dtype:
        append_to_anomalies(
            out_anomalies,
            "MODEL",
            f"Wrong dtype detected on variable {variable.name}: {variable.dtype} != {model.dtype}",
            logger,
        )
    if model.dims is not None and list(variable.dims) != model.dims:
        append_to_anomalies(
            out_anomalies,
            "MODEL",
            f"Wrong dims detected on variable {variable.name} : {list(variable.dims)} != {model.dims}",
            logger,
        )
    validate_attrs_schema(variable, model.attrs_schema, mode, out_anomalies, logger)
    validate_attrs_list(variable, model.attrs, mode, out_anomalies, logger)


def check_product_model_validity(
    product: EOProduct,
    out_anomalies: List[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """
    Check if the input product/container is valid against it's model.
    .

    Parameters
    ----------
        product (EOProduct|EOContainer): input EOProduct|EOContainer
        validation_mode (str): selected validation mode: possible values
    """

    models_folder = EOConfiguration().get("model__folder")
    if product.product_type is None:
        append_to_anomalies(out_anomalies, "MODEL", f"No product type found in product {product.name}", logger)
        return
    model_local = AnyPath.cast(models_folder) / f"{product.product_type}.json"
    if not model_local.exists():
        append_to_anomalies(
            out_anomalies,
            "MODEL",
            f"No product type model {model_local.path} found in folder {models_folder}",
            logger,
        )
        return
    data = load_json_file(model_local)
    loaded = EOProductModel(**data)
    validate_product_against_model(product, loaded, "EXACT", out_anomalies, logger)


################################################
# EOProduct Model utility functions
################################################


def product_to_model(product: EOProduct) -> EOProductModel:
    return EOProductModel(
        product_type_regex=product.product_type if product.product_type is not None else ".*",
        attrs={p: AttributeModel() for p in get_all_paths_in_dict(product.attrs)},
        variables={
            p.path: EOVariableModel(dims=list(p.dims), dtype=(str(p.dtype) if p.dtype is not None else "float64"))
            for p in product.walk()
            if isinstance(p, EOVariable)
        },
    )


def product_to_model_json_file(product: EOProduct, filepath: AnyPath) -> None:
    with filepath.open("w") as f:
        f.write(product_to_model(product).model_dump_json(indent=4, exclude_unset=True))


def model_to_product(model: EOProductModel) -> EOProduct:
    attrs_to_use = {} if model.attrs is None else model.attrs
    result = EOProduct(
        product_type=model.product_type_regex,
        name="TOBEDEFINED",
        attrs=nested_dict_from_paths(list(attrs_to_use.keys())),
    )
    if model.variables is not None:
        for gr_name, constraint in model.variables.items():
            dims_to_use = tuple(constraint.dims) if constraint.dims is not None else tuple()
            size_to_use = [50] * (len(constraint.dims)) if constraint.dims is not None else [50]
            chunks_to_use = [10] * (len(constraint.dims)) if constraint.dims is not None else [10]
            dtype_to_use = constraint.dtype if constraint.dtype is not None else "float64"
            result[gr_name] = EOVariable(
                dims=dims_to_use,
                data=da.zeros(size_to_use, dtype=dtype_to_use, chunks=chunks_to_use),
            )
            var = result[gr_name]
            var_parent = var.parent
            if isinstance(var, EOVariable) and isinstance(var_parent, EOGroup):
                for dim in dims_to_use:
                    var_parent[dim] = EOVariable(
                        dims=(dim,),
                        data=da.arange(50, dtype="int16", chunks=(10,)),
                    )
                var.assign_coords({dim: var_parent[dim] for dim in dims_to_use})

    return result
