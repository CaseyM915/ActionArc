"""Coordinate ActionArc engine operations."""

from collections.abc import Callable
from threading import Thread

from actionarc.engine.results import ArcRunResult
from actionarc.engine.runner import ArcRunner
from actionarc.engine.scheduler import ArcScheduler
from actionarc.models import Arc


class EngineController:
    """Control Arc execution and scheduler lifecycle."""

    def __init__(
        self,
        runner: ArcRunner,
        arcs: list[Arc],
        on_result: Callable[[Arc, ArcRunResult], None] | None = None,
    ):
        self.runner = runner
        self.arcs = arcs
        self.scheduler = ArcScheduler(runner, on_result)
        self._scheduler_thread: Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._scheduler_thread is not None and self._scheduler_thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return

        self._scheduler_thread = Thread(
            target=self.scheduler.run_forever,
            args=(self.arcs,),
            daemon=True,
            name="ActionArcScheduler",
        )
        self._scheduler_thread.start()

    def stop(self) -> None:
        if not self.is_running:
            return

        self.scheduler.stop()
        self._scheduler_thread.join()
        self._scheduler_thread = None

    def run_arc(self, arc: Arc) -> ArcRunResult:
        result = self.runner.run(arc)
        self.scheduler.publish_result(arc, result)
        return result

    def run_arc_by_id(self, arc_id: str) -> ArcRunResult:
        arc = next((arc for arc in self.arcs if arc.id == arc_id), None)

        if arc is None:
            raise ValueError(f"Arc not found: {arc_id}")

        return self.run_arc(arc)