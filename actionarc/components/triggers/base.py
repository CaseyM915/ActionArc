"""Base trigger class."""

from abc import ABC, abstractmethod

from actionarc.engine.context import RunContext
from actionarc.engine.results import TriggerResult


class Trigger(ABC):
    """Base class for all ActionArc triggers."""

    component_id: str

    @abstractmethod
    def evaluate(self, context: RunContext) -> TriggerResult:
        """Evaluate whether the trigger condition has been met."""
        raise NotImplementedError