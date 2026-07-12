"""Execution result models."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ArcRunStatus(StrEnum):
    NOT_TRIGGERED = "not_triggered"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(slots=True)
class TriggerResult:
    matched: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ActionResult:
    succeeded: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ArcRunResult:
    arc_id: str
    status: ArcRunStatus
    trigger: TriggerResult
    actions: list[ActionResult] = field(default_factory=list)