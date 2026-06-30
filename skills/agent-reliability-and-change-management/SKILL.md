---
name: agent-reliability-and-change-management
description: >-
  Ship a change to a running agent without degrading it, and keep a long-running
  agent reliable. Covers gating every system-prompt or model change behind a
  broad eval run, rolling out in stages and watching for report spikes, treating
  the agent's reasoning or thinking state as an invariant a cache must not drop,
  giving a long run external queryable memory in place of a bigger context
  window, and putting deterministic limits on consequential actions. Use this
  when someone edits an agent's system prompt, rolls out a model change, runs an
  agent unattended for hours or days, sees quality drop with no code change, or
  designs guardrails for an agent that spends money or acts on the world. Trigger
  on "agent quality regressed," "system prompt change," "agent got worse after
  deploy," "long-running agent drifts," and similar. This is operating and
  changing a shipped agent; structuring it to crash and resume is
  durable-agent-architecture, and measuring it is build-agent-evals.
---

# Agent reliability and change management

Source: [A postmortem of three recent issues](https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues), [an update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem), and [Project Vend](https://www.anthropic.com/research/project-vend-1). `durable-agent-architecture` keeps the service alive when a part crashes; this skill keeps the agent good after you change it and over a long run.

## Gate every change behind an eval run

A one-line system-prompt edit can drop quality across the board, and you will not catch it by reading a few transcripts. Run a broad eval suite for every system-prompt or model change before it ships, and ablate to find which change moved the number. A model recovers well from a single mistake, so a regression hides until you measure it at scale.

## Scope a change to its target

A change meant for one model can degrade another. Gate model-specific edits to the model they target, route by an exact match, and test that routing on the boundary cases (idle sessions, state transitions, the moment a cache fills) that skip your normal review.

## Roll out in stages and watch

Ship to a slice of traffic first, hold it there long enough to read the signal, then widen. Wire a feedback path, such as a `/bug` command or a thumbs-down, and watch for a spike in reports that lines up with a deploy. A correlated spike is your fastest regression detector.

## Treat reasoning state as an invariant

A cache change that dropped the agent's thinking blocks each turn made it forgetful and repetitive. The reasoning history is load-bearing. When you optimize the request path, assert that thinking and tool state survive the change, and add an integration test on the turn-to-turn boundary where caching bugs hide.

## Give a long run external memory

A long-running agent that leans on its context window drifts: it loses track of earlier commitments and starts to confuse its own state. Project Vend's shop agent invented details and lost the thread over days. Give it a place to write decisions and read them back, such as a log or a record store it queries, in place of trusting a longer window to hold everything.

## Put deterministic limits on consequential actions

An agent that spends money, grants access, or signs an agreement can be talked into a bad one. Anthropic's shop agent gave away discounts and came close to committing to a losing contract. Put fixed limits around the stakes: a price floor, an approval step above a threshold, a required verification before a quote. The limit does not depend on the model staying skeptical.

## Common mistakes

- Reading a handful of transcripts and calling a prompt change safe.
- Shipping to all traffic at once with no rollback signal wired.
- Letting a performance optimization drop reasoning or tool state unnoticed.
- Trusting a bigger context window to keep a multi-day agent on track.
- Leaving a money-or-access decision to the model's judgment alone.
