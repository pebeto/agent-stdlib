# Contributing

This pack distills Anthropic's engineering blog into installable Claude Code
components. A contribution earns its place by closing a gap, not by restating
what another skill already covers.

## Proposing a new skill

Before writing one, check two things:

1. **It traces to a specific article.** Every component names its source. If the
   procedure does not come from a documented practice, it belongs in a different
   repo.
2. **No existing skill already covers it well.** Search the public skill
   ecosystem first. If a solid skill exists, either improve that one or state
   plainly how yours differs. The README's "Already covered elsewhere" list
   shows the topics this pack deliberately skips.

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

Keep bundled scripts dependency-free where you can. The two in this pack run on
a standard Python install with no third-party packages, so anyone can run them
without a setup step. Hold that bar unless a dependency is unavoidable.

## Prose

Write the way the existing skills read: direct, specific, active voice, no
filler. Run a slop check before you open a pull request.

## Phases

The repo reserves `mcp-servers/`, `commands/`, `agents/`, and `hooks/` for the
runtime capabilities and enforcement layers the skills describe. A skill that
needs a tool to exist (rather than knowledge the model applies) belongs in one
of those, not in `skills/`.
