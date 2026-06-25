# agent-stdlib

A standard library for building agents.

Anthropic's engineering blog documents how to build, evaluate, and run agents in production. Most of that knowledge never ships as something you can install; it stays prose you reopen when you hit the problem it solves. `agent-stdlib` packages the parts nobody else has: Claude Code skills, a few MCP servers, and a tool-gating hook.

Each component names the article it comes from and says how it differs from any skill that already covers similar ground. The pack ships only what was missing. Topics that strong community skills already handle stay out, with pointers below.

## Skills

| Skill | What it gives you | Source article |
|-------|-------------------|----------------|
| `build-agent-evals` | Build automated evals for an agent: pick a grader, choose pass@k vs pass^k, run the zero-to-one roadmap | [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) |
| `calibrate-eval-infrastructure` | Stop container resource limits from swinging benchmark scores more than the models do | [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise) |
| `coding-agent-scaffold` | Design the two-tool (bash + file editor) interface for a coding agent so the model stops misusing it | [Raising the bar on SWE-bench Verified](https://www.anthropic.com/engineering/swe-bench-sonnet) |
| `durable-agent-architecture` | Split an agent service into brain, hands, and session so any part can crash and resume | [Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents) |
| `sandboxing-agentic-systems` | Contain an agent that runs code or reads untrusted content, layer by layer | [How we contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude) |
| `defending-against-prompt-injection` | Keep an agent from obeying instructions hidden in the pages, emails, and files it reads | [Mitigate jailbreaks and prompt injection](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks) |
| `using-the-think-step` | Decide when a mid-task reasoning step helps and how to prompt for it | [The "think" tool](https://www.anthropic.com/engineering/claude-think-tool) |
| `multi-agent-orchestration` | Run an orchestrator-worker research system with parallel subagents | [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) |
| `parallel-autonomous-agents` | Coordinate unsupervised agents on one git repo with lock files and an autonomy loop | [Building a C compiler with parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) |

## Install

Add the marketplace and install the plugin:

```
/plugin marketplace add pebeto/agent-stdlib
/plugin install agent-stdlib@agent-stdlib
```

Skills trigger themselves when a task matches their description. You can also load one explicitly with the `Skill` tool.

## MCP servers

Three servers live under `mcp-servers/`, each paired with a skill. They need [`uv`](https://docs.astral.sh/uv/), which installs each server's one dependency from the script header on first run.

- **think** (enabled). The no-op `think` tool, paired with `using-the-think-step`.
- **tool-gateway** (enabled). `search_tools` and `call_tool` over a larger catalog, so the agent reaches many tools through two. Paired with the tool-scaling guidance in `advanced-tool-use`.
- **code-execution** (opt-in). Presents tools as importable code and runs composed Python in a subprocess. It executes model-written code, so it is not enabled by default. Turn it on once you have wrapped it in real isolation; see `mcp-servers/code-execution/README.md` and the `sandboxing-agentic-systems` skill.

`think` and `tool-gateway` are wired into the plugin's `.mcp.json`. To enable `code-execution`, point your client's MCP config at `uv run .../mcp-servers/code-execution/server.py`.

## Commands, agent, and hooks

- **`/research <question>`** runs the orchestrator-worker flow: it decomposes the question, dispatches `research-worker` subagents in parallel, and synthesizes a cited answer. Paired with `multi-agent-orchestration`.
- **`/autonomous-loop`** sets up lock-file coordination for unsupervised agents on one repo, using `scripts/locks.py` and `scripts/autonomy_loop.sh`. Paired with `parallel-autonomous-agents`.
- **action-gating** is a `PreToolUse` hook that tiers Bash commands by risk and denies or asks on the dangerous ones. It stays off until you set `AGENT_STDLIB_GATING=warn` or `enforce`, and it only ever adds friction. See `hooks/README.md`.
- **injection-screening** is a `PostToolUse` hook that flags likely prompt-injection markers in fetched tool output and, on a hit, warns the agent or blocks it from acting until you confirm. Off until you set `AGENT_STDLIB_INJECTION=warn` or `enforce`. Paired with `defending-against-prompt-injection`. See `hooks/README.md`.

## Beyond Claude Code

Most of this pack is not Claude-specific. The MCP servers speak the open MCP protocol, the scripts are plain Python and Bash, and the skill content is harness-neutral procedural knowledge. To use it in OpenCode, Cursor, Cline, or a custom agent on any model, see [AGENTS.md](AGENTS.md), which maps each component to its portable form.

## Already covered elsewhere

These topics from the same blog have solid community skills, so they stay out of this pack. Reach for these instead:

- **Choosing an agent pattern** (prompt chaining, routing, orchestrator-workers): `markpitt/claude-skills` → `agent-patterns`
- **Context engineering** (compaction, note-taking, just-in-time retrieval): `muratcankoylan/agent-skills-for-context-engineering`
- **Designing agent or MCP tools** (consolidation, namespacing, token-efficient responses): the same pack's `tool-design`
- **Long-running build harness** (initializer + coding agent, git-tracked state): `eddiearc/long-running-harness`
- **GAN-style generator/evaluator harness**: `affaan-m/everything-claude-code` → `gan-style-harness`
- **Contextual retrieval RAG**: packaged versions exist on mcpmarket

## Provenance

This pack distills public writing on the Anthropic engineering blog. It is an independent project with no endorsement from Anthropic, and it ships no Anthropic code.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Each skill stands alone in `skills/<name>/SKILL.md` and opens with the article it distills.

## License

MIT. See [LICENSE](LICENSE).
