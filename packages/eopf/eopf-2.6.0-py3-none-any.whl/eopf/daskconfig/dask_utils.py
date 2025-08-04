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
import gc
from asyncio import CancelledError
from functools import wraps
from typing import Any, Callable, Optional

import dask
from dask.array import Array
from distributed import Client, Future, as_completed, get_client

from eopf.common.file_utils import AnyPath
from eopf.config.config import EOConfiguration
from eopf.daskconfig import ClusterType
from eopf.daskconfig.dask_context_manager import DaskContext
from eopf.exceptions.errors import DaskComputingError
from eopf.logging.log import EOLogging


def init_from_eo_configuration() -> DaskContext:
    logger = EOLogging().get_logger("eopf.daskconfig.dask_utils")
    conf = EOConfiguration()
    # init defaults
    cluster_config = {}
    auth_config = {}
    client_config = {}
    dask_config = {}
    cluster_type = None
    performance_report_file = None

    if conf.has_value("dask_context__cluster_type"):
        cluster_type_str = conf.__getattr__("dask_context__cluster_type")

        if cluster_type_str == ClusterType.ADDRESS.value:
            if not conf.has_value("dask_context__addr"):
                raise Exception("missing addr conf for ADDRESS cluster")
            logger.debug("Initializing an ADDRESS dask cluster")
            return DaskContext(cluster_type_str, address=conf.__getattr__("dask_context__addr"))
        else:
            for c in conf.param_list_available:
                if c.startswith("dask_context__cluster_config__"):
                    if c.startswith("dask_context__cluster_config__auth__"):
                        auth_config[c.replace("dask_context__cluster_config__auth__", "")] = conf.__getattr__(c)
                    else:
                        cluster_config[c.replace("dask_context__cluster_config__", "")] = conf.__getattr__(c)
                if c.startswith("dask_context__client_config__"):
                    client_config[c.replace("dask_context__client_config__", "")] = conf.__getattr__(c)
        cluster_type = ClusterType(cluster_type_str)
    for c in conf.param_list_available:
        if c.startswith("dask_context__client_config__"):
            client_config[c.replace("dask_context__client_config__", "")] = conf.__getattr__(c)
        if c.startswith("dask_context__dask_config__"):
            dask_config[c.replace("dask_context__dask_config__", "")] = conf.__getattr__(c)
        if c == "dask_context__performance_report_file":
            performance_report_file = conf.__getattr__(c)

    if len(client_config) != 0:
        logger.debug(f"Initialising a client with conf : {client_config} ")
    else:
        logger.debug("Initialising a client without conf")

    if len(auth_config) > 0:
        cluster_config["auth"] = auth_config

    return DaskContext(
        cluster_type=cluster_type,
        client_config=client_config,
        cluster_config=cluster_config,
        dask_config=dask_config,
        performance_report_file=performance_report_file,
    )


def remote_dask_cluster_decorator(config: dict[Any, Any]) -> Any:
    """Wrapper function used to setup a remote dask cluster and run the wrapped function on it

    Parameters
    ----------
    config: Dict
        dictionary with dask cluster configuration parameters

    Returns
    ----------
    Any: the return of the wrapped function

    Examples
    --------
    >>> dask_config = {
    ...    "cluster_type": "gateway",
    ...    "cluster_config": {
    ...        "address": "http://xxx.xxx.xxx.xxx/services/dask-gateway",
    ...        "auth": {
    ...            "auth": "jupyterhub",
    ...            "api_token": "xxxxxxxxxxxxxx"
    ...        },
    ...        "image": "registry.eopf.copernicus.eu/cpm/eopf-cpm:feat-create-docker-image",
    ...        "worker_memory": 4,
    ...        "n_workers" : 8
    ...    },
    ...    "client_config": {
    ...        "timeout" : "320s"
    ...    }
    ... }
    ...
    >>> @remote_dask_cluster_decorator(dask_config)
    >>> def convert_to_native_python_type():
    ...     safe_store = EOSafeStore("data/olci.SEN3")
    ...     nc_store = EONetCDFStore("data/olci.nc")
    ...     convert(safe_store, nc_store)
    """
    logger = EOLogging().get_logger("eopf.daskconfig.dask_utils")

    def wrap_outer(fn: Callable[[Any, Any], Any]) -> Any:
        @wraps(fn)
        def wrap_inner(*args: Any, **kwargs: Any) -> Any:
            with DaskContext(
                cluster_type=ClusterType.GATEWAY,
                cluster_config=config["cluster_config"],
                client_config=config["client_config"],
            ) as ctx:  # noqa
                if ctx.client is not None:
                    logger.info(f"Dask dashboard address: {ctx.client.dashboard_link}")
                return fn(*args, **kwargs)

        return wrap_inner

    return wrap_outer


