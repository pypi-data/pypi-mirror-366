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
import contextlib
from shutil import rmtree
from tempfile import mkdtemp
from typing import TYPE_CHECKING, Any, Optional, Tuple, Union

from distributed import get_client

from eopf.common.file_utils import AnyPath
from eopf.config import EOConfiguration
from eopf.daskconfig import init_from_eo_configuration
from eopf.exceptions.errors import (
    EOStoreFactoryNoRegisteredStoreError,
    ProductRetrievalError,
)
from eopf.logging import EOLogging
from eopf.product import EOContainer, EOProduct
from eopf.store import EOProductStore
from eopf.store.store_factory import EOStoreFactory
from eopf.store.zarr import ZARR_PRODUCT_FORMAT

EOConfiguration().register_requested_parameter(
    "store__convert__use_multithreading",
    True,
    True,
    description="Activate Dask LocalCluster if no Dask client detected",
)

if TYPE_CHECKING:  # pragma: no cover
    from eopf.daskconfig.dask_context_manager import DaskContext


def convert(
    source_path: AnyPath | str,
    target_path: AnyPath | str,
    target_format: str = ZARR_PRODUCT_FORMAT,
    mask_and_scale: Optional[bool] = None,
    source_store_kwargs: dict[str, Any] = {},
    target_store_kwargs: dict[str, Any] = {},
) -> Tuple[EOProduct | EOContainer, str]:
    """
    Converts a product from one format to another

    Parameters
    ----------
    source_path: AnyPath|str
        file system path to an existing product
    target_path: AnyPath|str
        file system path. If exiting folder name is provided,
        the product will be placed under the dir and named via the default_filename_convention
    target_format: EOProductFormat
        format in which the source product will be converted
    mask_and_scale: Optional[bool]
        mask and scale the output product
    source_store_kwargs: dict[str, Any] = {}
        kwargs of the source store
    target_store_kwargs: dict[str, Any] = {}
        kwargs of the source store

    Raises
    -------
    EOStoreFactoryNoRegisteredStoreError
    ProductRetrievalError

    Returns
    -------
    EOProduct | EOContainer
    """
    LOGGER = EOLogging().get_logger("eopf.store.convert")
    source_store_class: Optional[type[EOProductStore]] = None
    target_store_class: Optional[type[EOProductStore]] = None
    source_store: Optional[EOProductStore] = None
    target_store: Optional[EOProductStore] = None
    output_dir: AnyPath
    product_name: str

    eopf_config = EOConfiguration()

    if mask_and_scale is None:
        mask_and_scale = eopf_config.get("product__mask_and_scale")

    source_fspath: AnyPath = AnyPath.cast(url=source_path, **source_store_kwargs)
    target_fspath: AnyPath = AnyPath.cast(url=target_path, **target_store_kwargs)

    # determine the source store
    source_store_class = EOStoreFactory.get_product_store_by_file(source_fspath)

    # Check if a dask client is already available, if not create default
    dask_context_manager: Union[Any, DaskContext] = contextlib.nullcontext()
    if eopf_config.store__convert__use_multithreading:
        LOGGER.debug("MultiThread Convert enabled")
        try:
            client = get_client()
            if client is None:
                # default to multithread local cluster
                dask_context_manager = init_from_eo_configuration()
        except Exception:
            # no client ? # default to EOConfigured one
            dask_context_manager = init_from_eo_configuration()

    with dask_context_manager:
        LOGGER.info(f"Converting {source_fspath.path} to {target_fspath.path}")
        LOGGER.debug(f"Using dask context {dask_context_manager}")

        # TMP FIX sentineltoolbox does not support s3 access
        is_remote, source_fspath, tmp_download_dir = _convert_remote_handling(source_fspath)

        # TMP FIX sentineltoolbox does not support zip files
        is_zip, source_fspath, tmp_unzip_dir = _convert_handle_zip(source_fspath)

        # when creating the eop the data should be kept as on disk
        if "mask_and_scale" in source_store_kwargs:
            mask_and_scale = source_store_kwargs.pop("mask_and_scale")

        # load the EOProduct from source_path
        source_store = source_store_class(source_fspath.path, mask_and_scale=mask_and_scale, **source_store_kwargs)
        source_store.open()
        eop: EOProduct | EOContainer = source_store.load()
        source_store.close()

        # determine the target store
        try:
            # when the user specifies the name of the product
            target_store_class = EOStoreFactory.get_product_store_by_file(target_fspath)
            output_dir = target_fspath.dirname()
            product_name = target_fspath.basename

        except EOStoreFactoryNoRegisteredStoreError as err:
            # when the user gives the directory where the product should be written
            # and the name is automatically computed as per EOProduct rules
            output_dir = target_fspath
            if not output_dir.exists():
                output_dir.mkdir()

            if output_dir.isdir():
                for format, store_class in EOStoreFactory.product_formats.items():
                    # iterate over each registered store and check if the target_format matches
                    if target_format == format:
                        target_store_class = store_class

            # raise EOStoreFactoryNoRegisteredStoreError when no store could be retrieved
            if target_store_class is None:
                raise err
            product_name = eop.get_default_file_name_no_extension()

        LOGGER.info(
            f"EOProduct {eop.name} successfully loaded, starting to write to "
            f"{output_dir}/{product_name}{target_store_class.EXTENSION}",
        )

        # when writing the eop the data should be kept as on disk
        if "mask_and_scale" in target_store_kwargs:
            mask_and_scale = target_store_kwargs["mask_and_scale"]
        else:
            mask_and_scale = False

        # write the EOProduct with the target_store at the target_path
        target_store = target_store_class(output_dir, mask_and_scale=mask_and_scale, **target_store_kwargs)
        mode: str = target_store_kwargs.get("mode", "w+")
        target_store.open(mode=mode)
        target_store[product_name] = eop
        target_store.close()

        LOGGER.info("Conversion finished")

        # TMP FIX sentineltoolbox does not support zip files
        if is_remote:
            rmtree(tmp_download_dir)
        if is_zip:
            rmtree(tmp_unzip_dir)

        return eop, product_name


