"""Register components included with ActionArc."""

from actionarc.components.actions.write_file import WriteFileAction
from actionarc.components.registry import ComponentRegistry
from actionarc.components.triggers.always import AlwaysTrigger


def register_builtin_components(registry: ComponentRegistry) -> None:
    registry.register_trigger(AlwaysTrigger)
    registry.register_action(WriteFileAction)