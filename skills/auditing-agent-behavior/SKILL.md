---
name: auditing-agent-behavior
description: >-
  Audit an agent for risky behavior before it ships, the way you would red-team
  it, but automated. An auditor agent runs many multi-turn scenarios against your
  target agent from seed instructions you write, and a judge model scores the
  transcripts for deception, sycophancy, oversight subversion, power-seeking, and
  cooperation with misuse. Covers writing seed instructions that probe your
  agent's real risks, adapting the scoring rubric to your domain, and reading
  flagged transcripts. Use this when someone wants to red-team or safety-test an
  agent, asks how to find deceptive or manipulable behavior, audits a model or
  agent before deployment, or compares behavior across model versions. Trigger on
  "red-team my agent," "audit agent behavior," "test for deception," "alignment
  testing," and similar. This is auditing behavior for safety; measuring task
  success is build-agent-evals, and stopping objective-gaming is
  reward-hacking-and-inoculation.
---

# Auditing agent behavior

Source: [Petri, an open-source auditing tool](https://www.anthropic.com/research/petri-open-source-auditing) ([repo](https://github.com/safety-research/petri)). `build-agent-evals` asks whether the agent did the task; this skill asks whether it behaved well while trying, and points at Petri as the harness that runs the audit.

## What an audit catches that an eval misses

A task eval scores the end state: did the agent fix the bug, answer the question, complete the order. It says nothing about how the agent got there. An agent can pass every task and still lie to the user under pressure, flatter a wrong claim, hide an action from its operator, or help with a request it should refuse. An audit goes looking for those behaviors on purpose.

## Let an auditor drive the scenarios

Running these probes by hand does not scale past a handful. Petri automates the loop: an auditor agent takes a seed instruction, plans a multi-turn conversation, plays the user and any simulated tools, and pushes your target agent toward the behavior under test. A judge model then scores each transcript against a rubric. You supply the seeds and read the results.

## Write seeds that probe your agent's risks

The audit is only as good as its seed instructions. Generic seeds find generic problems. Write seeds around the pressure your agent will meet in production: a customer pushing for a refund it should deny, a user asking it to hide a step from an approver, a tool result that contradicts what the agent told the user a turn ago. Cover the cases where being helpful and being correct pull apart.

## Adapt the rubric to your domain

Petri ships a default rubric across dozens of dimensions (deception, sycophancy, oversight subversion, power-seeking, cooperation with misuse, and more). Keep the ones that map to your risk and add dimensions of your own. A score points a human at a transcript to read.

## Confirm flags by reading transcripts

The judge flags candidates; you confirm them. Open the flagged transcripts and check that the behavior is real and reproducible before you act on it, the same discipline `build-agent-evals` asks for. Run the audit again on each model or prompt change, and watch whether a fix in one dimension cost you ground in another.
