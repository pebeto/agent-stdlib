#!/usr/bin/env python3
"""Compute pass@k (capability) and pass^k (reliability) for an agent eval run.

Input JSON shape:

    {
      "tasks": [
        {"id": "fix-login-bug", "outcomes": [true, false, true, true, true]},
        {"id": "refactor-parser", "outcomes": [true, true, true, true, true]}
      ]
    }

Each task lists the pass/fail result of every run you executed (n runs per task,
where n must be at least k). The estimators are the unbiased ones from the
HumanEval pass@k paper, so n may exceed k:

    pass@k = 1 - C(n-c, k) / C(n, k)        # at least one of k runs passes
    pass^k =     C(c,   k) / C(n, k)        # all k runs pass

Usage:
    python passk.py --results results.json --k 5
"""
import argparse
import json
import sys
from math import comb


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that a sample of k of the n runs contains >= 1 success."""
    if k > n:
        raise ValueError(f"k={k} exceeds n={n}")
    if c == 0:
        return 0.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def pass_pow_k(n: int, c: int, k: int) -> float:
    """Probability that a sample of k of the n runs are all successes."""
    if k > n:
        raise ValueError(f"k={k} exceeds n={n}")
    if c < k:
        return 0.0
    return comb(c, k) / comb(n, k)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", required=True, help="path to results JSON")
    ap.add_argument("--k", type=int, required=True, help="sample size k")
    args = ap.parse_args()

    with open(args.results) as f:
        data = json.load(f)

    tasks = data.get("tasks", [])
    if not tasks:
        print("no tasks found in results", file=sys.stderr)
        return 1

    rows, at_k_vals, pow_k_vals, skipped = [], [], [], []
    for t in tasks:
        outcomes = t["outcomes"]
        n, c = len(outcomes), sum(1 for o in outcomes if o)
        if args.k > n:
            skipped.append((t.get("id", "?"), n))
            continue
        a, p = pass_at_k(n, c, args.k), pass_pow_k(n, c, args.k)
        at_k_vals.append(a)
        pow_k_vals.append(p)
        rows.append((t.get("id", "?"), n, c, a, p))

    print(f"{'task':<32} {'n':>3} {'c':>3} {'pass@k':>8} {'pass^k':>8}")
    for tid, n, c, a, p in rows:
        print(f"{tid:<32} {n:>3} {c:>3} {a:>8.3f} {p:>8.3f}")

    if at_k_vals:
        suite_at = sum(at_k_vals) / len(at_k_vals)
        suite_pow = sum(pow_k_vals) / len(pow_k_vals)
        print("-" * 60)
        print(f"{'suite (k=' + str(args.k) + ')':<32} {'':>3} {'':>3} "
              f"{suite_at:>8.3f} {suite_pow:>8.3f}")
        print(f"\ncapability  pass@{args.k} = {suite_at:.3f}")
        print(f"reliability pass^{args.k} = {suite_pow:.3f}")
        print(f"gap (lost to non-determinism) = {suite_at - suite_pow:.3f}")

    for tid, n in skipped:
        print(f"skipped {tid}: only {n} runs, need k={args.k}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
