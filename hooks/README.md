# action-gating (PreToolUse hook)

Hooks enforce behavior the model cannot be trusted to enforce on itself. An
agent asked to gate its own actions can argue itself into approval, so this gate
runs as a `PreToolUse` hook outside the model. It is the enforcement half of
[Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode).

## Off by default

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

## How it tiers a command

`action_gate.py` reads the tool call on stdin and sorts the Bash command into:

- **safe**: read-only commands (`ls`, `cat`, `grep`, `git status`, ...). Defers
  to your normal flow.
- **dangerous**: matches a rule in one of the auto-mode risk categories:
  destruction, exfiltration, security degradation, trust-boundary violation, or
  shared-resource bypass. Denied (enforce) or asked (warn).
- **unknown**: anything else. Asked (enforce) or allowed (warn).

A command with a pipe, chain, redirect, or subshell is never treated as safe,
because the risky part may be downstream of a harmless-looking first command.

## This is a reference, not the production classifier

The rules here are deterministic and offline. The article's version replaces the
rule engine with a fast single-token classifier plus detailed reasoning on the
flagged commands, and adds an output-layer screen on the transcript. Keep the
tiered structure and the deny-or-ask stance; swap the rule list for a classifier
call when you want real judgment. The gate covers the `Bash` tool; extend the
`matcher` in `hooks.json` to gate others.

## Extend the rules

Edit `DANGER` (patterns, each tagged with a risk category and a reason),
`SAFE_FIRST` (read-only command names), and `GIT_SAFE` (read-only git
subcommands) in `action_gate.py`.
