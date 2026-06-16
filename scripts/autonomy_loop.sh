#!/usr/bin/env bash
# Reference autonomy loop for parallel agents on one shared git repo.
#
# Each agent runs this loop: reap stale locks, then walk a task list, claim the
# first unclaimed task via the lock registry, run a fresh `claude -p` session on
# it, release the lock, and move on. Run several copies at once (one per terminal
# or container) and the lock files keep them off each other's tasks.
#
# This is a reference. A production loop would run continuously rather than once
# through the file, isolate each session in a fresh container, and pull/merge
# before pushing. See the parallel-autonomous-agents skill.
#
# Usage:
#   ./autonomy_loop.sh <tasks-file> [agent-id]
# where <tasks-file> has one task description per line.
set -euo pipefail

TASKS_FILE="${1:?usage: autonomy_loop.sh <tasks-file> [agent-id]}"
AGENT_ID="${2:-agent-$$}"
LOCK_DIR="current_tasks"
LOCKS="$(dirname "$0")/locks.py"

# Reclaim tasks abandoned by agents that died (locks older than 2 hours).
python3 "$LOCKS" reap --max-age 7200 --dir "$LOCK_DIR" || true

while IFS= read -r task || [ -n "$task" ]; do
  [ -z "$task" ] && continue
  if python3 "$LOCKS" claim "$task" --agent "$AGENT_ID" --dir "$LOCK_DIR" 2>/dev/null; then
    echo "[$AGENT_ID] working: $task"
    # A fresh, isolated session per task so context never accumulates across
    # tasks. Adjust the prompt and flags (e.g. --allowedTools) to your repo.
    claude -p "Work on this task to completion, then stop. Task: $task" || true
    python3 "$LOCKS" release "$task" --dir "$LOCK_DIR"
    echo "[$AGENT_ID] done: $task"
  else
    echo "[$AGENT_ID] skip (already claimed): $task"
  fi
done < "$TASKS_FILE"

echo "[$AGENT_ID] task list exhausted"
