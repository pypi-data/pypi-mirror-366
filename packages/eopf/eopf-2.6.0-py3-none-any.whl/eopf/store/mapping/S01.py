from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import numpy as np
import numpy.typing as nptyping
import pandas as pd

from eopf import EOContainer, EOGroup, EOLogging, EOProduct, EOVariable
from eopf.common.file_utils import AnyPath
from eopf.store.mapping_manager import EOPFAbstractMappingManager
from eopf.store.safe import EOSafeFinalize

# mypy: disable-error-code="union-attr"


def build_coordinates(additional_info: Dict[str, Any]) -> Tuple[Any, Any, Any, Any, Any]:
    """Build coordinates from metadata for Sentinel-1 products."""

    azimuth_time = pd.date_range(
        start=additional_info["product_first_line_utc_time"],
        end=additional_info["product_last_line_utc_time"],
        periods=additional_info["number_of_lines"],
    )
    pixel = np.arange(0, additional_info["number_of_samples"], dtype=int)
    line = np.arange(0, additional_info["number_of_lines"], dtype=int)
    ground_range = np.linspace(
        0,
        additional_info["range_pixel_spacing"] * (additional_info["number_of_samples"] - 1),
        additional_info["number_of_samples"],
    )
    slant_range_time = np.linspace(
        additional_info["image_slant_range_time"],
        additional_info["image_slant_range_time"]
        + (additional_info["number_of_samples"] - 1) / additional_info["range_sampling_rate"],
        additional_info["number_of_samples"],
    )
    return azimuth_time, pixel, line, ground_range, slant_range_time


def prepare_quality_noise(
    product: Union[EOProduct, EOContainer],
    range_coord: nptyping.NDArray[Any],
    range_coord_name: str,
) -> None:
    # quality/noise_azimuth
    if "noise_azimuth" in product.quality:
        noise_azimuth = product.quality.noise_azimuth.data.compute()
        noise_azimuth_lut_with_coords = noise_azimuth.noise_azimuth_lut.assign_coords(
            first_azimuth_time=noise_azimuth.first_azimuth_line,
            last_azimuth_time=noise_azimuth.last_azimuth_line,
            first_range_sample=noise_azimuth.first_range_sample,
            last_range_sample=noise_azimuth.last_range_sample,
        )
        product.quality["noise_azimuth"] = EOGroup(
            variables=dict(
                noise_azimuth_lut=EOVariable(
                    data=noise_azimuth_lut_with_coords,
                    attrs=noise_azimuth.noise_azimuth_lut.attrs,
                ),
            ),
            attrs=noise_azimuth.attrs,
        )

    # quality/noise_range
    idx_mask = product.quality.noise_range.noise_range_lut.data.coords["pixel"].values
    noise_range_ground_range_time = np.where(idx_mask >= 0, range_coord[idx_mask], -1)
    coords = {
        range_coord_name: (("azimuth_time", range_coord_name), noise_range_ground_range_time),
        "pixel": (("azimuth_time", range_coord_name), idx_mask),
    }
    product.quality.noise_range["noise_range_lut"] = EOVariable(
        data=product.quality.noise_range.noise_range_lut.data.assign_coords(coords=coords),
        attrs=product.quality.noise_range.noise_range_lut.attrs,
    )