def local_dask_cluster_decorator(cluster_config: dict[Any, Any]) -> Any:
    """
    Wrapper function used to setup a local dask cluster and run the wrapped function on it
    This wrapper can run with / without a pre-defined configuration.
    Note that the call of the wrapped function must be made inside
    the if __name__ == "__main__" if used in python standalone programs,
    this is not required for dynamic environments like IPython.

    Parameters
    ----------
    cluster_config: Dict
        dictionary with dask cluster configuration parameters

    Returns
    ----------
    Any: the return of the wrapped function

    Examples
    --------
    ... "cluster_config": {
    ...     "n_workers": 2,
    ...     "worker_memory": "2GB",
    ...     "threads_per_worker" : 2
    ... }
    ...
    ... @local_dask_cluster_decorator(config=cluster_config)
    ... def conv_to_zarr(input_prod, output_prod):
    ...     ss = EOSafeStore(input_prod)
    ...     zs = EOZarrStore(output_prod)
    ...     convert(ss, zs)
    ...
    ... if __name__ == "__main__":
    ...     input_path = <...>
    ...     output_path = <...>
    ...     conv_to_zarr(input_path, output_path)
    """
    logger = EOLogging().get_logger("eopf.daskconfig.dask_utils")

    def wrap_outer(fn: Callable[[Any, Any], Any]) -> Any:
        @wraps(fn)
        def wrap_inner(*args: Any, **kwargs: Any) -> Any:
            n_workers = cluster_config.get("n_workers", 4)
            memory_limit = cluster_config.get("memory_limit", "8GB")
            worker_threads = cluster_config.get("threads_per_worker", 2)
            with DaskContext(
                cluster_type=ClusterType.LOCAL,
                cluster_config={
                    "n_workers": n_workers,
                    "threads_per_worker": worker_threads,
                    "memory_limit": memory_limit,
                },
            ) as ctx:  # noqa
                if ctx.client is not None:
                    logger.info(f"Dask dashboard address: {ctx.client.dashboard_link}")
                return fn(*args, **kwargs)

        return wrap_inner

    return wrap_outer


EOConfiguration().register_requested_parameter(
    "dask_utils__compute__step",
    9999,
    True,
    description="Number of dask future computed simultaneously in dask_utils",
)

EOConfiguration().register_requested_parameter(
    "dask_utils__timeout",
    300,
    True,
    description="Default timeout on a submitted task",
)

EOConfiguration().register_requested_parameter(
    "dask_utils__retries",
    3,
    True,
    description="Default number of retries",
)


class FutureLike:
    """Simulates a Dask Future when no distributed client exists."""

    def __init__(self, value: Any) -> None:
        self.value = value

    def result(self, timeout: Optional[int] = None) -> Any:
        """Returns the computed result immediately."""
        return self.value

    def done(self) -> bool:
        """A FakeFuture is always 'done' since it's computed synchronously."""
        return True

    def cancel(self) -> bool:
        """Mimic cancel method (does nothing here)."""
        return False

    def exception(self) -> None:
        """No exception handling needed for immediate computation."""
        return None

    def __repr__(self) -> str:
        return f"FutureLike({self.value})"


def compute(*args: Any, **kwargs: Any) -> list[FutureLike | Future]:
    """
    Custom compute function that checks if a Dask client is available.
    If a client is available, it uses client.compute.
    Otherwise, it falls back to dask.compute and provides FutureLike object mimicking the future api
    """
    # Check if a Dask client is already instantiated
    logger = EOLogging().get_logger("eopf.daskconfig.dask_utils")
    collection = args[0] if isinstance(args[0], (list, tuple)) else [args[0]]
    client = get_distributed_client()
    priority = kwargs.pop("priority", None)
    if client is None:
        logger.debug("Computing without client ")
        return [FutureLike(v) for v in dask.compute(collection, **kwargs)]
    else:
        logger.debug(f"Computing using client {id(client)}")
        fu = []
        for idx, d in enumerate(collection):
            priority_used = 10 * idx if priority is None else priority
            logger.debug(f"Sending {d} to the client with priority {priority_used}")
            fu.append(
                client.compute(
                    d,
                    priority=priority_used,
                    retries=kwargs.pop("retries", EOConfiguration()["dask_utils__retries"]),
                    **kwargs,
                ),
            )
        return fu


