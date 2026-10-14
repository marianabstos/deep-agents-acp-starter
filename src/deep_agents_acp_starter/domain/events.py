from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


HarnessEventType = Literal[
    "session.started",
    "turn.started",
    "context.collected",
    "model.started",
    "model.token",
    "tool.requested",
    "permission.requested",
    "permission.resolved",
    "tool.started",
    "tool.finished",
    "turn.finished",
    "turn.failed",
]


@dataclass(frozen=True)
class HarnessEvent:
    type: HarnessEventType
    data: dict[str, Any] = field(default_factory=dict)
