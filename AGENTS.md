# Using agent-stdlib in any harness

This pack ships as a Claude Code plugin, but most of it is not Claude-specific.
This file maps each part to its portable form for harnesses like OpenCode,
Cursor, Cline, or a custom agent, on any tool-using model.

## What ports cleanly

- **MCP servers** (`mcp-servers/think`, `tool-gateway`, `code-execution`): MCP is
  an open protocol, so any MCP client can mount them. See "Mount the MCP servers".
- **Scripts** (`skills/*/scripts/*.py`, `scripts/locks.py`): plain Python, run
  anywhere.
- **`scripts/autonomy_loop.sh`**: set `AGENT_RUNNER` to your headless agent CLI
  (it defaults to `claude -p`), e.g. `AGENT_RUNNER="opencode run"`.

## What needs re-wrapping

- **Skills** (`skills/<name>/SKILL.md`): the content is harness-neutral; the
  auto-loading and triggering is a Claude Code feature. Load the file as a rule
  or paste its body into your system prompt. See "Use the skills as plain content".
- **action-gating hook** (`hooks/`): the classification logic is reusable; the
  `hooks.json` wiring and the input JSON shape are Claude Code's. See "Port the gate".
- **Commands and agent** (`commands/`, `agents/`): Claude Code formats that also
  rely on its subagent dispatch. Reuse the recipe inside them, not the files.

## Use the skills as plain content

Every skill is a self-contained markdown procedure. Point your agent at
`skills/<name>/SKILL.md`, or copy the body into your rules file (`AGENTS.md`,
`.cursorrules`, a system prompt). The frontmatter `description` says when each
skill applies, which is enough for a router to pick one. On a smaller model,
load the one you need explicitly rather than expecting it to self-select.

## Mount the MCP servers

The servers speak MCP over stdio and need [`uv`](https://docs.astral.sh/uv/),
which installs each one's single dependency on first run. A vendor-neutral
config most clients accept:

```json
{
  "mcpServers": {
    "think": {
      "command": "uv",
      "args": ["run", "/abs/path/agent-stdlib/mcp-servers/think/server.py"]
    },
    "tool-gateway": {
      "command": "uv",
      "args": ["run", "/abs/path/agent-stdlib/mcp-servers/tool-gateway/server.py"]
    }
  }
}
```

Claude Code, Cursor, and Cline read this shape. OpenCode declares servers in its
own `opencode.json` under an `mcp` key; use the same command and args. Add
`code-execution` the same way only after you have isolated it, since it runs
model-written code.

## Port the gate

`hooks/action_gate.py` reads a tool call on stdin and decides allow, ask, or
deny. The reusable core is `classify(command)`, which sorts a command into
`safe`, `unknown`, or `dangerous` and returns a category and reason. To use it
elsewhere, either call `classify()` from your harness's pre-execution hook, or
adapt the stdin parsing (it reads `{"tool_name", "tool_input": {"command"}}`) and
the output (it prints Claude Code's `hookSpecificOutput`) to your harness's
contract. The tiering and the deny-or-ask stance are the portable ideas; the I/O
shapes are the glue.

## Model notes

The knowledge applies to any model. Two things scale with capability: a smaller
model selects the right skill less reliably, so load it explicitly, and the
think step helps less than it does on a strong reasoner. Nothing here assumes
Claude as the model.
