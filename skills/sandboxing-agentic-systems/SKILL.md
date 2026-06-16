---
name: sandboxing-agentic-systems
description: >-
  Contain an agent that runs code or reads untrusted content, layer by layer.
  Covers OS-level filesystem and network isolation that also catches spawned
  subprocesses, an egress proxy that checks request provenance, treating tool
  outputs and fetched pages as prompt-injection vectors, and keeping credentials
  outside the sandbox behind a proxy. Use this whenever someone designs a
  sandbox for a coding or computer-use agent, asks how to safely let an agent
  run shell commands or browse, worries about prompt injection from tool
  results, needs to limit what an autonomous agent can reach or delete, or asks
  where an agent's credentials should live. Trigger on "sandbox the agent,"
  "agent runs untrusted code," "prompt injection," "restrict network access,"
  and similar. This is environment containment; deciding which actions need
  approval before they run is a separate concern (action gating).
---

# Sandboxing agentic systems

Source: [How we contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude) and [Beyond permission prompts](https://www.anthropic.com/engineering/claude-code-sandboxing). Single-layer skills exist (a Seatbelt-profile generator, Docker configs). None package the end-to-end, threat-model-driven layering, which is where containment actually comes from.

Contain at the environment layer first, steer at the model layer second. A prompt or a classifier is probabilistic and will miss an edge case eventually. A filesystem mount and a firewall rule are deterministic: they hold on the case you did not think of. Build the deterministic boundary first and treat model-layer guidance as a second line, never the only one.

## Isolate the filesystem

Scope reads and writes to the working directories the task needs. Block parent and system paths. Two details decide whether it holds:

- **Use an OS primitive that also covers spawned subprocesses.** Linux bubblewrap and macOS Seatbelt confine the process tree, so a shell command the agent runs is confined too. An application-level path check does not survive the agent shelling out.
- **Validate paths before symlink resolution.** A symlink inside an allowed directory can point at `/etc`. Resolve and check the real target, not the link.

Offer mount modes that match the task: read-only, read-write, and read-write-without-delete for work that should add but never remove.

## Isolate the network

Route every outbound connection through an egress proxy with allow and deny lists, and prompt on a new destination. The non-obvious part:

**Check provenance, not just the destination domain.** Allowlisting a domain opens every endpoint reachable through it, including ones that exfiltrate. Validate where the request came from and what it carries, not only where it is going.

## Treat incoming content as hostile

Anything a network-enabled tool returns is a possible prompt-injection payload, including a fetched web page, an API response, or a file from a shared drive. Run tool results through a lightweight classifier before they enter the model's context. Defer parsing or executing project-local config, localhost listeners, and similar local-but-untrusted inputs until the user has explicitly consented.

## Keep credentials outside the sandbox

The sandbox runs model-directed code, so a long-lived secret inside it is one injection away from leaving. Put credentials behind a transparent intermediary, such as a git proxy, that authenticates and validates the request's parameters before it injects the token. The agent uses the capability; it never holds the secret.

## Log every boundary attempt

Record and surface each escape or boundary-violation attempt immediately. The logs tell you whether your layers are holding and give you the signal to tighten them.

## Match the isolation to the blast radius

Prefer battle-tested primitives (gVisor, seccomp, hypervisors) over custom isolation you have to get right yourself. Size the isolation to what the agent could damage and to the expertise of whoever operates it. Anthropic's reference implementation is `anthropic-experimental/sandbox-runtime`.
