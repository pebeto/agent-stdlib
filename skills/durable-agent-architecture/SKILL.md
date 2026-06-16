---
name: durable-agent-architecture
description: >-
  Structure a long-lived agent service so any part can crash and resume.
  Decompose it into brain (model plus harness), hands (ephemeral sandbox and
  tools), and session (a durable event log), each replaceable on its own, with
  wake/resume semantics and credentials kept out of the execution environment.
  Use this whenever someone designs a production or long-running agent backend,
  asks how to make agents crash-recoverable or resumable, worries about losing
  session state when a container dies, needs to scale agents as a service, or
  asks where to keep credentials for an agent that runs code. Trigger on "agent
  infrastructure," "resume an agent after a crash," "agent runs for hours,"
  "where do tokens live," and similar.
---

# Durable agent architecture

Source: [Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents). Long-running-harness skills exist, but they track context and progress within a run. None encode the service-level decomposition that lets a component die and the agent resume.

A demo agent lives in one process. A production agent runs for hours, survives crashes, and resumes where it stopped. The difference is structural: split the agent into three planes with stable interfaces between them, so each fails and reboots without taking the others down.

## The three planes

- **Brain.** The model plus the harness logic that drives it. This decides what to do next.
- **Hands.** The sandbox and tools that execute. Treat these as ephemeral and disposable.
- **Session.** A durable, queryable event log of everything that happened. This is the source of truth.

The rule that makes it durable: the brain and the session live *outside* the execution container. When the container dies, and containers die, you lose the hands and nothing else. Cattle, not pets.

## Resume from the log, not from memory

The session is an append-only event log you can query, not a transcript stuffed back into the context window. Build two operations around it:

- `wake(sessionId)` rehydrates an agent from its log and continues.
- `getSession(id)` reads the current state without resuming execution.

Let the model pull history out of the log on demand through a `getEvents()`-style call that returns a selected range, rather than replaying the entire log into context every time. The full log will outgrow the window; selective retrieval keeps the agent working on long sessions.

The reference in `references/session-interface.md` sketches the event schema and these operations.

## Keep credentials out of the hands

The execution environment runs model-directed code, so it is the last place a long-lived secret should sit. Two patterns keep credentials out of it:

- **Token bundling at init.** Inject a short-lived, scoped token when the sandbox starts (the pattern Git access uses).
- **A vault proxy.** Route authenticated calls through an intermediary that holds the real credential and validates the request (the pattern OAuth flows use).

## Provision the hands lazily

Do not block on sandbox startup before the model can think. Decouple sandbox provisioning from inference startup and provision on the first tool call. The agent starts reasoning immediately, and time-to-first-token drops.
