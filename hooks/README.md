# Hooks

Hooks enforce behavior the model cannot be trusted to enforce on itself. An
agent asked to police its own actions can argue itself into approval, so these
hooks run outside the model. This pack ships two, both off by default: a
`PreToolUse` gate on the commands an agent runs, and a `PostToolUse` screen on
the text its tools pull in.

## Action gating (PreToolUse)

`action_gate.py` is the enforcement half of
[Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode).
It reads a Bash command before it runs and decides whether to allow, ask, or deny.

### Off by default

The hook is registered in `hooks.json`, but it does nothing until you turn it on
with the `AGENT_STDLIB_GATING` environment variable:

| Value | Behavior |
|-------|----------|
| `off` (default) | No-op. Every Bash command proceeds untouched. |
| `warn` | Dangerous commands prompt you (`ask`); everything else proceeds. |
| `enforce` | Dangerous commands are denied; commands not on the safe list prompt you. |

```
export AGENT_STDLIB_GATING=enforce
```

By design the gate only ever **denies** or **asks**. It never emits `allow`, so
it can add friction but never silently approves a command you would otherwise
have been prompted for.

### How it tiers a command

`action_gate.py` reads the tool call on stdin and sorts the Bash command into:

- **safe**: read-only commands (`ls`, `cat`, `grep`, `git status`, ...). Defers
  to your normal flow.
- **dangerous**: matches a rule in one of the auto-mode risk categories:
  destruction, exfiltration, security degradation, trust-boundary violation, or
  shared-resource bypass. Denied (enforce) or asked (warn).
- **unknown**: anything else. Asked (enforce) or allowed (warn).

A command with a pipe, chain, redirect, or subshell is never treated as safe,
because the risky part may be downstream of a harmless-looking first command.

### Extend the rules

Edit `DANGER` (patterns, each tagged with a risk category and a reason),
`SAFE_FIRST` (read-only command names), and `GIT_SAFE` (read-only git
subcommands) in `action_gate.py`.

## Injection screen (PostToolUse)

`injection_screen.py` is the inbound counterpart to the gate. The gate watches
commands the agent runs; the screen watches text the agent reads. A fetched
page, an email, or an API response can carry instructions aimed at the model,
and a helpful model follows them unless something flags the content as data
first. Pairs with the `defending-against-prompt-injection` skill.

### Off by default

Registered against the `WebFetch` tool in `hooks.json`, but inert until you set
`AGENT_STDLIB_INJECTION`:

| Value | Behavior |
|-------|----------|
| `off` (default) | No-op. Every tool result passes untouched. |
| `warn` | Suspicious output gets a context note; the agent still proceeds. |
| `enforce` | Suspicious output is blocked; the agent must report it and confirm before acting. |

```
export AGENT_STDLIB_INJECTION=warn
```

It scans the tool result for common injection markers (text telling the model to
ignore prior instructions, forged system turns, secrecy or exfiltration
requests, prompt-extraction attempts, known jailbreak handles) and flags a hit.
A `PostToolUse` hook runs after the tool already returned, so it annotates the
next step or blocks it; it does not strip or rewrite the output.

### Widen the coverage

The hook screens `WebFetch` by default. Add other tools that pull in outside text
to the `PostToolUse` matcher in `hooks.json`. Edit `MARKERS` in
`injection_screen.py` to tune the patterns.

## These are references, not the production classifiers

Both hooks are deterministic and offline. The article's versions replace the
rule lists with a fast classifier plus reasoning on the flagged cases, and add
an output-layer screen on the transcript. Keep the structure and the
deny-or-flag stance; swap the rules for a classifier call when you want real
judgment.