def build_gcp_variables(
    gcp: EOGroup,
    azimuth_time: Any,
    range_coord: Any,
    range_coord_name: str = "slant_range_time",
) -> Iterable[Tuple[str, EOVariable]]:
    """
    Unstack dimensions in gcp group, in order to convert variables
    from 1D (grid_point) to 2D (azimuth_time, slant_range_time) for GRD.
    """

    # source: https://github.com/bopen/xarray-sentinel, xarray_sentinel/sentinel1.py#L227
    geolocation_grid_points: List[Dict[str, Any]] = [{} for _ in range(gcp.data.sizes["grid_point"])]
    for coord_name, coord_values in gcp.data.coords.items():
        for idx, v in enumerate(coord_values.values):
            geolocation_grid_points[idx].update({coord_name: v})
    for var_name, var_values in gcp.data.items():
        for idx, v in enumerate(var_values.values):
            geolocation_grid_points[idx].update({var_name: v})

    azimuth_time_sel = []
    range_coord_sel = []
    line_set = set()
    pixel_set = set()
    for ggp in geolocation_grid_points:
        if ggp["line"] not in line_set:
            azimuth_time_sel.append(np.datetime64(azimuth_time[ggp["line"]], "ns"))
            line_set.add(ggp["line"])
        if ggp["pixel"] not in pixel_set:
            range_coord_sel.append(range_coord[ggp["pixel"]])
            pixel_set.add(ggp["pixel"])

    shape = (len(azimuth_time_sel), len(range_coord_sel))
    dims = ("azimuth_time", range_coord_name)
    data_vars = {
        "latitude": (dims, np.full(shape, np.nan), gcp.attrs),
        "longitude": (dims, np.full(shape, np.nan), gcp.attrs),
        "height": (dims, np.full(shape, np.nan), gcp.attrs),
        "incidence_angle": (dims, np.full(shape, np.nan), gcp.attrs),
        "elevation_angle": (dims, np.full(shape, np.nan), gcp.attrs),
        "azimuth_time_gcp": (dims, np.full(shape, np.nan), gcp.attrs),
        "slant_range_time_gcp": (dims, np.full(shape, np.nan), gcp.attrs),
    }
    line = sorted(line_set)
    pixel = sorted(pixel_set)
    for ggp in geolocation_grid_points:
        for var_name, var in data_vars.items():
            j = line.index(ggp["line"])
            i = pixel.index(ggp["pixel"])
            var[1][j, i] = ggp[var_name]
    for var_name, var in data_vars.items():  # cannot assign directly a Dataset to an EOGroup
        var1 = var[1].astype(ggp[var_name].dtype)
        eovar = EOVariable(
            data=var1,
            dims=dims,
        )
        yield (
            var_name,
            EOVariable(
                data=eovar.data.assign_coords(
                    {
                        "azimuth_time": [dt.astype("<M8[ns]") for dt in azimuth_time_sel],
                        range_coord_name: range_coord_sel,
                        "line": ("azimuth_time", line),
                        "pixel": (range_coord_name, pixel),
                    },
                ),
                attrs=gcp.attrs,
            ),
        )


def assign_degree_coord_to_doppler_centroid_vars(product: Union[EOProduct, EOContainer]) -> None:
    for var in ("data_dc_polynomial", "geometry_dc_polynomial"):
        if var in product.conditions.doppler_centroid:
            data_var = product.conditions.doppler_centroid[var]
            product.conditions.doppler_centroid[var] = EOVariable(
                data=data_var.data.assign_coords(
                    azimuth_time=("azimuth_time", data_var.data.azimuth_time.data),
                    degree=("degree", list(range(data_var.data.degree.size))[::-1]),
                ),
                attrs=data_var.attrs,
            )
            product.conditions.doppler_centroid[var].coords["azimuth_time"].attrs.update(
                data_var.data.azimuth_time.attrs,
            )
            product.conditions.doppler_centroid[var].coords["degree"].attrs.update(data_var.data.degree.attrs)


def assign_axis_coord_to_orbit_vars(product: Union[EOProduct, EOContainer]) -> None:
    for var in ("position", "velocity"):
        if var in product.conditions.orbit:
            data_var = product.conditions.orbit[var]
            product.conditions.orbit[var] = EOVariable(
                data=data_var.data.assign_coords(
                    azimuth_time=("azimuth_time", data_var.data.azimuth_time.data),
                    axis=("axis", ["x", "y", "z"]),
                ),
                attrs=data_var.attrs,
            )
            product.conditions.orbit[var].coords["azimuth_time"].attrs.update(data_var.data.azimuth_time.attrs)


def assign_range_coord_to_antena_pattern_vars(product: Union[EOProduct, EOContainer]) -> None:
    for var in ("slant_range_time_ap", "elevation_angle", "incidence_angle"):
        if var in product.conditions.antenna_pattern:
            data_var = product.conditions.antenna_pattern[var]
            product.conditions.antenna_pattern[var] = EOVariable(
                data=data_var.data.assign_coords(
                    azimuth_time=("azimuth_time", data_var.data.azimuth_time.data),
                    count=("count", list(range(data_var.data["count"].size))),
                ),
                attrs=data_var.attrs,
            )
            product.conditions.antenna_pattern[var].coords["count"].attrs.update(data_var.data["count"].attrs)
            product.conditions.antenna_pattern[var].coords["azimuth_time"].attrs.update(
                data_var.data.azimuth_time.attrs,
            )


