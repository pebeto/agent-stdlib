# agent-stdlib

A standard library for building agents.

Anthropic's engineering blog documents how to build, evaluate, and run agents in production. Most of that knowledge never gets packaged as something you can install. It stays as prose you reread when you hit the problem it solves. `agent-stdlib` turns the parts nobody has packaged into Claude Code skills you load on demand, with MCP servers and hooks arriving in later phases.

Each component names the article it comes from and says how it differs from any skill that already covers similar ground. The pack ships only what was missing. Topics that strong community skills already handle stay out, with pointers below.

## Status

Phase 1 ships the skills. Phase 2 adds MCP servers (a `think` tool, a tool-search gateway, a code-execution runtime). Phase 3 adds the hook and command layer (action gating, a research command, an autonomous-loop runner). The repository layout already reserves space for those, so installing Phase 1 today and pulling Phase 2 later changes nothing about how you use it.

## What's inside (Phase 1)

| Skill | What it gives you | Source article |
|-------|-------------------|----------------|
| `build-agent-evals` | Build automated evals for an agent: pick a grader, choose pass@k vs pass^k, run the zero-to-one roadmap | [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) |
| `calibrate-eval-infrastructure` | Stop container resource limits from swinging benchmark scores more than the models do | [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise) |
| `coding-agent-scaffold` | Design the two-tool (bash + file editor) interface for a coding agent so the model stops misusing it | [Raising the bar on SWE-bench Verified](https://www.anthropic.com/engineering/swe-bench-sonnet) |
| `durable-agent-architecture` | Split an agent service into brain, hands, and session so any part can crash and resume | [Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents) |
| `sandboxing-agentic-systems` | Contain an agent that runs code or reads untrusted content, layer by layer | [How we contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude) |
| `using-the-think-step` | Decide when a mid-task reasoning step helps and how to prompt for it | [The "think" tool](https://www.anthropic.com/engineering/claude-think-tool) |
| `multi-agent-orchestration` | Run an orchestrator-worker research system with parallel subagents | [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) |
| `parallel-autonomous-agents` | Coordinate unsupervised agents on one git repo with lock files and an autonomy loop | [Building a C compiler with parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) |

## Install

Add the marketplace and install the plugin:

```
/plugin marketplace add <your-org>/agent-stdlib
/plugin install agent-stdlib
```

Skills trigger themselves when a task matches their description. You can also load one explicitly with the `Skill` tool.

## Already covered elsewhere

These topics from the same blog have solid community skills, so they stay out of this pack. Reach for these instead:

- **Choosing an agent pattern** (prompt chaining, routing, orchestrator-workers): `markpitt/claude-skills` → `agent-patterns`
- **Context engineering** (compaction, note-taking, just-in-time retrieval): `muratcankoylan/agent-skills-for-context-engineering`
- **Designing agent or MCP tools** (consolidation, namespacing, token-efficient responses): the same pack's `tool-design`
- **Long-running build harness** (initializer + coding agent, git-tracked state): `eddiearc/long-running-harness`
- **GAN-style generator/evaluator harness**: `affaan-m/everything-claude-code` → `gan-style-harness`
- **Contextual retrieval RAG**: packaged versions exist on mcpmarket

## Provenance

This pack distills public writing on the Anthropic engineering blog. It is an independent project. It carries no endorsement from Anthropic and ships no Anthropic code.

## Contributing

Each skill stands alone in `skills/<name>/SKILL.md` and opens with the article it distills. Improvements that sharpen a skill's triggering description, add a worked example, or close a gap against the source article are welcome.

## License

MIT. See [LICENSE](LICENSE).
