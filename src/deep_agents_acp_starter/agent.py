from __future__ import annotations

import asyncio
import os

from acp import run_agent
from deepagents import create_deep_agent
from deepagents_acp.server import AgentServerACP, AgentSessionContext
from langgraph.checkpoint.memory import MemorySaver

from deep_agents_acp_starter.project_context import build_project_context


SYSTEM_PROMPT = """You are a careful coding agent embedded in the user's editor.

Work like a senior engineer:
- inspect the project before changing code
- keep changes focused
- use the plan tool for multi-step work
- run relevant checks when practical
- explain risks and tradeoffs briefly
- ask for permission before destructive actions

The user can still edit files by hand while you work, so treat unexpected changes as user-owned.
"""


MODELS = [
    {"value": "openai:gpt-5", "name": "GPT-5"},
    {"value": "openai:gpt-5-mini", "name": "GPT-5 mini"},
]


def build_deep_agent(model: str | None = None):
    selected_model = model or os.environ.get("DEFAULT_MODEL") or MODELS[0]["value"]
    project_context = build_project_context()

    return create_deep_agent(
        model=selected_model,
        system_prompt=f"{SYSTEM_PROMPT}\n\n{project_context}",
        checkpointer=MemorySaver(),
    )


def build_agent(context: AgentSessionContext):
    return build_deep_agent(model=context.model)


async def main() -> None:
    server = AgentServerACP(
        agent=build_agent,
        models=MODELS,
    )
    await run_agent(server)


if __name__ == "__main__":
    asyncio.run(main())
