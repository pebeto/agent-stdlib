# Contributing

This pack distills Anthropic's engineering blog, research, and docs into
installable, mostly harness-neutral components. A contribution earns its place by
closing a gap another skill leaves open.

## Proposing a new skill

Before writing one, check two things:

1. **It traces to a specific article.** Every component names its source. If the
   procedure does not come from a documented practice, it belongs in a different
   repo.
2. **No existing skill already covers it well.** Search the public skill
   ecosystem first. If a solid skill exists, improve that one, or state plainly
   how yours differs. The README's "Already covered elsewhere" list shows the
   topics this pack deliberately skips.

## Skill layout

Each skill stands alone:

```
skills/<name>/
  SKILL.md            # required
  scripts/            # optional, only for deterministic work
  references/         # optional, loaded on demand
```

`SKILL.md` opens with a `Source:` line linking the article, followed by a
one-line note on the prior art it improves on. Write the `description`
frontmatter so the skill fires when a task matches and stays quiet on the
near-misses; that field decides whether the skill is ever used.

## Scripts

Keep bundled scripts dependency-free where you can. The ones in this pack run on
a standard Python install with no third-party packages, so anyone can run them
without a setup step. Hold that bar unless a dependency is unavoidable.

## Prose

Write the way the existing skills read: direct, specific, active voice, no
filler. Run a slop check before you open a pull request.

## Where a contribution goes

Knowledge the model reads and applies is a skill, under `skills/`. A capability
the agent calls at runtime is an MCP server, under `mcp-servers/`. Behavior the
harness must enforce, because the model cannot be trusted to enforce it on
itself, is a hook under `hooks/`. Commands and agents in `commands/` and
`agents/` wrap any of these into one-step invocations.
