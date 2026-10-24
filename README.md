# AI Skill Bundle

A reusable, tool-neutral catalog of AI coding-assistant **skills**, **agents**, and
**rules**. Any repository can select from it, keep it up to date, and render it into
Claude Code, Codex, Cursor, and Gemini CLI. Python standard library only.

```text
catalog/                 canonical, portable entities (no project facts)
  skills/<name>/         Agent Skills directories: SKILL.md + references/ + scripts/
  agents/<name>.md       delegate/reviewer definitions with an access level
  rules/<name>.md        rules with description / always-apply / paths
  lint.json              portability lint (host paths, project names, model IDs)
packs/<name>.json        composable selections with `requires`
routing/tiers.json       cost tiers -> per-tool model and effort defaults
scripts/aibundle.py      catalog side: list, validate, init, install, status
scripts/render.py        repo side: vendored as .ai/render.py, replaces sync.sh
examples/<repo>/.ai/     migration kit for a pilot repository (bundle.json + overlays)
docs/                    review log, model-routing design, research
imports/                 local only (gitignored): snapshot of the platform repos' .ai folders
tests/                   behavioural tests for install and render
```

## How a repository uses it

```text
catalog ──install──▶ repo/.ai/  (canonical, committed) ──render──▶ .claude/ .agents/ .codex/ .cursor/ .gemini/ AGENTS.md
           │          bundle.json   you edit: packs, targets, routing, invocation
           │          bundle-lock.json  written by install: digests of managed files
           │          overlays/<skill>.md   you write: repository paths, commands, decisions
           │          project-guidance.md   you write: always-on repository context
           └──────── skills/ agents/ rules/ render.py routing.json   managed by install
```

```sh
# 1. Choose packs (see `aibundle.py list`)
python3 scripts/aibundle.py init --repo ../my-service --pack core --pack review --pack fastapi

# 2. Install or upgrade the canonical files under .ai/ (all-or-nothing, never clobbers local edits)
python3 scripts/aibundle.py install --repo ../my-service --dry-run
python3 scripts/aibundle.py install --repo ../my-service

# 3. Render assistant folders from .ai/ (inside the repository, no catalog needed)
python3 .ai/render.py            # write
python3 .ai/render.py --check    # CI gate: fails when generated outputs are stale
```

Commit `.ai/`, `AGENTS.md`, and `GEMINI.md`. Keep the tool folders gitignored as
with the previous `sync.sh` flow, and **add `.agents/`** to `.gitignore`: it is
new, and holds the shared skill copies for Codex, Cursor, and Gemini CLI. `aibundle.py status --repo R` shows pending
upgrades and local drift.

### Ownership rules

- **Managed** entities (listed in `bundle-lock.json`) belong to the catalog. If
  they are unmodified, `install` updates them in place. If they were edited locally,
  `install` stops and changes nothing. Upstream the edit to the catalog, or add
  the slot (for example `"skills/nestjs"`) to `"local"` in `bundle.json` to keep a fork.
- **Local** entities are yours. A skill directory under `.ai/skills/` that the
  catalog does not provide is rendered like any other.
- **Overlays** (`.ai/overlays/<skill>.md`) carry repository facts for a catalog
  skill: paths, commands, naming, and decisions. The rendered skill tells the agent
  to read the overlay first. This is how one generic `nestjs` skill serves many repos.
- `render.py` only writes inside allowlisted tool namespaces, removes only paths
  recorded in its previous manifest (`.ai/generated-outputs.txt`), and refuses to
  overwrite files it did not generate.

### What gets rendered

| Canonical | Claude Code | Codex | Cursor | Gemini CLI |
|---|---|---|---|---|
| index (guidance, rules, skills, agents, tiers) | `.claude/CLAUDE.md` | `AGENTS.md` | `AGENTS.md` | `GEMINI.md` → `@./AGENTS.md` |
| skills | `.claude/skills/` | `.agents/skills/` + `agents/openai.yaml` | `.agents/skills/` | `.agents/skills/` |
| agents | `.claude/agents/*.md` (tools, model, effort) | `.codex/agents/*.toml` (model, effort) | `.cursor/agents/*.md` (readonly, model) | `.gemini/agents/*.md` (tools, model) |
| rules | `.claude/rules/*.md` (`paths`) | via `AGENTS.md` | `.cursor/rules/*.mdc` | via `AGENTS.md` |
| explicit-only skills | `disable-model-invocation` | `allow_implicit_invocation: false` | `disable-model-invocation` | note in skill body |
| skills an agent uses (`metadata.skills`) | `skills:` preload (a read-first note for explicit-only skills) | read-first note in instructions | read-first note | read-first note |

Field names were checked against vendor documentation on 2026-10-23. See
[`catalog/skills/model-routing/references/tool-mechanics.md`](catalog/skills/model-routing/references/tool-mechanics.md)
for the sources and the caveats (for example, Codex agent files cannot make
a subagent read-only).

## Cost-aware model routing

Every skill and agent declares a tool-neutral **tier** and **effort**:

| Tier | For | Claude default |
|---|---|---|
| `fast` | mechanical, cheaply verifiable work: search, summaries, running checks | `haiku` |
| `balanced` | routine implementation and review with clear acceptance criteria | `sonnet` |
| `deep` | design, security, data, concurrency, contracts, root-causing | `opus` |

Routing works at three levels. The first two are configuration; the third is
orchestration behaviour, because a static label cannot know that an attempt just failed.

