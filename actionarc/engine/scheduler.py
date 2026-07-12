"""Schedule and execute enabled Arcs."""

from collections.abc import Callable
from threading import Event
from time import monotonic

from actionarc.engine.results import ArcRunResult
from actionarc.engine.runner import ArcRunner
from actionarc.models import Arc


class ArcScheduler:
    """Run enabled interval-based Arcs when they become due."""

    def __init__(
        self,
        runner: ArcRunner,
        on_result: Callable[[Arc, ArcRunResult], None] | None = None,
    ):
        self.runner = runner
        self.on_result = on_result
        self.stop_event = Event()
        self._last_runs: dict[str, float] = {}

    def run_forever(self, arcs: list[Arc], check_interval: float = 1.0) -> None:
        self.stop_event.clear()

        while not self.stop_event.is_set():
            for arc in arcs:
                if self.is_due(arc):
                    result = self.runner.run(arc)
                    self._last_runs[arc.id] = monotonic()
                    self.publish_result(arc, result)

            self.stop_event.wait(check_interval)

    def stop(self) -> None:
        self.stop_event.set()

    def is_due(self, arc: Arc) -> bool:
        if not arc.enabled or arc.schedule.type != "interval":
            return False

        seconds = arc.schedule.config.get("seconds")

        if not isinstance(seconds, (int, float)) or seconds <= 0:
            return False

        last_run = self._last_runs.get(arc.id)
        return last_run is None or monotonic() - last_run >= seconds

    def publish_result(self, arc: Arc, result: ArcRunResult) -> None:
        if self.on_result:
            self.on_result(arc, result)