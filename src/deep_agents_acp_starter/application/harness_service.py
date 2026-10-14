from __future__ import annotations

from collections.abc import AsyncIterator

from deep_agents_acp_starter.application.ports import AgentRuntimePort
from deep_agents_acp_starter.domain.events import HarnessEvent
from deep_agents_acp_starter.domain.models import TurnRequest


class HarnessService:
    def __init__(self, runtime: AgentRuntimePort) -> None:
        self._runtime = runtime

    async def stream_turn(self, request: TurnRequest) -> AsyncIterator[HarnessEvent]:
        yield HarnessEvent("turn.started", {"session_id": request.session_id})

        try:
            async for event in self._runtime.stream_turn(request):
                yield event
        except Exception as exc:
            yield HarnessEvent("turn.failed", {"message": str(exc)})
            return

        yield HarnessEvent("turn.finished", {"session_id": request.session_id})
