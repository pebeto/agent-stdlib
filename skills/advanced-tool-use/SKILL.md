---
name: advanced-tool-use
description: >-
  Give an agent access to many tools without flooding its context with every
  tool definition. Covers the three advanced-tool-use patterns: a search tool the
  agent calls to discover tools on demand, programmatic tool calling where the
  model writes code that invokes tools and filters results before they return,
  and tool-use examples that teach correct invocation. Use this when an agent's
  context fills with tool schemas, an agent picks the wrong tool out of dozens,
  someone connects many MCP servers at once, or a single task chains several tool
  calls. Trigger on "too many tools," "tool definitions eat my context," "tool
  search," "programmatic tool calling," "agent calls the wrong tool," and
  similar. This is scaling access to a large tool catalog; writing a single
  tool's description and response shape is tool design (covered by community
  packs), and gating which commands run is action gating.
---

# Advanced tool use

Source: [Advanced tool use on the Claude Developer Platform](https://www.anthropic.com/engineering/advanced-tool-use). Community packs cover writing one good tool; none package the patterns for reaching many tools through a few. This pack ships the runnable side under `mcp-servers/tool-gateway/` (search and call) and `mcp-servers/code-execution/` (tools as code); this skill is the judgment for when to reach for each.

## Tool definitions are context

Loading every tool's schema up front spends tokens before the agent does any work, and a long menu makes the model choose worse. Past a couple dozen tools, the definitions crowd out the task. The three patterns below each cut a different part of that cost.

## Discover tools on demand

Register one search tool in place of the full catalog. The agent describes what it needs, the search tool returns the few matching definitions, and only those enter the context. This pack's `tool-gateway` server does this with `search_tools` and `call_tool` over a larger catalog. Reach for it when the catalog is large or shifts between sessions.

## Call tools from code

Let the model write code that invokes tools, chains several calls, and applies control flow in one block, in place of one round-trip per call. The code runs in a sandbox and returns only what the model keeps. Two wins follow: a result with ten thousand rows gets filtered to the five the model needs before any of it crosses into the context, and a five-step sequence costs one turn rather than five. This pack's `code-execution` server presents tools as importable functions for this pattern. It runs model-written code, so isolate it first (see `sandboxing-agentic-systems`).

## Show a worked invocation

Add example calls to a tool's definition. A worked invocation teaches the right argument shape faster than prose, and it costs little context next to a paragraph of caveats. Use it on tools with fiddly inputs the model keeps getting wrong.

## Combine them

The three compose. Search narrows the catalog to a handful; examples on those few teach correct use; programmatic calling chains them and trims the output. Start with whichever cost hurts: schema bloat (search), wrong invocations (examples), or many sequential round-trips (programmatic calling).
