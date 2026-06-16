# Agents (Phase 3)

Subagent definitions the commands dispatch.

- **research-worker** — the worker the `/research` command spawns in parallel: takes one objective, an output format, and boundaries, then writes its findings to the shared filesystem rather than back through the lead. See the `multi-agent-orchestration` skill.
