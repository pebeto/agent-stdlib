# think (MCP server)

A single no-op `think` tool. The agent calls it to reason in the middle of a
tool-use chain: read a tool result, check the rules a task must follow, or plan
a sequence of steps where an early mistake would compound. It changes no state
and returns a short acknowledgment.

Source: [The "think" tool](https://www.anthropic.com/engineering/claude-think-tool).

The tool is deliberately empty. Its value comes from how you prompt the agent to
use it, which the **`using-the-think-step`** skill in this pack covers: when a
think step helps, when it only adds latency, and where the domain guidance
belongs (the system prompt, not the tool).

## Run

With `uv` (installs the dependency from the script header on first run):

```
uv run server.py
```

Or with `mcp` already installed:

```
pip install mcp
python3 server.py
```

## Wire into a client

This server ships in the `agent-stdlib` plugin's `.mcp.json` as
`agent-stdlib-think`. To add it to another MCP client by hand, point the client
at `uv run /path/to/mcp-servers/think/server.py` over stdio.
