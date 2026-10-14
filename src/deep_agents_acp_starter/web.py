from __future__ import annotations

import json
import os
import uuid
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from deep_agents_acp_starter.agent import MODELS, build_deep_agent


ROOT = Path(__file__).resolve().parents[2]
WEB_DIR = ROOT / "web"

app = FastAPI(title="Deep Agents Web")
app.mount("/assets", StaticFiles(directory=WEB_DIR), name="assets")


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    model: str | None = None


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/status")
async def status() -> dict[str, Any]:
    return {
        "name": "Deep Agents Starter",
        "workspace": str(ROOT),
        "model": os.environ.get("DEFAULT_MODEL", MODELS[0]["value"]),
        "models": MODELS,
        "langsmith_project": os.environ.get("LANGSMITH_PROJECT", "deep-agents-acp-starter"),
        "surfaces": ["VS Code ACP", "Local Web", "CLI"],
    }


@app.post("/api/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    session_id = request.session_id or uuid.uuid4().hex

    async def event_stream() -> AsyncIterator[str]:
        yield _event("session", {"session_id": session_id})
        yield _event("stage", {"name": "Context", "status": "active"})

        agent = build_deep_agent(model=request.model)
        config = {"configurable": {"thread_id": session_id}}
        payload = {"messages": [{"role": "user", "content": request.message}]}

        yielded_text = False
        try:
            async for chunk in agent.astream(payload, config=config, stream_mode="updates"):
                text = _extract_text(chunk)
                if text:
                    yielded_text = True
                    yield _event("stage", {"name": "Model", "status": "active"})
                    yield _event("token", {"text": text})

                tools = _extract_tools(chunk)
                for tool_name in tools:
                    yield _event("tool", {"name": tool_name})

            if not yielded_text:
                yield _event(
                    "token",
                    {
                        "text": "Terminei a execução, mas esta versão inicial da Web UI não recebeu texto estruturado do agente.",
                    },
                )

            yield _event("stage", {"name": "Done", "status": "complete"})
            yield _event("done", {"session_id": session_id})
        except Exception as exc:
            yield _event("error", {"message": str(exc)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _event(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _extract_text(chunk: Any) -> str:
    pieces: list[str] = []
    _walk(chunk, pieces)
    return "".join(pieces)


def _walk(value: Any, pieces: list[str]) -> None:
    if isinstance(value, dict):
        if "messages" in value and isinstance(value["messages"], list):
            for message in value["messages"]:
                content = getattr(message, "content", None)
                if isinstance(content, str):
                    pieces.append(content)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            pieces.append(str(item.get("text", "")))

        for child in value.values():
            _walk(child, pieces)
    elif isinstance(value, list):
        for child in value:
            _walk(child, pieces)


def _extract_tools(chunk: Any) -> list[str]:
    tools: list[str] = []
    _walk_tools(chunk, tools)
    return tools


def _walk_tools(value: Any, tools: list[str]) -> None:
    if isinstance(value, dict):
        name = value.get("name") or value.get("tool")
        if isinstance(name, str) and name not in tools:
            tools.append(name)

        for child in value.values():
            _walk_tools(child, tools)
    elif isinstance(value, list):
        for child in value:
            _walk_tools(child, tools)
