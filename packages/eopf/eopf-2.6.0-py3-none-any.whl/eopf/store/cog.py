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
import json
import os
import pathlib
import warnings
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Tuple, Union, cast

import rasterio
import rio_cogeo
import rioxarray
import xarray

from eopf.common.constants import DIMENSIONS_NAME, OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.common.json_utils import decode_all_attrs, encode_all_attrs
from eopf.exceptions import StoreNotOpenError
from eopf.product import EOContainer, EOGroup, EOProduct, EOVariable
from eopf.store import EOProductStore, StorageStatus
from eopf.store.netcdf import EONetCDFStore
from eopf.store.store_factory import EOStoreFactory

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_object import EOObject

# since the cog store is non product specific, many variable do not have a geo-reference
# hence we filter out NotGeoreferencedWarning warnings
warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)


@EOStoreFactory.register_store("cogs")
class EOCogStore(EOProductStore):
    def load(self, name: str = "", **kwargs: Dict[str, Any]) -> EOProduct | EOContainer:
        """
        TBD
        """
        return EOProduct("")

    URL_VALIDITY_DESCRIPTION = "Folder with .cog or .cog.zip extension"
    PRODUCT_VALIDITY_DESCRIPTION = "Folder with .cog extension of file with .cog.zip extension"
    EXTENSION = ".cog"

    # Wrapper class
    ATTRIBUTES_FILE_NAME = "attrs.json"

    SUPPORTED_FORMATS = [".cog", ".nc", ".tif"]

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        super().__init__(url, *args, **kwargs)
        self._driver: str = "COG"
        self._cog_kwargs: Dict[Any, Any] = {
            "COMPRESS": "DEFLATE",
            "NUM_THREADS": "ALL_CPUS",
            "PREDICTOR": "NO",
            "OVERVIEWS": "NONE",
        }
        self._netCDF4_kwargs: Dict[Any, Any] = {}

    def open(self, mode: OpeningMode | str = OpeningMode.OPEN, **kwargs: Any) -> "EOProductStore":
        mode = OpeningMode.cast(mode)

        if mode == OpeningMode.OPEN and not self.url.exists():
            raise FileNotFoundError(f"File {self.url} not Found")

        if mode == OpeningMode.CREATE or mode == OpeningMode.CREATE_OVERWRITE:
            self._cog_kwargs = kwargs.pop("cog_kwargs", self._cog_kwargs)
            self._netCDF4_kwargs = kwargs.pop("_netCDF4_kwargs", self._netCDF4_kwargs)

        if mode not in [OpeningMode.OPEN, OpeningMode.CREATE, OpeningMode.CREATE_OVERWRITE]:
            raise ValueError("Unsuported mode, only OPEN or CREATE")

        if (mode == OpeningMode.CREATE or mode == OpeningMode.CREATE_OVERWRITE) and not self.url.isdir():
            self.url.mkdir(exist_ok=True)

        super().open(mode)
        return self

    def is_group(self, path: str) -> bool:
        self.check_is_opened()
        return (self.url / path).isdir()

    def _get_variable(self, path: str) -> AnyPath | None:
        """
        Return the path to a variable (test different extension).
        None is returned if not found

        :param path: variable path in the product ("group/variable" syntax)
        :return: Path object to file storing the variable
        """

        for extension in EOCogStore.SUPPORTED_FORMATS:
            candidate = self.url / (path.rstrip("/") + extension)
            if candidate.isfile():
                return candidate
        return None

    def is_variable(self, path: str) -> bool:
        self.check_is_opened()
        return self._get_variable(path) is not None

    def is_product(self, path: str) -> bool:
        return (self.url / (path + self.EXTENSION)).isdir()

    def __len__(self) -> int:
        self.check_is_opened()
        if self.mode != OpeningMode.OPEN:
            raise NotImplementedError("Only available in reading mode")
        return sum(1 for _ in self.iter(""))

    def iter(self, path: str) -> Iterator[str]:
        self.check_is_opened()
        target_group = self.url / path
        if not target_group.exists():
            raise FileNotFoundError(f"Path {path} not found in {self.url}")
        for item in target_group.ls():
            if item.isdir():
                # group case
                yield item.relpath(target_group)
            cur_suffix = item.suffix
            if cur_suffix in EOCogStore.SUPPORTED_FORMATS:
                # remove suffix to show the variable name
                yield item.relpath(target_group)[: -len(cur_suffix)]

    def write_attrs(self, group_path: str, attrs: Any = ...) -> None:
        self.check_is_opened()

        if self.mode != OpeningMode.CREATE and self.mode != OpeningMode.CREATE_OVERWRITE:
            raise NotImplementedError("Only available in writing mode")

        # if there are group attributes write then as json file inside the group
        if attrs:
            target_group = self.url / group_path
            attrs_file_path = target_group / self.ATTRIBUTES_FILE_NAME
            # create group if needed
            target_group.mkdir(exist_ok=True)
            # write the json file
            with attrs_file_path.open(mode="w") as fp:
                json.dump(attrs, fp)

    def __getitem__(self, key: str) -> "EOObject":
        self.check_is_opened()

        # TODO: is it a requirement to forbid item access in CREATE mode ?
        if self._mode != OpeningMode.OPEN:
            raise NotImplementedError("Only available in reading mode")

        if self.is_group(key):
            return EOGroup(attrs=self.read_attrs(self.url / key))
        var_path = self._get_variable(key)
        if var_path is not None:
            eov_name = var_path.basename[: -len(var_path.suffix)]
            eov = self.read_eov(var_path, eov_name)
            existing_dims = eov.attrs.pop(DIMENSIONS_NAME, tuple())
            return EOVariable(key, eov, dims=existing_dims)

        raise KeyError(f"{key} not found!")

        # LOCAL
        if key in ["", "/"]:
            key_path = pathlib.Path(self.url).resolve()
        else:
            # Temporary solution, to be updated / improved with fsspec
            # key_path = Path(self.url).resolve()  /  key.removeprefix(self.sep)
            key_path = pathlib.Path(f"{self.url}/{key}").resolve()

        # check if key with extension (nc or cog) is file, and return EOV
        # Try EOV and all extensions
        for suffix in [".nc", ".cog", ".tif"]:
            if key_path.with_suffix(suffix).is_file():
                eov_name = key_path.stem
                eov = self.read_eov(key_path.with_suffix(suffix), eov_name)
                existing_dims = eov.attrs.pop(DIMENSIONS_NAME, tuple())
                return EOVariable(eov_name, eov, dims=existing_dims)
        # Read directory and return EOGroup
        if key_path.is_dir():
            return self._read_dir(key_path)

    def __setitem__(self, key: str, value: "EOObject") -> None:
        self.check_is_opened()

        if self.mode != OpeningMode.CREATE and self.mode != OpeningMode.CREATE_OVERWRITE:
            raise NotImplementedError("Only available in writing mode")

        from eopf.product import EOGroup, EOVariable

        if key.startswith("/"):
            key = key[1:]

        if isinstance(value, EOVariable) or isinstance(value, xarray.DataArray):
            self._write_eov(value, self.url, key)
        elif isinstance(value, EOGroup):
            output_dir = self.url / key
            if not output_dir.isdir():
                output_dir.mkdir(exist_ok=True)
            # write the attrbutes of the group
            self.write_attrs(key, value.attrs)
            # iterate trough all variables of the EOGroup
            # and write each in one file, cog or netCDF4
            for var_name, var_val in value.variables:
                self._write_eov(var_val, output_dir, var_name)
        else:
            raise NotImplementedError()

    def __delitem__(self, key: str) -> None:
        pass

    # docstr-coverage: inherited
    @staticmethod
    def guess_can_read(file_path: str | AnyPath, **kwargs: Any) -> bool:
        path_obj = AnyPath.cast(file_path, **kwargs.get("storage_options", {}))
        if EOCogStore.is_valid_url(path_obj):
            if not path_obj.exists():
                return False
            if path_obj.suffix == ".zip":
                if not path_obj.isfile():
                    return False
            else:
                if not path_obj.isdir():
                    return False
        else:
            return False
        # No reason found not to be able to read it
        return True

    @staticmethod
    def is_valid_url(file_path: str | AnyPath, **kwargs: Any) -> bool:
        path_obj = AnyPath.cast(file_path, **kwargs.get("storage_options", {}))
        return ".cog" in path_obj.suffixes and path_obj.suffix in [".cog", ".zip"]

    @staticmethod
    def _guess_can_read_files(file_path: str | AnyPath) -> bool:
        path_obj = AnyPath.cast(file_path)
        return path_obj.suffix in [".nc", ".cog", ".tif"]

    def _is_cogable(self, value: "EOVariable") -> bool:
        """
        Method used to determine if an EOVariable can be written
        as one or multiple cog files.

        Parameters
        ----------
        value: EOVariable
        """

        is_cogable: bool = False
        # is cogable when we have more than one dimensions
        # and the data type is not string
        if len(value.dims) > 1:
            is_cogable = True

        # hotfix due to https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/117
        # related to issue https://github.com/corteva/rioxarray/issues/402
        if is_cogable:
            for shp in value.shape[-2:]:
                if shp < 8:
                    is_cogable = False
                    break

        # S1 L2 variables containing strings should not be converted to cog
        # e.g. /conditions/rvl/zero_doppler_time
        if value.data.dtype.kind == "S":
            is_cogable = False

        return is_cogable

    def read_attrs(self, dir_path: AnyPath) -> dict[str, Any]:
        if self.status == StorageStatus.CLOSE:
            raise StoreNotOpenError("Store must be open before access to it")

        output = {}
        attrs_path = dir_path / EOCogStore.ATTRIBUTES_FILE_NAME
        if attrs_path.isfile():
            with attrs_path.open(mode="r") as fp:
                output = json.load(fp)
        return output

    def read_eov(self, path: AnyPath, eov_name: str) -> Union[xarray.DataArray, "EOVariable"]:
        """
        This method is used to read a file and return it as rasterio dataset.

        Parameters
        ----------
        path: pathlib.Path
            Path to input COG or .nc file
        eov_name: str
            Name of EOVariable

        Raise
        -----
        TypeError, when input file cannot be read or converted by rasterrio

        Return
        ------
        xarray.DataArray
        """

        if path.suffix in [".cog", ".tif"]:

            if path.islocal():
                rio_ds = rasterio.open(path.path)
                # Return rasterio dataset for .cog and .nc files.
                rio_data = rioxarray.open_rasterio(
                    rio_ds,
                    lock=False,
                    chunks="auto",  # type: ignore[arg-type]  # rioxarray chunks value is mistyped
                )
            else:
                with path.open() as file_input:
                    rio_ds = rasterio.open(file_input)
                    # Return rasterio dataset for .cog and .nc files.
                    rio_data = rioxarray.open_rasterio(
                        rio_ds,
                        lock=False,
                        chunks="auto",  # type: ignore[arg-type]  # rioxarray chunks value is mistyped
                    )
            if isinstance(rio_data, list):
                raise NotImplementedError("There no implementation for list of Dataset")
            data: xarray.DataArray
            if isinstance(rio_data, xarray.Dataset):
                data = rio_data.to_array()
            else:
                data = rio_data
            # TODO: cog_info
            cogeo_raw_attrs = rio_cogeo.cog_info(rio_ds.name)
            cogeo_attrs = decode_all_attrs(cogeo_raw_attrs.Tags["Image Metadata"])
            data.attrs = cogeo_attrs
            dimensions_tuple = ast.literal_eval(data.attrs[DIMENSIONS_NAME])
            data.attrs["scale_factor"] = cogeo_raw_attrs.Profile.Scales[0]
            if len(dimensions_tuple) == 2 and len(data.shape) == 3 and data.shape[0] == 1:
                data = data[0, :, :]
            rio_data.close()
            rio_ds.close()
            return data
        elif path.suffix == ".nc":
            from eopf.product import EOVariable

            # TODO: use a NetCDF accessor ?

            reader = EONetCDFStore(path)
            reader.open()
            tmp_eov = reader[eov_name]
            reader.close()
            return cast(EOVariable, tmp_eov)
        else:
            raise IOError(f"Cog store can NOT read: {path}")

    def _write_eov(self, value: "EOVariable", output_dir: AnyPath, var_name: str) -> None:
        """
        This method is used to write an EOVariable to cog or netcdf format.

        Parameters
        ----------
        value: EOVariable
            Variable to be written
        outputdir: AnyPath
            Path to output folder
        var_name: str
            Name of EOVariable
        """
        var_name = var_name.removeprefix(self.sep)
        file_path = output_dir / var_name

        # unscale EOVar and keep the attrs, as they need to written to disk
        value.unscale(remove_scale_attrs=False)

        # determine if an EOVariable can be written as cog
        if self._is_cogable(value):
            self._write_cog(value, file_path)
        else:
            self._write_netCDF4(value, file_path, os.path.basename(var_name))

    def _write_cog(self, value: "EOVariable", file_path: AnyPath) -> None:
        """
        This method writes multi0dimensional data to COG files

        Parameters
        ----------
        value: EOVariable
            rasterIO dataset
        file_path: AnyPath
            Base Path for new COG files
        """
        from eopf.product import EOVariable

        # dtype conversions to COG supported dtypes
        value = EOVariable(data=self._dtype_convert(value))

        dims_cp = self._get_dims_cp(value.shape)
        if dims_cp == []:
            # 2 dimensional variable
            # by convention the last dims is y and -2 is y
            self._write_raster(
                raster=value._data,
                file_path=file_path,
                x_dim=value.dims[-1],
                y_dim=value.dims[-2],
                dtype=value._data.dtype,
            )
        else:
            # more than 2 dimensions
            # iterate over each cartesian prod sub-register_requested_parameter
            from ast import literal_eval

            parent_path = file_path.dirname()

            for cur_combination in dims_cp:
                file_name: str = file_path.basename
                data_slice: str = ""
                # build new file name and data slice
                for dim_id, dim_val in enumerate(cur_combination):
                    dim_name = value.dims[dim_id]
                    if value.shape[dim_id] == 1:
                        # in some cases, e.g. S2 MSIL1C, there are dimensions with value 1
                        # which do not bring any added value, thus no need to add the name
                        # of the dimension to the variable name
                        pass
                    elif (self._reconversion_attrs is not None) and (dim_name in self._reconversion_attrs):
                        # for S1 L1 products the values of the polarisation dim are passed along with the
                        # reconversion_attrs. Hence we can add the dim value meaning to the variable name
                        dim_val_meaning = self._reconversion_attrs[dim_name]["meanings"][dim_val]
                        file_name += f"__{dim_val_meaning}"
                    else:
                        # append dim_name/meaning to the variable name
                        # only when the dimension has multiple values
                        file_name += f"__{value.dims[dim_id]}-{dim_val}"
                    data_slice += f"{dim_val},"
                # remove trailing comma
                data_slice.rstrip(",")

                # concatenate the folder with the new file_name add tif suffix and make sure the path is absolute
                new_file_path = parent_path / file_name

                # by convention the last dims is y and -2 is y
                self._write_raster(
                    raster=value._data[literal_eval(data_slice)],
                    file_path=new_file_path,
                    x_dim=value.dims[-1],
                    y_dim=value.dims[-2],
                    dtype=value._data.dtype,
                )

    def _write_netCDF4(self, value: "EOObject", file_path: AnyPath, var_name: str) -> None:
        """
        This method is used to write rasters to .nc (netcdf) files

        Parameters
        ----------
        value: Any
            rasterIO dataset
        file_path: AnyPath
            Path to .nc file
        var_name: str
            Name of EOVariable
        """
        # register_requested_parameter suffix .nc
        nc_path = file_path + ".nc"

        # write the netCDF4 file
        nc = EONetCDFStore(nc_path)
        if self.mode is None:
            raise StoreNotOpenError()
        nc.open(mode=self.mode, **self._netCDF4_kwargs)
        nc[var_name] = value
        nc.close()

    def _dtype_convert(self, value: "EOVariable") -> "EOVariable":
        """
        COG does not support many data types, thus conversions have to be carried to supported data types

        Parameters
        ----------
        value: EOVariable

        Returns
        ---------
        EOVariable
        """
        import numpy as np

        # convert bool and int8 to int16
        if value.dtype in [np.dtype("bool"), np.dtype("int8")]:
            return value.astype(np.int16)
        # convert datetime into unix time float32
        elif value.dtype == np.dtype("datetime64[us]"):
            return value.astype("datetime64[s]").astype(np.int32)
        else:
            return value

    def _write_raster(
        self,
        raster: xarray.core.dataarray.DataArray,
        file_path: AnyPath,
        x_dim: str,
        y_dim: str,
        dtype: Any,
    ) -> None:
        """
        This method writes rasters as COG

        Parameters
        ----------
        raster: xarray.core.dataarray.DataArray
            rasterIO dataset
        file_path: AnyPath
            Base Path for new COG files
        x_dim: str
            name of the x dimension
        y_dim: str
            name of the y dimension
        dtype: Any
            data type of the raster
        """
        # make sure the dimensions are consistent
        raster.attrs["_ARRAY_DIMENSIONS"] = raster.dims

        # add tif suffix and make sure the path is absolute
        tif_path = file_path + ".tif"

        # register_requested_parameter spatial coordinates of the subtracted raster
        raster.rio.set_spatial_dims(x_dim=x_dim, y_dim=y_dim, inplace=True)

        # break eovariable internals like dims.
        raster.attrs.update(encode_all_attrs(raster.attrs))

        # write the COG file
        if tif_path.islocal():
            raster.rio.to_raster(tif_path.path, lock=False, driver=self._driver, dtype=dtype, **self._cog_kwargs)
            raster.close()
        else:
            with tif_path.open(mode="wb") as file_obj:
                raster.rio.to_raster(file_obj, lock=False, driver=self._driver, dtype=dtype, **self._cog_kwargs)
                raster.close()

    def _cartesian_product(self, cp: List[List[int]], set_b: List[int]) -> List[List[int]]:
        """
        Computes cartesian product of two sets of integers
        saved as lists

        Parameters
        ----------
        cp: List[List[int]]
            previous result of a cartesian product
        set_b: List[int]

        Returns
        ----------
        new_cp: List[List[int]]
        """

        new_cp: List[List[int]] = []
        if len(cp) == 1:
            for e in cp[0]:
                for b in set_b:
                    new_cp.append([e, b])
        else:
            for sub_set_a in cp:
                for b in set_b:
                    new_cp.append(sub_set_a + [b])

        return new_cp

    def _get_dims_cp(self, shape: Tuple[int, ...]) -> List[List[int]]:
        """
        Build and computes a cartesian product of the iterable dims
        from the shape of an EOVariable. The iterable dims are all
        with the exception of the last 2, which by convention are
        considered dims of the raster.

        Parameters
        ----------
        shape: tuple[int]
            shape of a multidimensional variable

        Returns
        ----------
        cp: List[List[int]]
            a list containing lists of cp sets
        """

        if len(shape) == 2:
            cp = []
        elif len(shape) == 3:
            cp = [[val] for val in range(shape[0])]
        else:
            # more than 3 dimensions as _is_cogable precedes
            # the call to current function

            # compute sets of dims vals
            sets: List[List[int]] = []
            dim_size: int
            for dim_size in shape[:-2]:
                sets.append([val for val in range(dim_size)])

            # compute cartesian product over multiple sets
            cp = [sets.pop(0)]
            while len(sets) > 0:
                cp = self._cartesian_product(cp, sets.pop(0))

        return cp
