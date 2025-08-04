import gc
from typing import Any

from dask.typing import Key
from distributed import WorkerPlugin
from distributed.worker_state_machine import TaskStateState as WorkerTaskStateState


class AutoGCPlugin(WorkerPlugin):
    """
    Dask worker plugin to automaticcaly garbage collect at end of processing
    """

    def transition(
        self,
        key: Key,
        start: "WorkerTaskStateState",
        finish: "WorkerTaskStateState",
        **kwargs: Any,
    ) -> None:
        """Run GC when tasks move from 'processing' to 'memory' or 'erred'."""
        if start == "processing" and finish in {"memory", "erred"}:
            gc.collect()
