---
name: constitutional-classifiers
description: >-
  Screen an agent's input and output against a policy you write, so it refuses
  the content classes you disallow without over-refusing the ones you allow.
  Covers writing a constitution that lists allowed and disallowed content for your
  app, screening user input before the model and model output before delivery,
  generating synthetic examples from the constitution to test and harden the
  screen, setting a stricter policy for an autonomous agent than for a chat
  assistant, and tracking the over-block rate. Use this when someone needs content
  guardrails on an agent, wants to block a category of request or output, hardens
  an agent against jailbreaks, or deploys an agent in an abuse-prone or regulated
  domain. Trigger on "content policy for my agent," "block disallowed output,"
  "jailbreak defense," "input and output filtering," and similar. This is policy
  screening of agent I/O; keeping the agent from obeying instructions hidden in
  the content it reads is defending-against-prompt-injection.
---

# Constitutional classifiers

Source: [Constitutional classifiers](https://www.anthropic.com/research/constitutional-classifiers) and the [next-generation version](https://www.anthropic.com/research/next-generation-constitutional-classifiers). `defending-against-prompt-injection` guards the trust boundary on content the agent reads; this skill guards a content policy on what the agent takes in and sends out. The two stack.

## Write the constitution first

A classifier is only as clear as the policy behind it. Write a constitution: a plain-language list of the content classes your agent may produce and the ones it may not, with the line between them drawn by example. The canonical pair is "a recipe for mustard is allowed; a recipe for mustard gas is not." Concrete examples beat abstract categories, because the screen learns the boundary you drew rather than the one you meant.

## Screen both ends

Put a classifier on each end of the model. An input classifier reads the user's request before the model sees it; an output classifier reads the completion before it reaches the user. Two ends catch two failures: a request that should never be answered, and a harmful completion that slipped through despite a clean-looking request. For an agent, screen tool outputs and intermediate steps too, which is where this meets `defending-against-prompt-injection`.

## Harden the screen with synthetic data

You will not anticipate every phrasing of a banned request. Generate synthetic examples from the constitution, translate them into other languages, and rewrite them in known jailbreak styles, then check that the screen still catches them. The gap between what the constitution says and what the screen catches is your attack surface, and the synthetic set is how you measure it.

## Match the policy to the autonomy

An agent that acts on the world needs a stricter policy than an assistant that only talks. Set tighter classes for an autonomous agent, and loosen them for a supervised chat surface. Keep the constitution in version control and add to it as new attack vectors show up, without retraining the base model.

## Mind the cost of a wrong block

A screen that blocks too much is its own failure: it refuses work the user is entitled to. Track the over-block rate on benign requests alongside the catch rate on disallowed ones, and tune the constitution where the two trade off. When a guardrail blocks too much, someone disables it, and the protection is gone.
