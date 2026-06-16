# MCP servers (Phase 2)

These ship the runtime capabilities the skills describe but cannot provide on
their own. Each pairs with a skill that explains when to reach for it.

- **think** — the no-op `think` tool from [The "think" tool](https://www.anthropic.com/engineering/claude-think-tool). Pairs with the `using-the-think-step` skill.
- **tool-gateway** — lazy tool loading plus a tool-search mechanism, from [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use). For agents with large tool libraries.
- **code-execution** — MCP tools presented as importable code files, from [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp).

Once a server lands here, `.mcp.json` at the repo root wires it into the plugin.
