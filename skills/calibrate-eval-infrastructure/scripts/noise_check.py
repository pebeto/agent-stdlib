#!/usr/bin/env python3
"""Test whether container/runtime configuration is moving a benchmark score.

Run your benchmark several times under each resource configuration, then feed
the scores here. The script runs a label-permutation test on the between-group
variation: it asks how often a random reassignment of runs to configs produces
between-config spread as large as what you observed. A high p-value means the
configuration is not distinguishable from noise (good: the box is not deciding
the benchmark). A low p-value means configuration is still moving the score, so
widen the headroom band and rerun before trusting a single number.

Input JSON shape (each config lists scores from repeated runs):

    {
      "configs": {
        "mem-1x": [60.4, 61.8, 60.1, 62.0],
        "mem-2x": [63.5, 64.0, 63.2, 64.1],
        "mem-3x": [64.2, 64.0, 64.4, 64.1]
      }
    }

Usage:
    python noise_check.py --scores scores.json [--iters 20000] [--seed 0]
"""
import argparse
import json
import random
import sys

WITHIN_NOISE = 0.40  # the article treats roughly this and above as within noise


def between_group_ss(groups):
    """Between-group sum of squares: the spread of group means."""
    all_vals = [v for g in groups for v in g]
    grand = sum(all_vals) / len(all_vals)
    return sum(len(g) * (sum(g) / len(g) - grand) ** 2 for g in groups if g)


def permutation_p(groups, iters, rng):
    observed = between_group_ss(groups)
    sizes = [len(g) for g in groups]
    pool = [v for g in groups for v in g]
    hits = 0
    for _ in range(iters):
        rng.shuffle(pool)
        i, perm = 0, []
        for n in sizes:
            perm.append(pool[i:i + n])
            i += n
        if between_group_ss(perm) >= observed - 1e-12:
            hits += 1
    return observed, (hits + 1) / (iters + 1)  # add-one keeps p in (0, 1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scores", required=True, help="path to scores JSON")
    ap.add_argument("--iters", type=int, default=20000, help="permutations")
    ap.add_argument("--seed", type=int, default=0, help="rng seed")
    args = ap.parse_args()

    with open(args.scores) as f:
        configs = json.load(f)["configs"]

    groups = [v for v in configs.values() if v]
    if len(groups) < 2:
        print("need at least two configs with scores", file=sys.stderr)
        return 1
    if any(len(g) < 2 for g in groups):
        print("each config needs at least two runs to separate signal from noise",
              file=sys.stderr)
        return 1

    print(f"{'config':<16} {'runs':>5} {'mean':>8} {'min':>8} {'max':>8}")
    for name, vals in configs.items():
        if vals:
            m = sum(vals) / len(vals)
            print(f"{name:<16} {len(vals):>5} {m:>8.2f} {min(vals):>8.2f} {max(vals):>8.2f}")

    _, p = permutation_p(groups, args.iters, random.Random(args.seed))
    spread = max(sum(g) / len(g) for g in groups) - min(sum(g) / len(g) for g in groups)
    print(f"\nmean spread across configs: {spread:.2f} points")
    print(f"permutation p-value: {p:.3f}")
    if p >= WITHIN_NOISE:
        print(f"verdict: within noise (p >= {WITHIN_NOISE}). "
              f"Configuration is not deciding the score; model deltas are trustworthy.")
    else:
        print(f"verdict: configuration is still moving the score (p < {WITHIN_NOISE}). "
              f"Widen the headroom band and rerun.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
