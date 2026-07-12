"""Core Arc models."""

from dataclasses import dataclass, field
from typing import Any

from actionarc.models.action import ActionDefinition
from actionarc.models.trigger import TriggerDefinition


@dataclass(slots=True)
class ScheduleDefinition:
    """Describes when an Arc should be evaluated."""

    type: str
    config: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScheduleDefinition":
        """Create a schedule definition from persisted Arc data."""
        schedule_type = data["type"]

        return cls(
            type=schedule_type,
            config={
                key: value
                for key, value in data.items()
                if key != "type"
            },
        )


@dataclass(slots=True)
class Arc:
    """The primary automation object managed by ActionArc."""

    id: str
    name: str
    trigger: TriggerDefinition
    actions: list[ActionDefinition]
    schedule: ScheduleDefinition
    description: str = ""
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Arc":
        """Create an Arc from persisted Arc data."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            schedule=ScheduleDefinition.from_dict(data["schedule"]),
            trigger=TriggerDefinition.from_dict(data["trigger"]),
            actions=[
                ActionDefinition.from_dict(action_data)
                for action_data in data.get("actions", [])
            ],
        )