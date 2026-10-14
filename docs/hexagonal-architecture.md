# Hexagonal Architecture for the Harness

## Goal

Build one agent harness that can serve multiple surfaces:

- IDE through ACP over stdio
- local Web UI over HTTP and server-sent events
- local CLI through stdin/stdout
- future CLI, cloud sandbox, or mobile surfaces

The important boundary is this: surfaces should not own agent behavior. They should only translate user interaction into harness requests and translate harness events back into UI.

## Architecture Shape

```text
                         ┌────────────────────────┐
│        Surfaces         │
│  IDE ACP | Web | CLI    │
                         └───────────┬────────────┘
                                     │
                       inbound adapters / drivers
                                     │
             ┌───────────────────────▼───────────────────────┐
             │              Application Layer                  │
             │  sessions, turn orchestration, event mapping    │
             └───────────────────────┬───────────────────────┘
                                     │
                         application ports
                                     │
             ┌───────────────────────▼───────────────────────┐
             │                 Domain Core                    │
             │ prompts, policies, run stages, session model    │
             └───────────────────────┬───────────────────────┘
                                     │
                         outbound ports
                                     │
   ┌────────────────────┬────────────▼────────────┬────────────────────┐
   │ Deep Agents runtime│ filesystem / shell tools │ LangSmith tracing  │
   │ OpenAI models      │ permission policy        │ persistence        │
   └────────────────────┴─────────────────────────┴────────────────────┘
```

## Layers

### Domain Core

The domain core contains concepts that are true no matter where the user talks to the agent.

Responsibilities:

- define a session
- define a turn
- define run stages
- define events emitted by the harness
- define permission decisions
- define steering/project context contracts

It should not import FastAPI, ACP, LangGraph, Deep Agents, OpenAI, or LangSmith.

Suggested modules:

```text
src/deep_agents_acp_starter/domain/
├── events.py
├── models.py
└── policies.py
```

### Application Layer

The application layer coordinates use cases.

Responsibilities:

- start or resume a session
- submit a user prompt
- stream harness events
- choose the model
- call the agent runtime port
- map runtime events into product-level events

Suggested modules:

```text
src/deep_agents_acp_starter/application/
├── ports.py
└── harness_service.py
```

### Inbound Adapters

Inbound adapters are surfaces. They receive input from users and call the application layer.

Current adapters:

- ACP stdio adapter for VS Code and other IDE clients
- Web HTTP/SSE adapter for the browser UI
- CLI adapter for terminal workflows

Suggested modules:

```text
src/deep_agents_acp_starter/adapters/inbound/
├── acp_server.py
└── web_server.py
```

### Outbound Adapters

Outbound adapters implement ports required by the application layer.

Current adapters:

- Deep Agents runtime
- local project context provider
- LangSmith tracing through environment configuration

Future adapters:

- SQLite/Postgres session store
- permission store
- repository provider
- cloud sandbox executor
- MCP tool registry

Suggested modules:

```text
src/deep_agents_acp_starter/adapters/outbound/
├── deepagents_runtime.py
├── environment.py
├── project_context.py
└── tracing.py
```

## Primary Ports

### AgentRuntimePort

The application layer should see the runtime as a stream of events, not as a Deep Agents object.

```python
class AgentRuntimePort(Protocol):
    async def stream_turn(self, request: TurnRequest) -> AsyncIterator[HarnessEvent]:
        ...
```

Deep Agents becomes one implementation of this port.

### SessionStorePort

Stores session metadata separately from the model/runtime checkpoint.

```python
class SessionStorePort(Protocol):
    async def get(self, session_id: str) -> Session | None:
        ...

    async def save(self, session: Session) -> None:
        ...
```

First implementation can be in-memory. Later it can become SQLite or Postgres.

### PermissionPolicyPort

Keeps safety decisions out of the UI.

```python
class PermissionPolicyPort(Protocol):
    async def evaluate(self, request: ToolUseRequest) -> PermissionDecision:
        ...
```

ACP can render a permission prompt. Web can render a modal. The decision model stays the same.

### ProjectContextPort

Assembles steering/context before each turn.

```python
class ProjectContextPort(Protocol):
    async def build(self, workspace: WorkspaceRef) -> ProjectContext:
        ...
```

## Event Model

Use one event vocabulary for every surface:

```text
session.started
turn.started
context.collected
model.started
model.token
tool.requested
permission.requested
permission.resolved
tool.started
tool.finished
turn.finished
turn.failed
```

ACP maps these events to ACP session updates. Web maps them to SSE events. CLI can map them to terminal output.

## Surface Responsibilities

### IDE ACP

Owns:

- connection over stdio
- IDE chat UX
- mapping ACP requests to harness use cases
- mapping harness events back to ACP updates

Does not own:

- prompt policy
- runtime selection
- project context rules
- permission policy

### Web

Owns:

- browser layout
- HTTP endpoints
- SSE streaming
- status panels
- future auth/session UX

Does not own:

- agent loop
- permission decisions
- model provider configuration

## First Refactor Plan

1. Extract `build_deep_agent` into `adapters/outbound/deepagents_runtime.py`.
2. Move model and prompt configuration into domain/application config objects.
3. Create `HarnessService.stream_turn()`.
4. Update Web UI to call `HarnessService` instead of `build_deep_agent` directly.
5. Update ACP server to call the same service, or wrap the service in the Deep Agents ACP adapter if ACP requires a runtime object.
6. Add a real session store.
7. Add a shared permission model before implementing Web permission modals.

## Target Package Layout

```text
src/deep_agents_acp_starter/
├── application/
│   ├── __init__.py
│   ├── harness_service.py
│   └── ports.py
├── domain/
│   ├── __init__.py
│   ├── events.py
│   ├── models.py
│   └── policies.py
├── adapters/
│   ├── __init__.py
│   ├── inbound/
│   │   ├── __init__.py
│   │   ├── acp_server.py
│   │   ├── cli.py
│   │   └── web_server.py
│   └── outbound/
│       ├── __init__.py
│       ├── deepagents_runtime.py
│       ├── environment.py
│       ├── project_context.py
│       └── tracing.py
├── agent.py
└── web.py
```

During migration, `agent.py` and `web.py` can stay as compatibility entrypoints. Once the adapters are mature, they become thin imports.

## Why This Fits the Kiro-Like Model

Kiro's architecture is built around one harness and multiple surfaces. Hexagonal architecture gives this project the same separation:

- the harness is the application core
- ACP and Web are replaceable inbound adapters
- CLI is another inbound adapter for local automation and quick terminal use
- Deep Agents, OpenAI, filesystem tools, and LangSmith are outbound adapters
- configuration and policy live with the harness, not with one UI

That lets us add surfaces without duplicating agent behavior.

## References Consulted

- [LangChain Deep Agents ACP docs](https://docs.langchain.com/oss/python/deepagents/acp): used to ground the ACP inbound adapter, stdio runtime model, and editor-facing agent server setup.
- [JetBrains ACP + Deep Agents post](https://blog.jetbrains.com/ai/2026/04/using-acp-deep-agents-to-demystify-modern-software-engineering/#the-agent): used as the reference for the custom agent/harness concept this architecture formalizes.
