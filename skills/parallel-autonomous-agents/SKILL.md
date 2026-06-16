---
name: parallel-autonomous-agents
description: >-
  Coordinate several unsupervised agents working on one shared git repo without
  collisions. Covers the autonomy loop that lets each agent pick the next task
  and respawn without a human, file-based lock files that claim work, machine-
  readable test output so a test suite steers the agents instead of a person,
  and context hygiene for long unattended runs. Use this whenever someone wants
  multiple agents grinding on one codebase in parallel, asks how to stop agents
  from duplicating work or clobbering each other, sets up an unattended or
  overnight agent run, or asks how agents claim and release tasks. Trigger on
  "parallel agents on one repo," "agents keep doing the same task," "autonomy
  loop," "unsupervised agents," and similar. Not for breadth-first research
  across subagents (that's multi-agent-orchestration) or crash-recovery
  architecture (that's durable-agent-architecture).
---

# Parallel autonomous agents

Source: [Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler). The lock-file mechanism exists as a standalone framework (`claude_code_agent_farm`); the autonomy loop exists as other skills. No skill packages the two together for a shared git repo, and most skills coordinate by git worktree instead, which this contrasts against.

The goal is sustained parallel progress on one codebase with nobody watching. Several agents run at once, each claiming work, doing it, and moving to the next thing on its own. Two mechanisms make that safe: a loop that keeps each agent going, and a lock protocol that keeps them off each other's toes.

## The autonomy loop

Each agent runs in a loop that picks the next task, does it, and respawns without pausing for a human. A simple shape is a script that calls a headless agent CLI (`claude -p`, `opencode run`, or any other) in a fresh container per session, so context never accumulates across tasks and a wedged session cannot poison the next. The loop is what turns a one-shot agent into one that works through a backlog overnight.

## Lock files claim work

Coordinate through the repo itself. To take a task, an agent writes a lock file naming it, then works on an isolated clone:

1. Claim by writing `current_tasks/<task>.txt`.
2. Work on a private clone of the repo.
3. Pull and merge upstream before pushing, so concurrent work integrates.
4. Push the result.
5. Remove the lock file.

Add stale-lock detection: if a lock is older than a threshold, assume the agent died and reclaim the task. Without it, one crash strands a task forever.

## Lock files or worktrees

This is the fork worth naming, because most existing skills take the other branch. Worktree isolation gives each agent its own checkout and merges later; it suits agents that should never see a shared state mid-flight. Lock files keep the agents on one shared history with a visible claim registry, which suits a team grinding a backlog where you want one integrated line of work and cheap coordination. Choose lock files when the shared registry and single history are the point.

## Let tests steer, not a person

With no human in the loop, the test suite is the steering wheel. Keep it comprehensive enough that passing means progress. Assign agents specialized roles, such as one on code quality, one on docs, one on optimization, so they pull in complementary directions instead of all chasing the same target.

Make test output machine-readable, because an agent greps it:

- emit single-line results like `ERROR: <reason>` that an agent can scan
- pre-compute aggregate stats rather than forcing each agent to recompute them live

## Keep context clean over long runs

Unattended runs live or die on context hygiene. Minimize the noise each command dumps into the window. Prefer deterministic, fast sampling so agents stay productive rather than wandering. Keep a running progress document so a fresh session picks up the state instead of rediscovering it.
