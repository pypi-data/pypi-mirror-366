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


from typing import Any, cast

import click

from eopf import EOProduct
from eopf.cli.cli import EOPFPluginCommandCLI, EOPFPluginGroupCLI
from eopf.common.file_utils import AnyPath, load_json_file
from eopf.logging import EOLogging
from eopf.product.eo_product_validation import (
    EOProductModel,
    product_to_model_json_file,
    validate_product_against_model,
)
from eopf.product.eo_validation import AnomalyDescriptor
from eopf.store.store_factory import EOStoreFactory


class EOCLIModelCreate(EOPFPluginCommandCLI):
    """EO cli command to create a model from a zarr product.

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name = "create"
    cli_params: list[click.Parameter] = [
        click.Argument(["source_path"], type=click.Path()),
        click.Argument(["target_path"], type=click.Path()),
    ]
    help = (
        "Generate the json model of a product\n\n\n"
        "Args:\n\n"
        "  source_path = Source product \n\n"
        "  target_path = json file to write to\n\n"
    )

    @staticmethod
    def callback_function(
        source_path: str,
        target_path: str,
    ) -> Any:
        """

        Parameters
        ----------
        source_path
        target_path



        Returns
        -------

        """

        logger = EOLogging().get_logger("eopf.cli.model_create")
        logger.info(f"Creating model for product {source_path} to {target_path}")

        try:
            source_fspath: AnyPath = AnyPath.cast(url=source_path)

            # determine the source store
            source_store_class = EOStoreFactory.get_product_store_by_file(source_fspath)
            # load the EOProduct from source_path
            source_store = source_store_class(source_fspath.path)
            source_store.open()
            eop: EOProduct = cast(EOProduct, source_store.load())
            source_store.close()

            logger.info(f"EOProduct {eop} successfully loaded, starting to write json model")
            product_to_model_json_file(eop, AnyPath.cast(target_path))
        except Exception as e:
            logger.error("Error while generating product model")
            logger.error(f"{e}")
            return 1

        logger.info(f"Model successfully written in {target_path}")
        return 0


class EOCLIModelValidate(EOPFPluginCommandCLI):
    """EO cli command to create a model from a zarr product.

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name = "validate"
    cli_params: list[click.Parameter] = [
        click.Argument(["source_path"], type=click.Path()),
        click.Argument(["model_path"], type=click.Path()),
    ]
    help = (
        "Validate a product against its model\n\n\n"
        "Args:\n\n"
        "  source_path = Source product \n\n"
        "  model_path = json file to read model from\n\n"
    )

    @staticmethod
    def callback_function(
        source_path: str,
        model_path: str,
    ) -> Any:
        """

        Parameters
        ----------
        source_path
        model_path



        Returns
        -------

        """

        logger = EOLogging().get_logger("eopf.cli.model_validate")
        logger.info(f"Validation product {source_path} with {model_path}")

        try:
            source_fspath: AnyPath = AnyPath.cast(url=source_path)

            # determine the source store
            source_store_class = EOStoreFactory.get_product_store_by_file(source_fspath)
            # load the EOProduct from source_path
            source_store = source_store_class(source_fspath.path)
            source_store.open()
            eop: EOProduct = cast(EOProduct, source_store.load())
            source_store.close()

            logger.info(f"EOProduct {eop.name} successfully loaded, starting to validate model")
            anomalies: list[AnomalyDescriptor] = []
            json_path = AnyPath(model_path)
            data = load_json_file(json_path)
            loaded = EOProductModel(**data)
            validate_product_against_model(eop, out_anomalies=anomalies, logger=logger, model=loaded, mode="EXACT")
            if len(anomalies) != 0:
                logger.error("Product is not valid against it's model")
            else:
                logger.info("Product is valid against it's model !!!")
            for anom in anomalies:
                logger.error(f"** {anom.description}")
            if len(anomalies) != 0:
                return 1
        except Exception as e:
            logger.error("Error while validating product against model")
            logger.error(f"{e}")
            return 1

        return 0


class EOCLIModel(EOPFPluginGroupCLI):
    """EOTrigger cli command aggregator to triggers other services

    Parameters
    ----------
    **attrs: Any
        any argument for click.Command, click.MultiCommand

    See Also
    --------
    click.Group
    """

    name = "model"
    cli_commands: list[click.Command] = [EOCLIModelCreate(), EOCLIModelValidate()]
    help = "CLI commands for pydantic model handlings"
