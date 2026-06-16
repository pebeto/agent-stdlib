---
description: Set up and explain the lock-file autonomy loop for running unsupervised agents on one shared repo.
argument-hint: [goal or path to a tasks file]
---

Help the user run the parallel-autonomous-agents pattern from this pack. Follow
the `parallel-autonomous-agents` skill.

Context for what they passed: $ARGUMENTS

The loop itself runs in the shell, not inside this session, because it spawns
many fresh `claude -p` sessions over time. Your job here is to set it up and
explain it, not to run an overnight loop yourself.

Do this:

1. **Build the task list.** If they gave a tasks file, use it. Otherwise turn
   their goal into a `tasks.txt` with one independent, self-contained task per
   line. Tasks that touch the same files should be separate lines so agents do
   not collide on them.

2. **Explain the coordination.** The lock registry (`scripts/locks.py`) is how
   agents avoid duplicating work: claiming a task atomically creates a lock file,
   and only one agent can win the race. Stale locks (from a crashed agent) get
   reaped after a threshold.

3. **Show how to launch.** Each agent is one copy of the loop runner:

   ```
   scripts/autonomy_loop.sh tasks.txt agent-1
   ```

   Run several copies in parallel (separate terminals or containers), each with
   a distinct agent id. They share `current_tasks/` and stay off each other's
   work.

4. **Point at the steering mechanism.** With no human in the loop, the test
   suite is the steering wheel. Confirm they have a comprehensive suite and that
   its output is machine-readable (single-line `ERROR: <reason>` results an agent
   can grep), per the skill.

Do not start a long-running loop from this session. Hand the user the commands
and let them run it where they can watch it.
