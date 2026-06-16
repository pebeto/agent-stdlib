# Hooks (Phase 3)

Hooks enforce behavior the model cannot be trusted to enforce on itself.

- **action-gating** — a PreToolUse hook from [Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode). It tiers actions by risk and runs a classifier on the flagged ones, so a tool call clears an independent check before it runs. This sits outside the model on purpose: an agent asked to gate its own actions can argue itself into approval, so the gate has to live in the harness. Lands here as `hooks.json` plus the classifier.
