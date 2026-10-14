from __future__ import annotations

from langsmith import traceable


@traceable(name="deep-agents-acp-starter-smoke-test")
def smoke_test(message: str) -> str:
    return f"LangSmith tracing is working: {message}"


if __name__ == "__main__":
    print(smoke_test("ok"))
