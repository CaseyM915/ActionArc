"""ActionArc entry point."""

from actionarc.components.builtin import register_builtin_components
from actionarc.components.registry import ComponentRegistry
from actionarc.engine.runner import ArcRunner
from actionarc.storage.arc_store import ArcStore


def main() -> None:
    registry = ComponentRegistry()
    register_builtin_components(registry)

    arc = ArcStore().load("data/arcs/example_arc.json")
    result = ArcRunner(registry).run(arc)

    print(result)


if __name__ == "__main__":
    main()