class S01GRHSafeFinalize(EOSafeFinalize):
    """
    Finalize EOSafeStore import for Sentinel-1 GRD products.

    "finalize_function": {
           "module" : "eopf.store.sentineltoolbox_bindings",
           "class" : "S01GRHSafeFinalize"
       }
    """

    def finalize_product(
        self,
        eop: EOProduct,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:
        pass

    def finalize_container(
        self,
        container: EOContainer,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:

        for _, product in container.items():

            additional_info = product.attrs.pop("additional_info")

            # duplicate and merge attributes into subproducts
            product_attrs = {
                "other_metadata": container.attrs["other_metadata"] | product.attrs.get("other_metadata", {}),
                "stac_discovery": container.attrs["stac_discovery"] | product.attrs.get("stac_discovery", {}),
            }
            product_attrs["stac_discovery"]["properties"]["sar:pixel_spacing_range"] = additional_info[
                "range_pixel_spacing"
            ]
            product_attrs["stac_discovery"]["properties"]["sar:pixel_spacing_azimuth"] = additional_info[
                "azimuth_pixel_spacing"
            ]
            product.attrs = product_attrs

            # build coordinates
            azimuth_time, pixel, line, ground_range, _ = build_coordinates(additional_info)

            # measurements/grd
            # There is no straightforward way to assign coordinates to existing variable,
            # so we have to recreate them. The EOVariable.assign_coords shortcut does not
            # operate inplace.
            # https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/619
            data = product.measurements.grd.data.assign_coords(
                azimuth_time=("azimuth_time", azimuth_time),
                line=("azimuth_time", line),
                pixel=("ground_range", pixel),
                ground_range=("ground_range", ground_range),
            )
            chunk_sizes = {
                dim: chunk_size for dim, chunk_size in mapping.get("chunk_sizes", {}).items() if dim in data.coords
            }
            product.measurements["grd"] = EOVariable(
                data=data.chunk(chunk_sizes),
                attrs=product.measurements.grd.attrs,
            )

            prepare_quality_noise(product, ground_range, "ground_range")
            assign_degree_coord_to_doppler_centroid_vars(product)
            assign_axis_coord_to_orbit_vars(product)
            assign_range_coord_to_antena_pattern_vars(product)

            # gcp
            for var_name, eovar in build_gcp_variables(
                product.conditions.gcp,
                azimuth_time,
                ground_range,
                "ground_range",
            ):
                product.conditions.gcp[var_name] = eovar


class S01OCNSafeFinalize(EOSafeFinalize):
    """
    Finalize EOSafeStore import for Sentinel-1 OCN products.

    "finalize_function": {
           "module" : "eopf.store.sentineltoolbox_bindings",
           "class" : "S01OCNSafeFinalize"
       }
    """

    def finalize_product(
        self,
        eop: EOProduct,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:

        pass

    def finalize_container(
        self,
        container: EOContainer,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:

        # duplicate and merge attributes into subproducts
        for _, category in container.items():
            for _, product in category.items():
                product_attrs = {
                    "other_metadata": container.attrs["other_metadata"] | product.attrs.get("other_metadata", {}),
                    "stac_discovery": container.attrs["stac_discovery"] | product.attrs.get("stac_discovery", {}),
                }
                product.attrs = product_attrs


class S01SLCSafeFinalize(EOSafeFinalize):
    """
    Finalize EOSafeStore import for Sentinel-1 SLC products.

    "finalize_function": {
           "module" : "eopf.store.sentineltoolbox_bindings",
           "class" : "S01SLCSafeFinalize"
       }
    """

    def finalize_product(
        self,
        eop: EOProduct,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:

        pass

    def finalize_container(
        self,
        container: EOContainer,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:

        for _, product in container.items():

            additional_info = product.attrs.pop("additional_info")

            # duplicate and merge attributes into subproducts
            product_attrs = {
                "other_metadata": container.attrs["other_metadata"] | product.attrs.get("other_metadata", {}),
                "stac_discovery": container.attrs["stac_discovery"] | product.attrs.get("stac_discovery", {}),
            }
            product.attrs = product_attrs

            # build coordinates
            azimuth_time, pixel, line, _, slant_range_time = build_coordinates(additional_info)

            # measurements/slc
            # There is no straightforward way to assign coordinates to existing variable,
            # so we have to recreate them. The EOVariable.assign_coords shortcut does not
            # operate inplace.
            # https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/619
            data = product.measurements.slc.data.assign_coords(
                azimuth_time=("azimuth_time", azimuth_time),
                line=("azimuth_time", line),
                pixel=("slant_range_time", pixel),
                slant_range_time=("slant_range_time", slant_range_time),
            )
            chunk_sizes = {
                dim: chunk_size for dim, chunk_size in mapping.get("chunk_sizes", {}).items() if dim in data.coords
            }
            product.measurements["slc"] = EOVariable(
                data=data.chunk(chunk_sizes),
                attrs=product.measurements.slc.attrs,
            )

            prepare_quality_noise(product, slant_range_time, "slant_range_time")
            assign_degree_coord_to_doppler_centroid_vars(product)
            assign_axis_coord_to_orbit_vars(product)
            assign_range_coord_to_antena_pattern_vars(product)

            # gcp
            for var_name, eovar in build_gcp_variables(product.conditions.gcp, azimuth_time, slant_range_time):
                product.conditions.gcp[var_name] = eovar


class S01SXWSLCSafeFinalize(S01SLCSafeFinalize):
    """
    Finalize EOSafeStore import for Sentinel-1 SLC TOPSAR products.

    "finalize_function": {
           "module" : "eopf.store.sentineltoolbox_bindings",
           "class" : "S01SXWSLCSafeFinalize"
       }
    """

    def finalize_product(
        self,
        eop: EOProduct,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:

        pass

    def finalize_container(
        self,
        container: EOContainer,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:

        super().finalize_container(
            container=container,
            url=url,
            mapping=mapping,
            mapping_manager=mapping_manager,
            **eop_kwargs,
        )

        logger = EOLogging().get_logger("eopf.s01.safe_finalizer")

        container_data = {}

        for product_name, product in container.items():

            # split into bursts
            burst_info = product.attrs["other_metadata"].pop("burst_info")

            burst_ids = burst_info["burst_id"]
            burst_azimuth_times = burst_info["burst_azimuth_time"]

            for burst_idx, (burst_id, first_azimuth_time_burst) in enumerate(zip(burst_ids, burst_azimuth_times)):

                product_burst_name = f"{product_name}_{burst_id}"

                product_burst_attrs = product.attrs.copy()
                product_burst_attrs["other_metadata"]["burst_id"] = burst_id

                container_data[product_burst_name] = {
                    "attributes": product_burst_attrs,
                    "measurements": {},
                    "conditions": {},
                    "quality": {},
                }

                start_idx, end_idx = (
                    burst_info["lines_per_burst"] * burst_idx,
                    burst_info["lines_per_burst"] * (burst_idx + 1),
                )
                azimuth_time_burst = pd.date_range(
                    start=first_azimuth_time_burst,
                    periods=burst_info["lines_per_burst"],
                    freq=pd.Timedelta(burst_info["azimuth_time_interval"] * 10**9, unit="ns"),
                )

                for var_name, var in product.measurements.items():
                    splitted_data_var = var.data.isel(azimuth_time=slice(start_idx, end_idx))
                    splitted_data_var_retimed = splitted_data_var.assign_coords({"azimuth_time": azimuth_time_burst})
                    container_data[product_burst_name]["measurements"][var_name] = splitted_data_var_retimed

                for group_name, group in product.conditions.items():
                    container_data[product_burst_name]["conditions"].update({group_name: {}})
                    for var_name, var in group.items():
                        container_data[product_burst_name]["conditions"][group_name][var_name] = var.data

                for group_name, group in product.quality.items():
                    container_data[product_burst_name]["quality"].update({group_name: {}})
                    for var_name, var in group.items():
                        try:
                            container_data[product_burst_name]["quality"][group_name][var_name] = var.data
                        except TypeError as err:
                            # TODO
                            logger.error(f"quality/{group_name}/{var_name}\n : {err}")

        # empty eocontainer
        container_keys = list(container.keys())
        for product_name in container_keys:
            del container[product_name]

        # rebuild eocontainer
        for product_burst_name, product_burst_data in container_data.items():
            product = EOProduct(name=product_burst_name)
            product.attrs = product_burst_data["attributes"]
            for var_name, var in product_burst_data["measurements"].items():
                product[f"measurements/{var_name}"] = var
            for group_name, group in product_burst_data["conditions"].items():
                for var_name, var in group.items():
                    product[f"conditions/{group_name}/{var_name}"] = var
            for group_name, group in product_burst_data["quality"].items():
                for var_name, var in group.items():
                    product[f"quality/{group_name}/{var_name}"] = var
            container[product_burst_name] = product