1. **Static defaults.** `render.py` maps an agent's tier to each tool's model and
   effort fields (`routing/tiers.json`, overridden per repository in
   `bundle.json` `routing.models`/`routing.overrides`). Unmapped tiers inherit the
   session model. Inline skills stay *advisory* by default, so a skill never silently
   downgrades your main session. Set `routing.apply.skills: "enforce"` to emit
   effort for skills too. A skill with `metadata.context: fork` runs in its own
   subagent and gets its tier's model.
2. **Plan-time assignment.** `principal-engineer-planner` suggests a tier per
   implementation step, from that step's hardest decision.
3. **Run-time adjustment.** `model-routing` defines when to escalate (repeated
   failure without new evidence, a newly found security/data/contract concern, a
   failed review) or de-escalate (mechanical follow-ups, noisy check runs). It
   caps escalation at once per unit, keeps validation independent, and has
   `plan-execution` record tier, escalation, and outcome. The lead agent applies
   it by passing a per-spawn model/effort override. The `scout` and `check-runner`
   agents are ready-made `fast` delegates that keep noisy output out of an
   expensive context.

For the main session itself, pick the model yourself or use Claude Code's
`opusplan` alias (Opus while planning, Sonnet while executing). `routing.apply.skills:
"enforce"` is experimental: a `fast`/`low` skill activated during hard work also
lowers effort for that work while the skill is active.

Design rationale and limits: [docs/model-routing.md](docs/model-routing.md).

## Maintaining the catalog

```sh
python3 scripts/aibundle.py validate          # structure, packs, links, portability lint
python3 -m unittest discover -s tests -v      # installer and renderer behaviour
```

- Keep catalog content generic. Repository facts go in that repository's
  overlays or project guidance. The lint enforces the obvious cases.
- Canonical frontmatter allows only portable fields (`name`, `description`,
  `metadata`, …). Tool-specific fields are generated. Allowed `metadata` keys:
  `routing-tier` (required), `routing-effort`, `invocation`, `context`, `agent`,
  `tags`, `max-turns`, and `skills` (agents only: skills the agent applies, such as
  `security-practices` → `appsec-review`). Every pack that selects such an agent,
  including its `requires`, must select those skills, and `install` refuses a
  manifest that drops one.
- Add a new entity to at least one pack. Keep `SKILL.md` under 500 lines and move
  detail into `references/` (progressive disclosure).
- Changing an entity changes its digest. Repositories pick it up on their next
  `install`. Review a change against the packs that select it.
- Treat third-party skills as dependencies: review provenance, scripts, and
  permissions before adding them.

## Migrating a repository from sync.sh

1. Move repository-specific content out of the old `.ai/skills/*` files into
   `.ai/overlays/<skill>.md` (see `examples/movie-reservation-service/`).
   Anything you want to keep verbatim stays a local entity.
2. Delete the old `.ai/skills`, `.ai/agents`, `.ai/rules`, and `.ai/meta` copies
   that the catalog now provides, or list them in `"local"`.
3. Write `.ai/bundle.json` (`aibundle.py init`), then `install` and `render`.
   The old `generated-outputs.txt` lets the renderer remove the previous outputs,
   including the misplaced `.codex/skills/` and `.gemini/GEMINI.md`.
4. Add `.agents/` to `.gitignore`, review the generated diff, delete `.ai/sync.sh`,
   and add `python3 .ai/render.py --check` to CI.

`render.py` refuses to write through a symlinked tool directory (for example a
`.claude/` linked to `~/.claude`), so it never touches user-level configuration.

Do this one repository at a time, in its own issue, branch, and pull request.

## Status

- The catalog and tooling are validated by `aibundle.py validate` and the test
  suite. A pilot migration ran against a scratch copy of `movie-reservation-service`.
  No real repository has been changed.
- The skill content is curated from the imported snapshot. Behaviour in real
  agent sessions has not been evaluated per skill.
- `imports/` is a local, unversioned snapshot of the platform repositories' `.ai`
  folders and the previous composer, kept for writing overlays. The source of
  truth for that content is the platform repositories themselves.

## Alternatives to evaluate

The catalog uses the standard `SKILL.md` layout, so it stays portable. The
installer and renderer (`aibundle.py`, `render.py`) could be replaced by an
existing tool. Each one below was surveyed from its documentation on 2026-10-24
and has not been tried here yet:

| Option | What it covers | Gap to check |
|---|---|---|
| [Microsoft APM](https://github.com/microsoft/apm) | `apm.yml` manifest, `apm.lock.yaml` with content hashes, installs skills, instructions, plugins, and MCP servers into Claude, Codex, Cursor, Gemini, Copilot, and others | Tier/effort routing, agents with skill links, overlays |
| [Vercel `skills` CLI](https://vercel.com/docs/agent-resources/skills) ([skills.sh](https://skills.sh)) | `npx skills add owner/repo --skill <name>` installs single skills into many agents' skill folders | Skills only: no agents, routing, or overlays |
| [Claude Code plugins and marketplaces](https://code.claude.com/docs/en/discover-plugins) | Plugins bundle skills, agents, hooks, and MCP servers; a marketplace is a JSON catalog in a git repo | Mainly Claude Code; other tools still need rendering |
| [rulesync](https://github.com/dyoshikawa/rulesync) | Generates rules, commands, subagents, skills, and MCP config for many tools from one source | Model routing, overlays, ownership rules |
| [ai-rules-sync](https://github.com/lbb00/ai-rules-sync) | Syncs rules, skills, commands, and subagents across tools | Same as rulesync |

Suggested first trial: point APM at this catalog from a scratch repository and
compare its output with `render.py`. Before writing more renderer code for a
vendor change, check whether one of these tools already handles it.

## License

[MIT No Attribution (MIT-0)](LICENSE). Copy, adapt, and redistribute any skill,
agent, or rule, alone or together, with or without credit.
