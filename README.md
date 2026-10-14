# Deep Agents + ACP Starter

This project is a small starter for building a coding agent like the one described in JetBrains' post, "Using ACP + Deep Agents to Demystify Modern Software Engineering."

The core idea:

- Use Deep Agents for the agent harness: filesystem tools, shell access, planning, sub-agents, streaming, and human-in-the-loop interrupts.
- Expose that agent through Agent Client Protocol so an editor can talk to it as a native agent.
- Keep the harness inspectable and customizable in Python instead of hiding behavior behind a CLI-only configuration layer.
- Add observability with LangSmith so you can inspect prompts, tool calls, traces, and failure modes.

## Project Layout

```text
.
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── hexagonal-architecture.md
│   └── post-outline.md
├── pyproject.toml
├── scripts/
│   └── run_agent.sh
└── src/
    └── deep_agents_acp_starter/
        ├── __init__.py
        ├── agent.py
        └── project_context.py
```

## Quick Start

1. Install `uv`.
2. Create your environment file:

```bash
cp .env.example .env
```

3. Fill in `OPENAI_API_KEY` in `.env`.
4. Install dependencies:

```bash
uv sync
```

5. Run the ACP server:

```bash
./scripts/run_agent.sh
```

## VS Code Setup

This project can run inside VS Code through the **ACP Client** extension. VS Code is the client; this project is the ACP server.

### 1. Install The Extension

Install **ACP Client** from the VS Code Marketplace.

After installing it, reload VS Code:

```text
Command Palette -> Developer: Reload Window
```

### 2. Open This Project In VS Code

Open the repository folder itself:

```bash
code "/absolute/path/to/deep-agents-acp-starter"
```

If the `code` command is not available, open VS Code and use:

```text
File -> Open Folder...
```

### 3. Configure The ACP Agent

Create `.vscode/settings.json` in your local checkout.

Do not commit this file if it contains machine-specific absolute paths. This repo ignores `.vscode/settings.json` for that reason.

Use this template and replace the two paths with your local repository path:

```json
{
  "acp.agents": {
    "Deep Agents Starter": {
      "command": "/absolute/path/to/deep-agents-acp-starter/scripts/run_agent.sh",
      "args": [],
      "env": {}
    }
  },
  "acp.defaultWorkingDirectory": "/absolute/path/to/deep-agents-acp-starter"
}
```

Example on macOS:

```json
{
  "acp.agents": {
    "Deep Agents Starter": {
      "command": "/Users/your-user/Desktop/deep-agents-acp-starter/scripts/run_agent.sh",
      "args": [],
      "env": {}
    }
  },
  "acp.defaultWorkingDirectory": "/Users/your-user/Desktop/deep-agents-acp-starter"
}
```

The extension starts `run_agent.sh` automatically. You do not need to run the script manually while using VS Code.

### 4. Connect To The Agent

Open the Command Palette and run:

```text
ACP: Open Chat Panel
```

Then connect:

```text
ACP: Connect to Agent
```

Choose:

```text
Deep Agents Starter
```

If needed, create a conversation with:

```text
ACP: New Conversation
```

### 5. Test The Connection

Send:

```text
Liste os arquivos deste projeto e explique a estrutura.
```

If everything is working, the ACP Client log should show lines similar to:

```text
Starting Deep Agents ACP server with openai:gpt-5...
LangSmith project: deep-agents-acp-starter
Connected to agent Deep Agents Starter
Prompt response: stopReason=end_turn
```

### Troubleshooting VS Code

If the ACP commands do not appear, confirm that the installed extension is **ACP Client**, then reload VS Code.

If the agent does not start, open:

```text
Command Palette -> ACP: Show Log
```

Common issues:

