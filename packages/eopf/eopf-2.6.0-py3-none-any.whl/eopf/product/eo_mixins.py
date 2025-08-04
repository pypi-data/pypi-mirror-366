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
import operator
from typing import Any, Callable, Generic, Optional, TypeVar, Union

import numpy as np
import xarray as xr

EOV_TYPE = TypeVar("EOV_TYPE", bound="EOVariableOperatorsMixin[Any]")
# Type of EOVariable, could be replaced by PEP 673 -- Self Type, starting with Python 3.11


class EOVariableOperatorsMixin(Generic[EOV_TYPE]):
    """
    Provide unary and binary operations on the _data of it's subtype EOV_TYPE.
    All inheriting class must define the following attributes:

    Attributes
    ----------
    _data : xarray.DataArray
    """

    __slots__ = ()
    __array_priority__ = 60

    _data: xr.DataArray

    def _init_similar(self: EOV_TYPE, data: xr.DataArray) -> EOV_TYPE:  # pragma: no cover
        raise NotImplementedError

    def __bool__(self: Any) -> bool:
        return bool(self._data)

    def __float__(self: Any) -> float:
        return float(self._data)

    def __int__(self: Any) -> int:
        return int(self._data)

    def __complex__(self: Any) -> complex:
        return complex(self._data)

    def __array__(self: Any, dtype: Optional[Union[np.dtype[Any], str]] = None) -> np.ndarray[Any, Any]:
        return np.asarray(self._data, dtype=dtype)

    def __array_ufunc__(self, ufunc: Any, method: str, *inputs: Any, **kwargs: Any) -> EOV_TYPE:
        data_list = [var._data if isinstance(var, EOVariableOperatorsMixin) else var for var in inputs]
        return self._init_similar(self._data.__array_ufunc__(ufunc, method, *data_list, **kwargs))

    def __array_wrap__(self, obj: Any, context: Optional[Any] = None) -> EOV_TYPE:
        return self._init_similar(self._data.__array_wrap__(obj, context=context))

    def __apply_binary_ops__(
        self: EOV_TYPE,
        other: Any,
        ops: Callable[[Any, Any], Any],
        reflexive: Optional[bool] = False,
    ) -> EOV_TYPE:
        if isinstance(other, EOVariableOperatorsMixin):
            other_value = other._data
        else:
            other_value = other
        data = self._data

        return self._init_similar(ops(data, other_value) if not reflexive else ops(other_value, data))

    def __add__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.add)

    def __sub__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.sub)

    def __mul__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.mul)

    def __pow__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.pow)

    def __truediv__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.truediv)

    def __floordiv__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.floordiv)

    def __mod__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.mod)

    def __and__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.and_)

    def __xor__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.xor)

    def __or__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.or_)

    def __lt__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.lt)

    def __le__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.le)

    def __gt__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.gt)

    def __ge__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.ge)

    def __radd__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.add, reflexive=True)

    def __rsub__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.sub, reflexive=True)

    def __rmul__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.mul, reflexive=True)

    def __rpow__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.pow, reflexive=True)

    def __rtruediv__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.truediv, reflexive=True)

    def __rfloordiv__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.floordiv, reflexive=True)

    def __rmod__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.mod, reflexive=True)

    def __rand__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.and_, reflexive=True)

    def __rxor__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.xor, reflexive=True)

    def __ror__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.or_, reflexive=True)

    def __apply_inplace_ops__(self: EOV_TYPE, other: Any, ops: Callable[[Any, Any], Any]) -> EOV_TYPE:
        if isinstance(other, EOVariableOperatorsMixin):
            other_value = other._data
        else:
            other_value = other

        data = self._data

        self._data = ops(data, other_value)
        return self

    def __iadd__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.iadd)

    def __isub__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.isub)

    def __imul__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.imul)

    def __ipow__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.ipow)

    def __itruediv__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.itruediv)

    def __ifloordiv__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.ifloordiv)

    def __imod__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.imod)

    def __iand__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.iand)

    def __ixor__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.ixor)

    def __ior__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.ior)

    def __apply_unary_ops__(self: EOV_TYPE, ops: Callable[[Any], Any], *args: Any, **kwargs: Any) -> EOV_TYPE:
        return self._init_similar(ops(self._data), *args, **kwargs)

    def __neg__(self: EOV_TYPE) -> EOV_TYPE:
        return self.__apply_unary_ops__(operator.neg)

    def __pos__(self: EOV_TYPE) -> EOV_TYPE:
        return self.__apply_unary_ops__(operator.pos)

    def __abs__(self: EOV_TYPE) -> EOV_TYPE:
        return self.__apply_unary_ops__(operator.abs)

    def __invert__(self: EOV_TYPE) -> EOV_TYPE:
        return self.__apply_unary_ops__(operator.invert)

    def round(self: EOV_TYPE, *args: Any, **kwargs: Any) -> EOV_TYPE:
        return self.__apply_unary_ops__(xr.DataArray.round, *args, **kwargs)

    def argsort(self: EOV_TYPE, *args: Any, **kwargs: Any) -> EOV_TYPE:
        return self.__apply_unary_ops__(xr.DataArray.argsort, *args, **kwargs)

    def conj(self: EOV_TYPE, *args: Any, **kwargs: Any) -> EOV_TYPE:
        return self.__apply_unary_ops__(xr.DataArray.conj, *args, **kwargs)

    def conjugate(self: EOV_TYPE, *args: Any, **kwargs: Any) -> EOV_TYPE:
        return self.__apply_unary_ops__(xr.DataArray.conjugate, *args, **kwargs)

    __add__.__doc__ = operator.add.__doc__
    __sub__.__doc__ = operator.sub.__doc__
    __mul__.__doc__ = operator.mul.__doc__
    __pow__.__doc__ = operator.pow.__doc__
    __truediv__.__doc__ = operator.truediv.__doc__
    __floordiv__.__doc__ = operator.floordiv.__doc__
    __mod__.__doc__ = operator.mod.__doc__
    __and__.__doc__ = operator.and_.__doc__
    __xor__.__doc__ = operator.xor.__doc__
    __or__.__doc__ = operator.or_.__doc__
    __lt__.__doc__ = operator.lt.__doc__
    __le__.__doc__ = operator.le.__doc__
    __gt__.__doc__ = operator.gt.__doc__
    __ge__.__doc__ = operator.ge.__doc__
    __radd__.__doc__ = operator.add.__doc__
    __rsub__.__doc__ = operator.sub.__doc__
    __rmul__.__doc__ = operator.mul.__doc__
    __rpow__.__doc__ = operator.pow.__doc__
    __rtruediv__.__doc__ = operator.truediv.__doc__
    __rfloordiv__.__doc__ = operator.floordiv.__doc__
    __rmod__.__doc__ = operator.mod.__doc__
    __rand__.__doc__ = operator.and_.__doc__
    __rxor__.__doc__ = operator.xor.__doc__
    __ror__.__doc__ = operator.or_.__doc__
    __iadd__.__doc__ = operator.iadd.__doc__
    __isub__.__doc__ = operator.isub.__doc__
    __imul__.__doc__ = operator.imul.__doc__
    __ipow__.__doc__ = operator.ipow.__doc__
    __itruediv__.__doc__ = operator.itruediv.__doc__
    __ifloordiv__.__doc__ = operator.ifloordiv.__doc__
    __imod__.__doc__ = operator.imod.__doc__
    __iand__.__doc__ = operator.iand.__doc__
    __ixor__.__doc__ = operator.ixor.__doc__
    __ior__.__doc__ = operator.ior.__doc__
    __neg__.__doc__ = operator.neg.__doc__
    __pos__.__doc__ = operator.pos.__doc__
    __abs__.__doc__ = operator.abs.__doc__
    __invert__.__doc__ = operator.invert.__doc__
    round.__doc__ = xr.DataArray.round.__doc__
    argsort.__doc__ = xr.DataArray.argsort.__doc__
    conj.__doc__ = xr.DataArray.conj.__doc__
    conjugate.__doc__ = xr.DataArray.conjugate.__doc__
