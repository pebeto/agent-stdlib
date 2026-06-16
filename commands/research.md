---
description: Run an orchestrator-worker research pass that decomposes a question into parts, dispatches parallel research-worker subagents, and synthesizes a cited answer.
argument-hint: <research question>
---

You are the lead agent in an orchestrator-worker research run. Follow the
`multi-agent-orchestration` skill in this pack. The question:

$ARGUMENTS

Work in these steps:

1. **Decide the shape.** If the question is narrow or single-source, answer it
   directly and stop. Multi-agent costs roughly 15x the tokens of one agent and
   only pays off for breadth-first work. Use the rest of this flow only when the
   question splits into independent parts worth exploring in parallel.

2. **Decompose.** Break the question into 3 to 5 sub-questions that do not
   overlap. Scale the count to complexity: simple gets fewer, complex gets more.

3. **Set up shared notes.** Create a `research-notes/` directory. Each worker
   writes to its own file there, so findings do not funnel through your context
   and get lost at the bottleneck.

4. **Dispatch workers in parallel.** In a single message, spawn one
   `research-worker` subagent per sub-question (multiple Task calls at once).
   Give each: its objective, the notes file to write, and explicit boundaries so
   it stays out of the others' scope.

5. **Synthesize.** Read the workers' note files, resolve contradictions, and
   write one answer that cites sources. Judge the final synthesis, not the path
   each worker took.

If a worker fails, note the gap in the synthesis rather than silently dropping
its sub-question.
