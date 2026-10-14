# Post Outline

## Working Title

Building an Inspectable Coding Agent With Deep Agents and ACP

## Opening

Start with the personal problem: coding agents are useful, but the harness can feel opaque. The goal is not to train a model; it is to own the software layer around the model.

## Why ACP Instead of a Terminal

Explain why the editor matters:

- the developer already understands code through the IDE
- selected files and code blocks are valuable context
- the agent can live beside normal editing and review workflows
- permission prompts and progress updates feel native

## The Agent

Describe the Deep Agents layer:

- filesystem tools
- shell execution
- planning
- sub-agents
- streaming
- cancellation
- summarization

Then explain the custom project context middleware in this repo.

## The ACP Adapter

Explain the mapping:

- agent plans become visible plans
- interrupts become permission prompts
- sessions map to checkpointers
- streamed updates become editor-visible progress
- model choices become session configuration

## Permission Handling

Go deeper here. This is where trust is built:

- what requires approval
- what can be allowed for the session
- what should never bypass approval
- how similar commands are classified

## Observability

Show why tracing matters:

- inspect exact context
- see tool calls
- identify wrong assumptions
- tune prompts and tools based on real failures

## What Worked

Share practical findings:

- small context improvements matter
- model switching is useful mid-session
- visible traces reduce mystery
- editor-native UX changes how often you use the agent

## What To Build Next

Close with extensions:

- durable persistence
- custom project tools
- repo-specific skills
- evals for common tasks
- safer permission policies
