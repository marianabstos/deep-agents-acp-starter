from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


PermissionStatus = Literal["allow", "ask", "deny"]


@dataclass(frozen=True)
class PermissionDecision:
    status: PermissionStatus
    reason: str | None = None
