from typing import TYPE_CHECKING, Any, Tuple

from dask.typing import Key
from distributed import SchedulerPlugin

if TYPE_CHECKING:
    from distributed.scheduler import TaskStateState as SchedulerTaskStateState


class FailureMonitorPlugin(SchedulerPlugin):
    """
    Dask scheduler plugin to detect failed task

    """

    def __init__(self) -> None:
        self.failed_tasks: list[Tuple[Key, Any]] = []

    def transition(
        self,
        key: Key,
        start: "SchedulerTaskStateState",
        finish: "SchedulerTaskStateState",
        *args: Any,
        stimulus_id: str,
        **kwargs: Any,
    ) -> None:
        """ """

        if finish == "erred":
            exception = kwargs.get("exception", None)
            self.failed_tasks.append((key, exception))

    def get_failed_tasks(self) -> list[Tuple[Key, Any]]:
        """Return the list of failed tasks."""
        return self.failed_tasks
