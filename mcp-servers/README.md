# MCP servers (Phase 2)

These ship the runtime capabilities the skills describe but cannot provide on
their own. Each pairs with a skill that explains when to reach for it. Running
them needs [`uv`](https://docs.astral.sh/uv/), which installs each server's one
dependency from the script header on first run.

- **think** (enabled) — the no-op `think` tool from [The "think" tool](https://www.anthropic.com/engineering/claude-think-tool). Pairs with the `using-the-think-step` skill.
- **tool-gateway** (enabled) — `search_tools` plus `call_tool` over a larger catalog, so the agent reaches many tools through two, from [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use).
- **code-execution** (opt-in) — MCP tools presented as importable code files, with composed Python run in a subprocess, from [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp). It runs model-written code, so it is not wired in by default; see its README.

`think` and `tool-gateway` are wired into the repo-root `.mcp.json`.
`code-execution` is enabled by hand once you have isolated it.
