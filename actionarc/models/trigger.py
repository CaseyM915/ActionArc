"""Trigger definitions used by ActionArc models."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TriggerDefinition:
    """Describes the trigger configured for an Arc."""

    type: str
    config: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TriggerDefinition":
        """Create a trigger definition from persisted Arc data."""
        return cls(
            type=data["type"],
            config=data.get("config", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the trigger definition to persisted Arc data."""
        return {
            "type": self.type,
            "config": self.config,
        }