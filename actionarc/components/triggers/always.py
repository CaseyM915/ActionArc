"""Trigger that always matches."""

from actionarc.components.triggers.base import Trigger
from actionarc.engine.context import RunContext
from actionarc.engine.results import TriggerResult


class AlwaysTrigger(Trigger):
    """Always reports that its trigger condition matched."""

    component_id = "always"
    def evaluate(self, context: RunContext) -> TriggerResult:
        return TriggerResult(matched=True, message="Trigger matched.")