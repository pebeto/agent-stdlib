---
name: coding-agent-scaffold
description: >-
  Design the tool interface for a coding agent so the model stops misusing it.
  Covers the minimal two-tool scaffold (a bash tool plus a file editor), exact
  single-match string replacement, absolute-path rules, and error-proofing the
  tool descriptions so common model mistakes become impossible. Use this
  whenever someone is building a coding agent or SWE-bench-style harness,
  designing a bash or file-edit tool for an agent, deciding how much scaffolding
  to impose, or debugging an agent that keeps editing the wrong place, fumbling
  multi-line edits, or escaping shell commands wrong. Trigger on "build a coding
  agent," "str_replace tool," "agent keeps breaking the file," and similar.
  Not for general MCP or service tool design; this is the bash plus
  file-editor interface specifically.
---

# Coding agent scaffold

Source: [Raising the bar on SWE-bench Verified with Claude 3.5 Sonnet](https://www.anthropic.com/engineering/swe-bench-sonnet). The procedure circulates as tutorials and reference codebases (Thorsten Ball's "How to build an agent" is the canonical one). None ship it as a skill focused on tool-interface design, which is the part that decides reliability.

A strong coding agent does not need elaborate scaffolding. It needs two tools designed with the care you would give a UI, and the freedom to decide its own order of operations. The scaffolding encodes your guesses about what the model cannot do, and those guesses age badly as models improve. Keep it thin.

## Give the model control, suggest the order

Do not hard-code a rigid pipeline. In the prompt, suggest a shape and let the model deviate when the task calls for it: explore the code, reproduce the problem, make the fix, verify it, then check edge cases. A suggested sequence guides without boxing in a model that often knows a better route for the specific bug.

Let the agent keep sampling until it finishes or hits the context limit. Expect a high token and turn count on hard tasks; that is the cost of letting the model work the problem.

## Tool 1: bash

One parameter, a single command string. No XML wrapping, no escaping scheme the model has to satisfy on top of normal shell quoting.

Write the description the way you would brief a careful new engineer on an unfamiliar machine. Cover the things the model cannot see and will otherwise assume wrong:

- how shell quoting and escaping work in this environment
- which packages and interpreters are available
- whether state persists between calls (does `cd` or an exported variable survive to the next command)
- how to run something in the background, and how to read its output later

Steer the model away from commands that dump huge output into the context. A `find /` or an unbounded log tail wastes the window it needs for the actual task.

## Tool 2: file editor

Give it a small, explicit verb set: `view`, `create`, `str_replace`, `insert`, `undo_edit`. Two design choices prevent most edit failures:

- **Absolute paths only.** Relative paths depend on a working directory the model is tracking in its head, and it tracks it wrong often enough to matter.
- **`str_replace` matches exactly one occurrence.** The old string must appear once. If it appears zero times or several times, the tool refuses and says which, instead of editing the wrong line and corrupting the file. This single rule removes a whole class of silent damage.

## Error-proof the descriptions (poka-yoke)

Every recurring mistake the model makes is a gap in a tool description, not a flaw in the model. When you watch a transcript and see the agent trip on the same thing twice, write the limitation and the edge case directly into the tool description so the mistake becomes hard to make:

- the editor rejects a non-unique `str_replace` and tells the model to add surrounding context until the match is unique
- the bash tool states its output is truncated past some size, so the model pipes through `head` or greps instead of paging everything
- the editor states paths must be absolute, with an example

This is the highest-leverage work in the whole scaffold. A tool that explains its own failure modes turns a confused agent into a competent one without touching the model.
