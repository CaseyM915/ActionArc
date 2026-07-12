"""Base action class."""

from abc import ABC, abstractmethod

from actionarc.engine.context import RunContext
from actionarc.engine.results import ActionResult


class Action(ABC):
    """Base class for all ActionArc actions."""

    component_id: str

    @abstractmethod
    def execute(self, context: RunContext) -> ActionResult:
        """Execute the action."""
        raise NotImplementedError