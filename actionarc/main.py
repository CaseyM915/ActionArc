"""ActionArc entry point."""

from datetime import datetime
from time import sleep

from actionarc.components.builtin import register_builtin_components
from actionarc.components.registry import ComponentRegistry
from actionarc.engine.controller import EngineController
from actionarc.engine.results import ArcRunResult
from actionarc.engine.runner import ArcRunner
from actionarc.models import Arc
from actionarc.storage.arc_store import ArcStore


def print_result(arc: Arc, result: ArcRunResult) -> None:
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {arc.name} | {result.status.value}")


def main() -> None:
    registry = ComponentRegistry()
    register_builtin_components(registry)

    arc = ArcStore().load("data/arcs/example_arc.json")
    controller = EngineController(ArcRunner(registry), [arc], print_result)

    print("ActionArc engine started. Press Ctrl+C to stop.")
    controller.start()

    try:
        while controller.is_running:
            sleep(0.25)
    except KeyboardInterrupt:
        controller.stop()
        print("\nActionArc engine stopped.")


if __name__ == "__main__":
    main()