- `OPENAI_API_KEY is missing`: create `.env` from `.env.example` and fill `OPENAI_API_KEY`.
- `run_agent.sh` path is wrong: update `.vscode/settings.json` with the absolute path on your machine.
- `uv` is missing: install `uv`, then run `uv sync`.
- `EnvAddressError` from LangSmith: use `LANGSMITH_PROJECT`, not `LANGSMITH_AGENT_ID` / `LANGSMITH_AGENT_ENVIRONMENT`.

## Other ACP Editors

For another ACP-compatible editor, configure a custom agent server that runs:

```bash
/absolute/path/to/deep-agents-acp-starter/scripts/run_agent.sh
```

The exact settings shape depends on the editor. Zed and JetBrains ACP integrations follow the same core model: the editor starts this command, then communicates with the agent over ACP.

## Local Web UI

This project also includes a local browser surface inspired by Kiro's "one harness, many surfaces" architecture.

```bash
cd "/Users/marianabastos/Desktop/Deep Agents"
./scripts/run_web.sh
```

Then open:

```text
http://127.0.0.1:8787
```

The Web UI uses the same Deep Agents harness, OpenAI configuration, and LangSmith project as the ACP server.

## Local CLI

The same harness can also run from a terminal.

Interactive mode:

```bash
cd "/Users/marianabastos/Desktop/Deep Agents"
./scripts/run_cli.sh
```

Single prompt mode:

```bash
./scripts/run_cli.sh "Leia o README deste projeto e resuma em 5 bullets."
```

You can reuse a conversation with:

```bash
./scripts/run_cli.sh --session-id my-session "Continue a resposta anterior."
```

## Architecture Direction

The project is moving toward a hexagonal architecture:

- domain core: sessions, turns, events, permissions, policies
- application layer: harness use cases and orchestration
- inbound adapters: ACP for IDEs, HTTP/SSE for Web, terminal CLI
- outbound adapters: Deep Agents, OpenAI, filesystem tools, LangSmith, persistence

See [docs/hexagonal-architecture.md](docs/hexagonal-architecture.md) for the full design.

## OpenAI Configuration

This starter is configured to use OpenAI only. The active local `.env` file should contain:

```bash
OPENAI_API_KEY="..."
DEFAULT_MODEL="openai:gpt-5"
```

For LangSmith tracing, add:

```bash
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="..."
LANGSMITH_PROJECT="deep-agents-acp-starter"
```

This starter uses `LANGSMITH_PROJECT`, which is the stable tracing mode for Deep Agents/LangGraph.

You can switch to another OpenAI model by changing `DEFAULT_MODEL` and the `MODELS` list in `src/deep_agents_acp_starter/agent.py`.

## LangSmith Smoke Test

To confirm that the LangSmith API key and project are working independently of the editor, run:

```bash
cd "/Users/marianabastos/Desktop/Deep Agents"
set -a; source .env; set +a
uv run python scripts/test_langsmith.py
```

Then open the `Local` environment in the `deep-agents-acp-starter` project in LangSmith.

## What To Customize First

- `src/deep_agents_acp_starter/agent.py`: model list, system prompt, custom tools, and session behavior.
- `src/deep_agents_acp_starter/project_context.py`: what project metadata gets appended to the agent prompt.
- `docs/architecture.md`: implementation decisions and tradeoffs.
- `docs/post-outline.md`: article structure if you also want to publish a post similar in shape to the JetBrains one.

## References

- [LangChain Deep Agents ACP docs](https://docs.langchain.com/oss/python/deepagents/acp) - consulted for exposing Deep Agents over ACP, `deepagents-acp`, stdio server behavior, and ACP-compatible editor setup.
- [JetBrains post: Using ACP + Deep Agents to Demystify Modern Software Engineering](https://blog.jetbrains.com/ai/2026/04/using-acp-deep-agents-to-demystify-modern-software-engineering/#the-agent) - consulted for the agent architecture, custom harness framing, and implementation narrative.
- [Deep Agents ACP README](https://github.com/langchain-ai/deepagents/blob/main/libs/acp/README.md)
- [Agent Client Protocol](https://agentclientprotocol.com/)
