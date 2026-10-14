#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -f ".env" ]; then
  set -a
  source ".env"
  set +a
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY is missing. Add it to .env before starting the agent." >&2
  exit 1
fi

LANGSMITH_TRACING_NORMALIZED="$(printf '%s' "${LANGSMITH_TRACING:-}" | tr '[:upper:]' '[:lower:]')"
LANGSMITH_PROJECT_NAME="${LANGSMITH_PROJECT:-deep-agents-acp-starter}"

if [ "$LANGSMITH_TRACING_NORMALIZED" = "true" ]; then
  export LANGSMITH_TRACING=true
  unset LANGSMITH_AGENT_ID
  unset LANGSMITH_AGENT_ENVIRONMENT
  export LANGSMITH_PROJECT="$LANGSMITH_PROJECT_NAME"
  export LANGCHAIN_TRACING_V2=true
  export LANGCHAIN_API_KEY="${LANGSMITH_API_KEY:-}"
  export LANGCHAIN_PROJECT="$LANGSMITH_PROJECT_NAME"
fi

export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"

echo "Starting Deep Agents ACP server with ${DEFAULT_MODEL:-openai:gpt-5}..." >&2
echo "LangSmith project: ${LANGSMITH_PROJECT_NAME}" >&2
echo "This process stays open while it waits for an ACP-compatible editor to connect." >&2

exec uv run python -m deep_agents_acp_starter.agent
