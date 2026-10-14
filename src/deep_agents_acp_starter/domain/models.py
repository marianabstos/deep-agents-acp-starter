from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkspaceRef:
    root: str


@dataclass(frozen=True)
class Session:
    id: str
    workspace: WorkspaceRef


@dataclass(frozen=True)
class TurnRequest:
    session_id: str
    message: str
    workspace: WorkspaceRef
    model: str | None = None