def _convert_handle_zip(source_fspath: AnyPath) -> Tuple[bool, AnyPath, str]:
    is_zip: bool = False
    tmp_unzip_dir = ""
    if "zip" in source_fspath.protocol_list():
        is_zip = True
        # check zip
        zip_ok = source_fspath._fs.zip.testzip()
        if zip_ok is not None:
            raise ProductRetrievalError(f"Corrupt zip file: {zip_ok}")
        try:
            # make a safe temporary directory
            tmp_unzip_dir = mkdtemp(prefix="eopf-unzip-")
            # extract the zip inside the temporary directory
            source_fspath._fs.zip.extractall(tmp_unzip_dir)
        except Exception as err:
            raise ProductRetrievalError(f"Can not unzip product {source_fspath.path} due to: {err}")
        finally:
            # source_fspath is replaced by the extracted product
            source_fspath = AnyPath.cast(tmp_unzip_dir).ls()[0]
    return is_zip, source_fspath, tmp_unzip_dir


def _convert_remote_handling(source_fspath: AnyPath) -> Tuple[bool, AnyPath, str]:
    is_remote: bool = False
    tmp_download_dir: str = ""
    if not source_fspath.islocal():
        is_remote = True
        try:
            # make a safe temporary directory
            tmp_download_dir = mkdtemp(prefix="eopf-download-")
            if "zip" in source_fspath.protocol_list():
                tmp_download_product = AnyPath.cast(tmp_download_dir) / source_fspath.basename
                tmp_download_product.mkdir()
            else:
                tmp_download_product = AnyPath.cast(tmp_download_dir)
            # download the product in the tmp dir
            source_fspath._fs.get(source_fspath._path, tmp_download_product.path, recursive=True)
        except Exception as err:
            raise ProductRetrievalError(f"Can not download product from {source_fspath.path} due to {err}")
        finally:
            # source_fspath is replaced by the downloaded product
            source_fspath = AnyPath.cast(tmp_download_dir).ls()[0]
    return is_remote, source_fspath, tmp_download_dir
