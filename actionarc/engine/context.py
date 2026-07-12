"""Execution context shared throughout an Arc run."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RunContext:
    arc_id: str
    data: dict[str, Any] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)