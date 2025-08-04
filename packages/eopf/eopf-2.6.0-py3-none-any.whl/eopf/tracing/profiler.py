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
from cProfile import Profile
from functools import wraps
from pathlib import Path
from pstats import Stats
from typing import Any, Callable, Optional, Union

from dask.distributed import performance_report

from eopf.daskconfig import ClusterType, DaskContext
from eopf.exceptions import DaskProfilerError, SingleThreadProfilerError
from eopf.exceptions.warnings import DaskProfilerHtmlDisplayNotWorking


def _in_ipynb() -> bool:
    """Determines if the code calling the function is run in IPython

    Returns
    ----------
    bool    True if code is run in IPython interactive shell, False otherwise
    """
    try:
        from IPython import get_ipython

        if "IPKernelApp" not in get_ipython().config:  # pragma: no cover
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True


def dask_profiler(
    n_workers: int = 2,
    threads_per_worker: int = 2,
    report_name: Union[str, Path] = "dask-report.html",
    display_report: bool = True,
    enable: bool = True,
    mem_limit: str = "8GB",
) -> Any:
    """Wrapper function used to perform multi-threaded profiling (dask) on code running in dask

    Parameters
    ----------
    n_workers: int
        number of workers to be run with dask
    threads_per_worker: int
        number of threads per dask worker
    report_name: str
        name of dask html generated report
    display_report: bool
        whether to display the report as embedded html in interactive console such as IPython
    enable: bool
        enable or disable the stats gathering
    mem_limit: str
        dask memory limit

    Raises
    ----------
    DaskProfilerError
        When the dask_profiler raises any error
    DaskProfilerHtmlDisplayNotWorking
        When the report display of the dask_profiler is not working

    Returns
    ----------
    Any: the return of the wrapped function

    Examples
    --------
    >>> @dask_profiler(n_workers=4, threads_per_worker=2, report_name="experiment1.html", display=False)
    >>> def convert_to_native_python_type():
    ...     safe_store = EOSafeStore("data/olci.SEN3")
    ...     nc_store = EONetCDFStore("data/olci.nc")
    ...     convert(safe_store, nc_store)
    ...
    >>> @dask_profiler()
    >>> def convert_to_native_python_type():
    ...     safe_store = EOSafeStore("data/olci.SEN3")
    ...     nc_store = EONetCDFStore("data/olci.nc")
    ...     convert(safe_store, nc_store)
    """

    def wrap_outer(fn: Callable[[Any, Any], Any]) -> Any:
        @wraps(fn)
        def wrap_inner(*args: Any, **kwargs: Any) -> Any:
            # if not enabled just call the function as it was not wrapped
            if not enable:
                return fn(*args, **kwargs)

            # determine if a specific dask configuration is given
            if n_workers and n_workers > 0 and threads_per_worker and threads_per_worker > 0:
                dask_specific_config = True
            else:
                dask_specific_config = False

            try:
                # start a dask cluster with given specification
                if dask_specific_config:
                    with DaskContext(
                        cluster_type=ClusterType.LOCAL,
                        cluster_config={
                            "n_workers": n_workers,
                            "threads_per_worker": threads_per_worker,
                            "memory_limit": mem_limit,
                        },
                        performance_report_file=report_name,
                    ):
                        result = fn(*args, **kwargs)
                else:
                    # wrap the actual execution of dask function with perfomance monitoring
                    with performance_report(filename=report_name):
                        result = fn(*args, **kwargs)

            except Exception as e:
                raise DaskProfilerError(f"Exception encountered: {e}")

            # display the html report if wanted and possible
            if display_report and _in_ipynb():
                from IPython.display import HTML, display

                try:
                    with open(report_name, mode="r") as f:
                        html_page = f.read()
                    display(HTML(html_page))
                except Exception as e:
                    raise DaskProfilerHtmlDisplayNotWorking(f"Report display faillure reason: {e}")

            return result

        return wrap_inner

    return wrap_outer


def single_thread_profiler(
    report_name: Optional[Union[Path, str]] = None,
    enable: bool = True,
    mem_limit: str = "8GB",
) -> Any:
    """Decorator function used to perform single threaded profiling (cProfile) on code running in dask

    Parameters
    ----------
    report_name: str
        name of cProfile.Stats dump file
    enable: bool
        enable or disable the stats gathering
    mem_limit: str
        dask memory limit

    Raises
    ----------
    SingleThreadProfilerError
        When the single_thread_profiler raises any error

    Returns
    ----------
    Any: a pstat.Stats object ordered by n_calls

    Examples
    --------
    >>> @single_thread_profiler("stats.dump")
    >>> def convert_to_native_python_type():
    ...     safe_store = EOSafeStore("data/olci.SEN3")
    ...     nc_store = EONetCDFStore("data/olci.nc")
    ...     convert(safe_store, nc_store)
    ...
    >>> stats = convert_to_native_python_type()
    >>> stats.stats.strip_dirs().print_stats()

    Can be used together with dask_reporter decorator as long as it does not register_requested_parameter a
    specific dask configuration:
    >>> @single_thread_profiler("stats.dump")
    >>> @dask_profiler(report_name="dask_out.html")
    >>> def convert_to_native_python_type():
    ...     safe_store = EOSafeStore("data/olci.SEN3")
    ...     nc_store = EONetCDFStore("data/olci.nc")
    ...     convert(safe_store, nc_store)

    Notes
    -----
    In IPython environments one can use snakeviz to obtain a graphical representation of the returned Stats:
    >>> pip install snakeviz
    >>> %load_ext snakeviz
    >>> %snakeviz stats

    See Also
    -------
    pstats.Stats
    """

    def wrap_outer(fn: Callable[[Any, Any], Any]) -> Any:
        @wraps(fn)
        def wrap_inner(*args: Any, **kwargs: Any) -> Stats:
            # if not enabled just call the function as it was not wrapped
            if not enable:
                return fn(*args, **kwargs)

            try:
                # start a dask cluster with 1 worker and 1 thread
                with DaskContext(
                    cluster_type=ClusterType.LOCAL,
                    cluster_config={
                        "n_workers": 1,
                        "processes": False,
                        "threads_per_worker": 1,
                        "memory_limit": mem_limit,
                    },
                ):
                    # wrap the actual execution of dask function with perfomance monitoring
                    profiler = Profile()
                    profiler.enable()
                    fn(*args, **kwargs)
                    profiler.disable()

                    # extract, print and return stats
                    stats: Stats = Stats(profiler).sort_stats("ncalls")
                    if report_name:
                        stats.dump_stats(report_name)
                    stats.print_stats()

                    return stats

            except Exception as e:
                raise SingleThreadProfilerError(f"Exception encountered: {e}")

        return wrap_inner

    return wrap_outer
