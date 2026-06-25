---
name: using-the-think-step
description: >-
  Decide where an agent should reason during a task and how to prompt for it.
  Covers three places a model can think and how to choose between them: extended
  thinking before the turn, interleaved thinking between tool calls, and the
  no-op "think" tool that logs reasoning mid-chain at a point you pick. Also
  covers when a mid-task step helps, when it only adds latency, the contract
  interleaved thinking imposes on the request, and why the think tool's gains
  come from system-prompt guidance rather than the tool itself. Use this whenever
  someone builds an agent that follows policies or makes long sequential
  decisions, asks about a think or scratchpad tool or interleaved thinking, finds
  an agent skipping rules or mishandling tool output mid-task, or wants more
  deliberate tool use.
  Trigger on "think tool," "interleaved thinking," "reasoning between tool
  calls," "let the agent reason before acting," "agent ignores the policy," and
  similar. Not for general prompt engineering or one-shot chain-of-thought.
---

# Using the think step

Source: [The "think" tool](https://www.anthropic.com/engineering/claude-think-tool), with the cross-mode decision drawing on the [extended thinking docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking). The pattern ships as MCP servers around the web; none package the judgment of *when* to use it, how it relates to extended and interleaved thinking, and how to prompt it. This pack ships the tool itself under `mcp-servers/think/`; this skill is about reaching for it well.

The think tool is a no-op the model can call to reason in the middle of a tool-use chain. It changes no state and returns nothing useful; its only job is to give the model a moment to lay out its reasoning before the next action. That makes it different from extended thinking, which happens once before the agent acts. The think step happens *between* actions, after the agent has seen a tool result and before it commits to what comes next.

## Where the reasoning goes

A model can reason in three places, and each does a different job:

- **Extended thinking, before the turn.** The model plans before it acts or fires off parallel, independent tool calls. On recent models, turn on adaptive thinking and set an effort level; on older ones, set a token budget below `max_tokens`. Reach for it when the hard part is the plan you make up front.
- **Interleaved thinking, between tool calls.** The model reasons after each tool result, inside the same turn, before it picks the next call. Use it when the next action depends on reading the last result and the agent has to adapt as results arrive.
- **The think tool, a logged checkpoint.** A no-op call the model makes to write its reasoning into the transcript at a point you choose. Use it in long sequential or policy-heavy chains where you want the reasoning on the record and the model to check a rule before the action it gates. It works whether or not the model supports interleaved thinking.

The think tool and interleaved thinking both reason between actions, so they overlap. The think tool leaves an inspectable record and takes a prompt you control; interleaved thinking is lighter and needs no tool call. Reach for the think tool when you want to audit or shape the reasoning, and for interleaved thinking when you want the model to adapt on its own.

### The interleaved-thinking contract

Two rules decide whether interleaved thinking works:

- **Pass thinking blocks back unmodified.** The server signs each block and checks the signature on the next request. Edit, reorder, or drop a block and the request fails. Return them as they came.
- **The thinking budget can run past `max_tokens`.** The budget covers all reasoning across the turn rather than a single response, so it sits above the output cap instead of under it. While thinking is on, only `tool_choice` `auto` or `none` work.

## When it earns its place

Add a think step where a wrong next action is expensive and the right one depends on what just came back:

- **Reading tool output mid-chain.** The agent gets a large or messy result and has to interpret it before acting. The think step is where it does that instead of reacting.
- **Policy- or compliance-heavy tasks.** The agent must check several rules before it is allowed to proceed. On the tau-bench airline domain, pairing the tool with domain guidance produced a 54% relative improvement, because the model checked the rules in the open rather than skipping them.
- **Long sequential decisions where errors compound.** Each step depends on the last, so an early slip propagates. A pause to re-derive the state pays off.

## When to skip it

Leave it out where it only adds latency:

- parallel or independent tool calls that do not depend on each other's results
- simple instruction-following the model handles in one shot

Adding a reasoning step to a task that does not need one slows the agent and clutters the transcript for no gain.

## How to add it

Define a tool named `think` with a single string parameter, often called `thought`, and no external effect. That is the whole tool. Its value does not come from the schema.

**Put the real guidance in the system prompt, not the tool description.** The tool is a blank scratchpad; the prompt teaches the model how to use it. Give it:

- worked examples that show the reasoning pattern you want, end to end
- a decision tree or checklist for the policy the agent must honor
- explicit instruction to verify compliance in a think step *before* the action it gates

Then test on the hardest cases first, watch how the model uses the scratchpad, and tighten the prompt where the reasoning comes out thin.
