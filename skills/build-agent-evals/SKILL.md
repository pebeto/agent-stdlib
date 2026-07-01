---
name: build-agent-evals
description: >-
  Build automated evaluations for an AI agent from scratch: collecting tasks
  from real failures, choosing code/model/human graders, picking pass@k vs
  pass^k, building an isolated harness, and keeping the suite honest over time.
  Use this whenever someone wants to measure, benchmark, or regression-test an
  agent, write an eval harness for an LLM agent, decide how to grade
  non-deterministic output, set up an LLM-as-judge, or asks any version of "how
  do I know if my agent is actually getting better." Trigger even when they say
  "tests for my agent," "eval set," or "agent benchmark" rather than the word
  "evals," or when they ask about benchmark contamination or a model recognizing
  the eval. Not for container or resource limits making scores flaky across
  runs; that's calibrate-eval-infrastructure.
---

# Build agent evals

Source: [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), with the section on keeping evals honest drawing on [Eval awareness in BrowseComp](https://www.anthropic.com/engineering/eval-awareness-browsecomp) and [Designing AI-resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations). A standalone gist of the core material exists but is undiscoverable; this skill packages it and adds the runnable metric script.

An eval tells you whether a change to an agent made it better or worse. Without one you are guessing from vibes, and vibes miss regressions that only show up on the tenth run. Treat the eval suite the way you treat a unit-test suite: it has an owner, it grows when bugs slip through, and it fails loudly.

## Start from real failures

Collect 20 to 50 tasks before writing any grader. The best sources are bugs your agent already produced, support tickets, and manual test cases you keep rerunning by hand. Write each task so two experts reading it reach the same verdict on pass or fail. If you cannot decide whether an output passed, the task is underspecified and will poison every measurement built on it.

Include a reference solution for each task to prove it is solvable, and build both positive cases (the agent should do X) and negative cases (the agent should refuse, or should not touch Y). A suite made only of positive cases optimizes toward an agent that does too much.

## Choose the grader to match the task

Grade what the agent produced, not the path it took. An agent that reaches the right end state by an unusual route still passed.

- **Code-based grader.** String match, schema validation, a state check against a database or filesystem. Use this wherever the correct answer is checkable by a program. It is fast, free, and never flaky in the way a model judge is.
- **Model-based grader (LLM-as-judge).** A rubric scored by a separate model call. Use it for output that needs judgment: tone, summary quality, whether an explanation is correct. Give the judge a rubric with explicit criteria rather than asking "is this good," and have it cite evidence for its score so you can audit it.
- **Human grader.** Subject-matter spot checks and A/B preference. Use it sparingly to calibrate the other two, not as the everyday loop.

For tasks with several components, award partial credit per component instead of one all-or-nothing verdict. Partial credit shows you which part regressed.

## Pick a metric that respects non-determinism

An agent run twice gives two answers. One pass tells you little. Run each task k times and report the metric that matches what you care about:

- **pass@k** measures capability: at least one of k runs succeeded. Use it when you want to know whether the agent *can* do the task.
- **pass^k** measures reliability: all k runs succeeded. Use it when a single failure in production is expensive, which for most shipped agents it is.

The bundled script computes both from a list of per-run outcomes:

```
python scripts/passk.py --results results.json --k 5
```

See `scripts/passk.py` for the input format. Report both numbers early; the gap between them is your reliability problem stated as a single figure.

## Keep the harness clean

Start every trial from a fresh, isolated environment. A shared scratch directory or a database left dirty by the previous run produces correlated failures that look like an agent regression and are really a harness bug. Reset state per trial.

## Maintain the suite

- Read full transcripts on a schedule, not just the pass/fail column. A grader that passes a wrong answer is worse than no grader.
- Watch for saturation. When the suite hits near 100% pass, it has stopped discriminating; add harder tasks pulled from recent failures.
- Give the suite an owner. Unowned eval suites rot exactly like unowned tests.

## Keep the eval honest as the model improves

Two failure modes appear once the model is strong. Both inflate the score without a matching gain in skill.

- **Contamination.** If a task or its answer leaked into training data, or an earlier agent in your pipeline left notes a later one reads, the model scores high by recall. Hold out a set the model has never seen, refresh it, and check that one agent's output does not seed another's eval.
- **Eval awareness.** A capable model can notice it is inside a benchmark, name it, and shift how it acts, in one documented case locating the stored answers. A task that reads like a test invites this. Write tasks that look like real work, and treat a sudden jump on a familiar benchmark as a reason to inspect it.

As the model beats each version of the suite, push the new tasks toward novel, out-of-distribution problems rather than harder variants of what it already handles. A problem the model has seen measures memory rather than the skill you are testing.

## Common mistakes

- Grading the trajectory instead of the outcome, which punishes correct-but-unexpected solutions.
- One-sided suites that reward an agent for doing too much.
- A single run per task, reported as if it were the truth.
- An LLM judge with a vague prompt, whose scores nobody audits.
- A benchmark the model has seen or can recognize, whose score reflects memory over skill.
