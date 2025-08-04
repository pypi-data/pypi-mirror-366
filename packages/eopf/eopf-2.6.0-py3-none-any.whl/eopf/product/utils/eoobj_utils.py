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
import collections
from typing import Any, Optional

from eopf import EOGroup, EOVariable
from eopf.product.eo_object import EOObject


def copy_variable(source: EOVariable, target: "EOGroup", name: Optional[str] = None) -> EOVariable:
    """
    Copies a variable into a group of a different product without duplicating data or attributes.

    Parameters
    ----------
    source: EOVariable
        the variable to copy, part of a source EOProduct
    target: EOGroup
        the group to place the new EOVariable into, part of a target EOProduct
    Returns
    -------
    EOVariable
        the variable of the target product just added
    """
    var_copy = EOVariable(name or source.name, source.data, attrs=source.attrs, dims=source.dims)  # avoids data dupli.
    target[name or source.name] = var_copy

    return var_copy


def copy_group(source: "EOGroup", target: "EOGroup", name: Optional[str] = None) -> "EOGroup":
    """
    Copies a group into a different product, without duplicating the data or attributes.

    Parameters
    ----------
    source: EOGroup
        the group to copy, part of a source EOProduct
    target: EOGroup
        the product or group to place the new EOGroup into, part of a target EOProduct
    name: str
        optional name of the target group, overwrites source.name as group name for target if provided
    Returns
    -------
    EOGroup
        the group of the target product just added
    """
    group_copy = EOGroup(name or source.name, attrs=copy_attrs(source.attrs), dims=source.dims)
    target[name or source.name] = group_copy
    for n, g in source.groups:
        copy_group(g, group_copy, n)
    for n, v in source.variables:
        copy_variable(v, group_copy, n)
    return group_copy


def copy_attrs(source: Any) -> Any:
    """
    Deep-copies an attribute tree (but not the leaves) and returns the copy.

    Parameters
    ----------
    source: Any
        either a dict or a list or a leaf of the attribute tree
    Returns
    -------
    Any
        a copy of the dict or just a reference to the value.
    """
    if isinstance(source, collections.abc.Mapping):
        target = dict()
        for k in source:
            target[k] = copy_attrs(source[k])
        return target
    elif isinstance(source, list):
        return [copy_attrs(i) for i in source]
    else:
        return source


# since the __getitem__ of stores can not return None
# one can use the NONE_EOV
NONE_EOObj: EOObject = EOVariable(name="None")


def is_None_EOObj(eov: EOObject) -> bool:
    """EOVariable used as replacement for None"""
    if eov.name == "None":
        return True
    else:
        return False
