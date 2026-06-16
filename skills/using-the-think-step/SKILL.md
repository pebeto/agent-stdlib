---
name: using-the-think-step
description: >-
  Decide when to give an agent a mid-task reasoning step and how to prompt for
  it. Covers the no-op "think" tool that lets a model stop and reason in the
  middle of a tool-use chain (distinct from extended thinking, which happens
  before acting), the task shapes where it helps, the ones where it just adds
  latency, and why the gains come from system-prompt guidance rather than the
  tool itself. Use this whenever someone builds an agent that follows policies or
  makes long sequential decisions, asks whether to add a think or scratchpad
  tool, finds an agent skipping rules or mishandling tool output mid-task, or
  wants more deliberate tool use. Trigger on "think tool," "let the agent reason
  before acting," "agent ignores the policy," and similar. Not for general
  prompt engineering or one-shot chain-of-thought, and not the same as
  extended thinking before a turn.
---

# Using the think step

Source: [The "think" tool](https://www.anthropic.com/engineering/claude-think-tool). The pattern ships as MCP servers around the web; none package the judgment of *when* to use it and how to prompt it. This pack ships the tool itself under `mcp-servers/think/`; this skill is about reaching for it well.

The think tool is a no-op the model can call to reason in the middle of a tool-use chain. It changes no state and returns nothing useful; its only job is to give the model a moment to lay out its reasoning before the next action. That makes it different from extended thinking, which happens once before the agent acts. The think step happens *between* actions, after the agent has seen a tool result and before it commits to what comes next.

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
