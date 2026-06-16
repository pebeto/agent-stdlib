# code-execution (MCP server)

Tools as importable code, composed in a sandbox. Instead of loading every tool
definition into context, this server presents tools as files the agent
discovers and reads on demand, then lets the agent write Python that imports and
composes them. Large intermediate results stay in the execution environment;
only what the code prints returns to the model.

Source: [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp).

## Not enabled by default

`run_python` executes model-written code. For that reason it is **not** wired
into the plugin's `.mcp.json`. Enable it yourself, and only once you have
wrapped it in real isolation.

The server already applies a wall-clock timeout, POSIX resource limits (CPU,
memory, file size), a minimal environment, and a temporary working directory.
That is not a substitute for OS-level containment: it does not isolate the
network or the wider filesystem. The `sandboxing-agentic-systems` skill in this
pack describes the layers to add (filesystem and network isolation that covers
subprocesses, an egress proxy, credentials kept outside the sandbox). Treat this
server as a reference for the pattern, not a finished sandbox.

## The three tools

- **`list_tools()`** — list the importable tool modules.
- **`read_tool(name)`** — read a module's source before you use it.
- **`run_python(code, timeout_seconds=10)`** — run code with the `tools`
  package importable; returns stdout and stderr. Timeout caps at 60s.

The `tools/` directory holds two dependency-free examples (`text_utils`,
`math_utils`). Replace them with wrappers around your real tools or MCP calls.

## Enable it

Add to your client's MCP config (not the shipped `.mcp.json`):

```json
{
  "mcpServers": {
    "agent-stdlib-code-execution": {
      "command": "uv",
      "args": ["run", "/abs/path/to/mcp-servers/code-execution/server.py"]
    }
  }
}
```
