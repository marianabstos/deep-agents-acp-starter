from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from deep_agents_acp_starter.domain.events import HarnessEvent
from deep_agents_acp_starter.domain.models import TurnRequest


class AgentRuntimePort(Protocol):
    async def stream_turn(self, request: TurnRequest) -> AsyncIterator[HarnessEvent]:
        ...
