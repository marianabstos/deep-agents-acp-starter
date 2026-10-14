from __future__ import annotations

import argparse
import asyncio
import sys
import uuid
from typing import Any

from deep_agents_acp_starter.agent import MODELS, build_deep_agent


async def run_prompt(message: str, session_id: str, model: str | None = None) -> None:
    agent = build_deep_agent(model=model)
    config = {"configurable": {"thread_id": session_id}}
    payload = {"messages": [{"role": "user", "content": message}]}

    printed = False
    async for chunk in agent.astream(payload, config=config, stream_mode="updates"):
        text = _extract_text(chunk)
        if text:
            printed = True
            print(text, end="", flush=True)

    if printed:
        print()


async def interactive(model: str | None = None) -> None:
    session_id = uuid.uuid4().hex
    print("Deep Agents CLI")
    print(f"Session: {session_id}")
    print("Type /exit to quit.")
    print()

    while True:
        try:
            message = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not message:
            continue
        if message in {"/exit", "/quit"}:
            return

        print("agent> ", end="", flush=True)
        await run_prompt(message, session_id=session_id, model=model)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Deep Agents harness from the CLI.")
    parser.add_argument("prompt", nargs="*", help="Prompt to send. Omit it for interactive mode.")
    parser.add_argument("--model", choices=[model["value"] for model in MODELS], default=None)
    parser.add_argument("--session-id", default=None, help="Reuse a session id for follow-up turns.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    if args.prompt:
        session_id = args.session_id or uuid.uuid4().hex
        asyncio.run(run_prompt(" ".join(args.prompt), session_id=session_id, model=args.model))
        return

    asyncio.run(interactive(model=args.model))


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


if __name__ == "__main__":
    main()
