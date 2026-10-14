# Architecture

## Goal

Build a coding agent that feels native inside an editor while keeping the agent harness understandable and editable as ordinary Python code.

The long-term project shape is described in `docs/hexagonal-architecture.md`: one harness core, multiple inbound surfaces, and replaceable outbound adapters.

## Components

### ACP Client

The editor is the client. It owns the user interface: threads, mentions, permission prompts, cancellation, and visible progress.

### ACP Server

`AgentServerACP` adapts the Deep Agent runtime to ACP. It is responsible for:

- session lifecycle
- message routing
- streaming updates
- model selection
- translating agent interrupts into editor permission requests

### Deep Agent

Deep Agents provides the agent harness:

- filesystem tools
- shell access
- planning
- sub-agents
- context summarization
- human-in-the-loop interrupts

### Project Context

`project_context.py` appends local project metadata to the agent prompt:

- current workspace root
- Git repository and branch
- package manager
- available local tools

This mirrors the custom middleware pattern from the JetBrains post: small, explicit bits of local context make the agent less likely to wander through the wrong directory or choose the wrong workflow.

## Permission Flow

The intended flow is:

1. The agent decides it needs a risky action, such as shell execution or file modification.
2. Deep Agents emits an interrupt.
3. The ACP adapter maps that interrupt to a client permission request.
4. The user approves, rejects, or allows that command class for the session.
5. The agent resumes with the user's decision.

## Observability

Enable LangSmith with the `.env` variables when you want traceability:

- prompts sent to the model
- tool calls
- model responses
- branching and failure points

Use traces to debug agent behavior, especially slow filesystem sweeps, missing context, or repeated failed commands.

## Model Provider

This starter is intentionally OpenAI-only. The local `.env` file should provide `OPENAI_API_KEY`, and `DEFAULT_MODEL` should use the `openai:<model>` format expected by Deep Agents.

## First Implementation Milestones

1. Run the default ACP server from this repo.
2. Connect it to an ACP-compatible editor.
3. Confirm basic message streaming.
4. Confirm file read/edit behavior.
5. Confirm shell permission prompts.
6. Add durable session persistence.
7. Add project-specific tools.
8. Add LangSmith tracing.

## References Consulted

- [LangChain Deep Agents ACP docs](https://docs.langchain.com/oss/python/deepagents/acp): ACP package setup, stdio server behavior, `AgentServerACP`, and editor/client integration model.
- [JetBrains ACP + Deep Agents post](https://blog.jetbrains.com/ai/2026/04/using-acp-deep-agents-to-demystify-modern-software-engineering/#the-agent): agent section, harness customization, and the developer-story structure for this starter.
