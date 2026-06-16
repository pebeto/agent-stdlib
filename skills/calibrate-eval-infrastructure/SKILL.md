---
name: calibrate-eval-infrastructure
description: >-
  Stop the machine from deciding your benchmark. Configure and validate the
  container and runtime resources for an agentic coding eval so infrastructure
  noise stays inside statistical bounds instead of swinging scores more than the
  models do. Use this whenever someone runs SWE-bench or any agentic coding
  benchmark in containers, sees scores jump between runs for no code reason,
  suspects OOM kills or flaky infra are skewing results, sets container memory
  or CPU limits for an eval harness, or wants to trust a leaderboard delta.
  Trigger on "my benchmark scores are inconsistent," "OOM during eval," "how
  much memory should the eval container get," and similar.
---

# Calibrate eval infrastructure

Source: [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise). This had no packaged skill anywhere; the topic existed only as the article and a few summaries.

Container configuration can move an agentic coding benchmark by 6 or more points. That is larger than the gap between the top models, which means a careless resource setting can rank a worse model above a better one. Treat resource configuration as an experimental variable you control and report, on the same footing as prompt format and sampling temperature.

## The mistake that causes most of it

A container has two separate numbers, and pinning them together is the trap:

- a **guaranteed allocation**, the floor the workload always has, and
- a **hard kill threshold**, the ceiling past which the runtime kills the process.

Set the floor equal to the ceiling and the workload has zero headroom. A normal memory spike crosses the line and the process dies an OOM death that looks like the agent failing the task. It was not the agent. It was the box.

Give the two numbers separate values and leave a band between them.

## Size the band empirically

Do not guess the headroom. Sweep it and measure whether the score still moves:

1. Run the benchmark at several ceilings (a useful starting reference is roughly 3x the baseline ceiling; Anthropic's sweep cut infra errors from 5.8% to 2.1% with negligible score change at that point).
2. Run each configuration several times, because one run per config cannot separate signal from noise.
3. Test whether the score differences across configurations are distinguishable from noise. If they are not, you have found a band wide enough that the infrastructure no longer decides the outcome.

The bundled script runs that test:

```
python scripts/noise_check.py --scores scores.json
```

It reports a permutation p-value across your configs. A high p-value (the article treats roughly 0.40 and above as within noise) means resource configuration is no longer moving the score, so any model differences you measure are real. A low p-value means the infrastructure is still talking, and you need a wider band before you trust a single number. See `scripts/noise_check.py` for the input format.

## A subtler effect

The headroom band also changes *what the benchmark rewards*. A tight band quietly favors lean code and penalizes an agent that spins up heavyweight tooling, even when the heavyweight approach is correct. So document the band you chose: it is part of what the benchmark measures, not a detail.

## The other noise sources

Memory is the loudest, not the only one. Control these too, or hold them constant and say so:

- time of day (shared-infra contention)
- API latency and rate-limit backoff
- hardware specs of the runner
- concurrency level (how many trials share a host)
- egress bandwidth for tasks that fetch dependencies

## Reading someone else's leaderboard

Distrust a difference smaller than about 3 points unless the eval documents its resource and infrastructure configuration and you can match it. An undocumented harness makes a small delta meaningless.
