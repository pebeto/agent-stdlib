---
name: multi-agent-orchestration
description: >-
  Run an orchestrator-worker system for breadth-first research: a lead agent
  plans, spawns three to five subagents with their own context windows, and
  synthesizes their findings. Covers when multi-agent actually beats a single
  agent and when it just burns tokens, how to delegate so subagents do not
  overlap, broad-to-narrow search, writing findings to a filesystem, and how to
  evaluate the system. Use this whenever someone wants to parallelize research
  or exploration across agents, asks how to coordinate a lead and subagents,
  considers a multi-agent setup, or asks whether multi-agent is worth it for
  their task. Trigger on "orchestrator and workers," "parallel research agents,"
  "lead agent spawns subagents," "should this be multi-agent," and similar.
---

# Multi-agent orchestration

Source: [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system). The pattern lives in Anthropic's cookbook as notebooks and prompts. This packages the parallel-research recipe as a skill, with the judgment of when to use it. The pack also ships a `/research` command and a `research-worker` subagent that run this flow.

A lead agent plans a question, spawns several subagents to chase parts of it in parallel, and synthesizes what they return. Each subagent has its own context window, so the system explores far more ground than one agent could hold at once. That power has a price, so the first decision is whether to use it at all.

## Use it for breadth, not for coupling

Multi-agent fits work that splits into independent pieces explored at the same time: surveying a literature, gathering evidence from many sources, mapping a large unknown space. It fits poorly when the pieces depend on each other.

Do not reach for it on a coding task with shared state, or anything that needs tight coordination between the parts, because the subagents cannot see each other's context and will step on the shared thing. A multi-agent run also costs on the order of 15 times the tokens of a single chat. Spend that only when the breadth is worth it.

## Delegate so workers do not collide

A vague subagent prompt produces overlap and gaps. Give each worker four things:

- a specific objective, narrow enough that two workers will not duplicate it
- the output format you want back
- guidance on which tools to use
- explicit boundaries on what to leave to other workers

Scale the effort to the task. A simple question wants one agent and a handful of tool calls. A complex one warrants ten or more subagents. Stating the scale in the lead's plan stops it from over- or under-spawning.

## Search broad, then narrow

Have agents open with broad queries to map the space, then tighten toward the specifics. Use extended or interleaved thinking in the lead for planning the decomposition and for judging what comes back, so the synthesis reacts to the findings rather than to the original plan.

## Let workers write to a filesystem

Route findings through a shared filesystem rather than funneling every detail back through the lead agent's context. Passing everything through the lead loses information at the bottleneck and burns its window. A worker that writes its result to a file lets the lead read what it needs when it needs it.

## Evaluate the end state

Start with around 20 real queries, not synthetic ones. Grade with an LLM-as-judge rubric covering accuracy, citation quality, completeness, source quality, and tool efficiency. Judge the final answer, not the path the agents took to reach it. Add human spot checks to calibrate the judge.

## Harden for real runs

- Checkpoint and resume on stateful errors, so a mid-run failure does not restart the whole thing.
- Observe the lead's decision patterns without reading private content, so you can see how it delegates.
- Budget tokens explicitly, given the 15x multiplier.
