#!/usr/bin/env python3
"""A file-based lock registry for coordinating unsupervised agents on one repo.

Several agents grinding on a shared codebase need a way to claim work without
clobbering each other. This implements the lock protocol from Anthropic's
parallel-Claudes work: an agent claims a task by atomically creating a lock file,
works, then removes it. The atomic create (O_CREAT | O_EXCL) is the whole trick:
two agents racing for the same task, exactly one wins.

Commands:
    claim <task>    [--agent ID] [--dir D]   create a lock; exit 1 if held
    release <task>  [--dir D]                remove a lock (idempotent)
    list            [--dir D]                show held locks and their age
    reap            [--max-age S] [--dir D]  remove locks older than S seconds

Default dir is ./current_tasks. The task name can be anything; it is mapped to a
safe filename and the original is stored inside the lock.

See the parallel-autonomous-agents skill, and autonomy_loop.sh for the loop that
drives this.
"""
import argparse
import hashlib
import json
import os
import sys
import time

DEFAULT_DIR = "current_tasks"


def _lock_path(directory: str, task: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in task)[:80]
    digest = hashlib.sha1(task.encode()).hexdigest()[:8]
    return os.path.join(directory, f"{safe}.{digest}.lock")


def claim(args) -> int:
    os.makedirs(args.dir, exist_ok=True)
    path = _lock_path(args.dir, args.task)
    payload = json.dumps({"task": args.task, "agent": args.agent, "ts": time.time()})
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        holder = "unknown"
        try:
            with open(path) as f:
                holder = json.load(f).get("agent", "unknown")
        except (OSError, ValueError):
            pass
        print(f"already claimed by {holder}", file=sys.stderr)
        return 1
    with os.fdopen(fd, "w") as f:
        f.write(payload)
    print(f"claimed: {args.task}")
    return 0


def release(args) -> int:
    path = _lock_path(args.dir, args.task)
    try:
        os.unlink(path)
        print(f"released: {args.task}")
    except FileNotFoundError:
        print(f"no lock held for: {args.task}")
    return 0


def list_locks(args) -> int:
    if not os.path.isdir(args.dir):
        print("(no locks)")
        return 0
    now = time.time()
    rows = []
    for name in sorted(os.listdir(args.dir)):
        if not name.endswith(".lock"):
            continue
        try:
            with open(os.path.join(args.dir, name)) as f:
                d = json.load(f)
            rows.append((d.get("task", "?"), d.get("agent", "?"), now - d.get("ts", now)))
        except (OSError, ValueError):
            continue
    if not rows:
        print("(no locks)")
        return 0
    print(f"{'task':<40} {'agent':<20} {'age (s)':>8}")
    for task, agent, age in rows:
        print(f"{task:<40} {agent:<20} {age:>8.0f}")
    return 0


def reap(args) -> int:
    if not os.path.isdir(args.dir):
        return 0
    now, reaped = time.time(), 0
    for name in os.listdir(args.dir):
        if not name.endswith(".lock"):
            continue
        path = os.path.join(args.dir, name)
        try:
            with open(path) as f:
                ts = json.load(f).get("ts", now)
        except (OSError, ValueError):
            ts = now
        if now - ts > args.max_age:
            try:
                os.unlink(path)
                reaped += 1
                print(f"reaped stale lock: {name}")
            except OSError:
                pass
    print(f"reaped {reaped} stale lock(s) older than {args.max_age}s")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("claim"); c.add_argument("task"); c.add_argument("--agent", default=f"agent-{os.getpid()}"); c.add_argument("--dir", default=DEFAULT_DIR); c.set_defaults(fn=claim)
    r = sub.add_parser("release"); r.add_argument("task"); r.add_argument("--dir", default=DEFAULT_DIR); r.set_defaults(fn=release)
    l = sub.add_parser("list"); l.add_argument("--dir", default=DEFAULT_DIR); l.set_defaults(fn=list_locks)
    p = sub.add_parser("reap"); p.add_argument("--max-age", type=float, default=7200); p.add_argument("--dir", default=DEFAULT_DIR); p.set_defaults(fn=reap)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
