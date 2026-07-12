"""Component registry."""

from typing import Any

from actionarc.components.actions.base import Action
from actionarc.components.triggers.base import Trigger


class ComponentRegistry:
    """Registers and creates ActionArc components."""

    def __init__(self):
        self._triggers: dict[str, type[Trigger]] = {}
        self._actions: dict[str, type[Action]] = {}

    def register_trigger(self, trigger: type[Trigger]) -> None:
        self._triggers[trigger.component_id] = trigger

    def register_action(self, action: type[Action]) -> None:
        self._actions[action.component_id] = action

    def create_trigger(self, component_id: str, config: dict[str, Any]) -> Trigger:
        return self._triggers[component_id]()

    def create_action(self, component_id: str, config: dict[str, Any]) -> Action:
        return self._actions[component_id](config)