def wait_and_get_results(
    futures: list[FutureLike | Future],
    cancel_at_first_error: Optional[bool] = True,
    **kwargs: Any,
) -> list[Any]:
    """
    Function to wait on the futures list and return the results.
    Order is kept.
    FutureLike objects are accepted

    """
    logger = EOLogging().get_logger("eopf.daskconfig.dask_utils")
    indexed_futures = {i: f for i, f in enumerate(futures)}  # Store index-future mapping
    results = [None] * len(futures)  # Pre-allocate results list
    real_futures = {i: f for i, f in indexed_futures.items() if isinstance(f, Future)}
    fake_futures = {i: f for i, f in indexed_futures.items() if isinstance(f, FutureLike)}
    has_failure = False

    # Process real Dask Futures as they complete
    if len(real_futures) != 0:
        timeout = kwargs.pop("timeout", EOConfiguration()["dask_utils__timeout"])
        client = get_distributed_client()
        if client is not None:
            for future in as_completed(real_futures.values(), timeout=timeout):
                index = next(i for i, f in real_futures.items() if f == future)  # Find correct index
                if isinstance(index, int) and int is not None:
                    try:
                        results[index] = future.result()
                        del real_futures[index]
                    except CancelledError as e:
                        logger.warning(f"Task {future} has been cancelled : {e}")
                        has_failure = True
                    except Exception as e:
                        logger.warning(f"Task {future} is in error : {e}")
                        if cancel_at_first_error:
                            client.cancel(real_futures)
                        has_failure = True
            gc.collect()
        else:
            raise DaskComputingError("Dask future computation requested but no Client available !!!!")

    if has_failure:
        raise DaskComputingError(f"Error occurred during dask computation on {futures}")

    # Process FakeFutures (already done)
    for index, future in fake_futures.items():
        results[index] = future.result()
        gc.collect()

    return results  # Returns results in correct order


def cancel_futures(
    futures: list[FutureLike | Future],
    **kwargs: Any,
) -> None:
    """
    Function to cancel the futures list and return the results.
    Order is kept.
    FutureLike objects are accepted

    """

    indexed_futures = {i: f for i, f in enumerate(futures)}  # Store index-future mapping
    real_futures = {i: f for i, f in indexed_futures.items() if isinstance(f, Future)}

    # Process real Dask Futures as they complete
    if len(real_futures) != 0:
        client = get_distributed_client()
        if client is not None:
            client.cancel(real_futures, force=kwargs.get("force", False))
        else:
            raise DaskComputingError("Dask future cancellation requested but no Client available !!!!")

        gc.collect()


def scatter(data: Array, **kwargs: Any) -> Future | Array:
    logger = EOLogging().get_logger("eopf.daskconfig.dask_utils")
    client = get_distributed_client()

    if client is not None:
        logger.debug(f"scattering on client client {id(client)} with options : {kwargs}")
        timeout = kwargs.pop("timeout", EOConfiguration()["dask_utils__timeout"])
        return client.scatter(data, timeout=timeout, **kwargs)
    else:
        # No client, can't future the data
        logger.debug("No client in scatter : returning data itself ")
        return data


def get_distributed_client() -> Client | None:
    """
    Get the client, None if not available
    """
    try:
        client = get_client()
    except Exception:
        client = None
    return client


def is_distributed() -> bool:
    """
    Get the distributed status
    Returns True only if a distributed client is available and un running status

    """
    logger = EOLogging().get_logger("eopf.daskconfig.dask_utils")
    client = get_distributed_client()

    if client is not None and client.status == "running":
        logger.debug(f"Distributed client detected : {id(client)}")
        return True
    else:
        # No client, can't future the data
        logger.debug("No distributed client detected")
        return False


def is_worker_reachable(a_path: AnyPath) -> bool:
    """
    Test if an AnyPath is reachable from the workers
    This is primarily to test if it is a shared folder or an S3 folder

    warning ; Do this test after creating the daskcontext/client or it will only test local access to the path

    Parameters
    ----------
    a_path: AnyPath
        AnyPath to test access to

    Returns
    ----------
    bool : reachable or not


    """
    logger = EOLogging().get_logger("eopf.daskconfig.dask_utils")
    if is_distributed():
        client = get_distributed_client()
        if client is not None:
            global_result = True
            results = client.run(a_path.exists)
            for worker, is_reachable in results.items():
                if is_reachable:
                    logger.debug(f"Path {a_path} reachable for {worker}")
                else:
                    global_result = False
                    logger.debug(f"Path {a_path} NOT reachable for {worker}")
            return global_result
        else:
            return a_path.exists()
    else:
        return a_path.exists()
