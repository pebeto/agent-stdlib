# tool-gateway (MCP server)

Many tools behind two. A large tool library bloats an agent's context, because
every definition sits in the window whether the task needs it or not. This
server exposes only `search_tools` and `call_tool`, holding a larger catalog
behind them. The agent searches for what it needs, reads only those
definitions, then invokes them by name.

Source: [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) and [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp). See the `scaling-agent-tools` direction in the pack's design notes.

## The two tools

- **`search_tools(query, detail)`** — ranks the catalog against a plain-language
  query and returns the matches. `detail="summary"` returns names and
  descriptions; `detail="full"` adds each tool's argument schema.
- **`call_tool(name, arguments)`** — invokes a catalog tool by name. Unknown
  names and bad arguments return an actionable error, not a crash.

## What this covers, and what it does not

This is the server-side half of progressive disclosure: keeping definitions out
of context until asked for. True lazy-loading at the API layer (the client
deferring tool definitions and expanding them on demand) is a client feature;
this server is what you put behind it.

The catalog ships four dependency-free example tools (`text_stats`,
`temp_convert`, `base_convert`, `json_validate`) so the server runs and tests on
its own. To use it for real, replace `CATALOG` in `server.py` with your tools,
or adapt `call_tool` to proxy to downstream MCP servers. The ranking is
deliberate term-overlap matching; swap in BM25 or embeddings when the catalog
grows.

## Run

```
uv run server.py        # installs mcp from the script header
```
