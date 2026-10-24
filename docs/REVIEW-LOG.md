# Review Log

Five review → fix cycles on the reusable AI bundle, 2026-10-23. Each cycle reviews
the state left by the previous one. Severity: **H** blocks reuse across repos,
**M** causes wrong or degraded behaviour, **L** is friction or polish.

The pre-review state is archived unchanged in [`imports/`](../imports/README.md).

## Cycle 1: baseline (the imported snapshot)

The question was whether the bundle works as a reusable catalog for many repositories.
It does not yet. It is a lossless **archive** of 12 repositories' `.ai` folders,
not a generic catalog.

| # | Sev | Finding | Evidence |
|---|---|---|---|
| 1.1 | H | The catalog is keyed by *origin repository*, not by capability. Flavors such as `python/fastapi-agent`, `python/environment-automation` and `python/recommendation-mcp` are repo nicknames. A new repo cannot pick a flavor without knowing this platform's history. | `imports/catalog/skills/*/*` |
| 1.2 | H | Many variants exist only because of drift. There are 7 `clean-architecture`, 7 of each review agent, 5 `typescript`, 4 `testing` and 3 `programming-kb`. Two `programming-kb` variants differ by one trailing newline. `frontend-clean-architecture` and `hybrid-teaching-mode` each appear twice, byte-for-byte identical in content. | similarity scan: `local-vault` ≡ `local-vault-original` minus `\n` |
| 1.3 | H | "Shared" assets still contain project facts: `/home/patex1987/...` vault paths, `movie-reservation-service/` paths, reservation/booking examples, and service routes (`/movies`, `/recommendations`). | `skills/knowledge/local-vault/programming-kb`, `nestjs`, `vitest-testing`, `rust/axum/*` |
| 1.4 | H | There is no install, upgrade or drift story. `compose` only writes a *new* staging directory, so adopting a catalog update in a repo means a manual diff and copy. Nothing detects local edits to managed files. | `scripts/bundle.py compose` refuses existing targets |
| 1.5 | H | Rendering into tool folders is owned by four diverging copies of `sync.sh`. Default Codex models differ (`gpt-5.4` vs `gpt-6-astra`). One copy lacks stale-output cleanup. | `sha256(sync.sh)`: 4 distinct digests across 11 repos |
| 1.6 | H | Codex skills are projected to `.codex/skills/`, but Codex discovers repo skills only in `.agents/skills/`. The skills are invisible to Codex. | [Codex skills docs](https://learn.chatgpt.com/docs/build-skills) |
| 1.7 | M | Codex agent TOML gets `sandbox_mode = "read-only"`. Codex ignores it, because subagents inherit the parent sandbox, so the reviewers are **not** read-only in Codex. `.codex/rules/*.md` is also not a Codex instruction surface: Codex `rules` are command exec-policy files. | [Codex subagents docs](https://learn.chatgpt.com/docs/agent-configuration/subagents) |
| 1.8 | M | Model choice is hard-coded per tool (`codexModel: gpt-5.4`, Claude `model: inherit`). There is no tool-neutral notion of "this task needs a cheap/strong model", and no way to adjust it per repo or as models change. | agent frontmatter |
| 1.9 | M | Metadata is duplicated: skill frontmatter plus `meta/*.yaml` plus `agents/openai.yaml` must stay aligned by hand. Invocation policy (explicit-only KB) is encoded by forking the skill text rather than as configuration. | `meta/*`, 3 KB variants |
| 1.10 | M | Profiles are repo-named, with collision/override machinery. That complexity exists only because names are not unique by capability. | `profiles/*.json`, `resolve()` |
| 1.11 | L | Content digests are hand-maintained in `catalog.json`, so every legitimate edit needs a manual hash refresh. | README "Maintenance" |
| 1.12 | L | The bundle is not under version control, so there is no history for reviewing catalog changes. | `git rev-parse` fails |

**Fix direction for cycle 1:** archive the snapshot, introduce a capability-keyed
catalog with unique names, composable packs, a per-repo manifest, and repo-local
overlays for project facts. Replace the hand-maintained digests with a generated lock.

### Cycle 1 fixes

| Finding | Fix |
|---|---|
| 1.1, 1.2, 1.10 | New capability-keyed catalog: 24 skills, 6 agents, 1 rule, each name unique. 14 composable **packs** (`core`, `review`, `typescript`, `nestjs`, `python`, `fastapi`, …) with `requires`. Collisions are impossible by construction, so the override machinery is gone. Duplicate variants were merged. Stack-specific detail moved into `references/` (for example `clean-architecture/references/*.md`). |
| 1.3 | Project facts were removed from catalog content. A portability lint (`catalog/lint.json`) rejects host paths, personal identifiers, project names and pinned model IDs. It caught one more leak (`/golden-path/` in a CDK example). Repository facts move to **overlays** (`.ai/overlays/<skill>.md`), which the renderer links from the skill. |
| 1.4, 1.11 | `aibundle.py install` syncs a repo's `.ai/` from its `.ai/bundle.json` and writes `.ai/bundle-lock.json` with digests. It updates unmodified entities in place, refuses to touch locally modified or unmanaged ones (all-or-nothing), and supports `"local"` to release ownership. Digests are computed, never hand-edited. |
| 1.9 | One source of metadata: canonical frontmatter plus spec-compliant `metadata` keys. `meta/*.yaml` and hand-written `agents/openai.yaml` are gone. The explicit-only KB is now a configuration value (`invocation`), not a forked copy. |
| 1.5 | One stdlib renderer, `render.py`, is vendored into each repo as `.ai/render.py` by `install` and upgraded with the catalog. It replaces all `sync.sh` copies. It reuses their manifest-based stale-output cleanup, deletes only allowlisted namespaces, and refuses to overwrite hand-written files. `--check` gives CI a drift gate. |
| 1.6 | Shared skills render to `.agents/skills/`, which Codex, Cursor and Gemini CLI all read. Legacy `.codex/skills/` entries in an old manifest are removed. |
| 1.7 | Codex agents no longer emit `sandbox_mode`. Read-only agents get an explicit instruction that the parent sandbox is the only enforcement. `.codex/rules/*.md` is no longer produced. |
| 1.8 | Tool-neutral **routing tiers** (`fast`/`balanced`/`deep` plus effort) on every skill and agent, mapped per tool by `routing/tiers.json` and overridable per repo in `bundle.json`. A new `model-routing` skill covers dynamic escalation during execution. The planner suggests a tier per step, and execution and validation record escalations (see cycle 3 for the review of that design). |
| 1.12 | Not fixed. Needs a decision from the user (see cycle 2). |

Files were written test-after for the new tooling. A mutation check (4 seeded
defects in `render.py`) was killed by the 28-test suite.

## Cycle 2: tooling after the redesign

Method: read both scripts end to end, and run a pilot migration on a scratch copy of
`movie-reservation-service` (install, render, `--check`, inspect every tool's output).

| # | Sev | Finding | Evidence |
|---|---|---|---|
| 2.1 | M | The generated index repeated every full description: about 24 long lines in always-loaded context, duplicating what all four tools already load from native skill discovery. This works against the KB's context-budgeting guidance. | pilot `AGENTS.md` |
| 2.2 | M | `.gemini/GEMINI.md` (inherited from `sync.sh`) is not a documented Gemini CLI load location. Gemini looks for `GEMINI.md` in workspace directories and their parents, so the index was probably never loaded. | geminicli.com `gemini-md` docs |
| 2.3 | M | `bundle.json` had no type checks. `"packs": "core"` iterated characters. | code reading |
| 2.4 | L | The lock was written non-atomically. An interrupted write could leave invalid JSON that blocks the next install. Entity copies are self-healing on re-run, because an unlocked file that matches the catalog is adopted. | code reading |
| 2.5 | L | Empty legacy directories (`.codex/skills/`, `.gemini/rules/`, …) remained after cleanup. | pilot tree |
| 2.6 | L | The refusal message for a hand-written `AGENTS.md` or `CLAUDE.md` did not say where that content should go. | code reading |
| 2.7 | L | The Codex display name "Programming Kb". Unused import. | pilot output |
| 2.8 | M | No README existed for the new layout, and there was no written design rationale for routing. | tree |
| 2.9 | L | `tool-mechanics.md` did not mention the per-spawn override, which is the actual lever for run-time escalation. | Claude docs precedence item 1 |

### Cycle 2 fixes

- 2.1: The index shows the first sentence (≤160 chars) per entity and says skills load natively.
- 2.2: A root `GEMINI.md` containing `@./AGENTS.md` (documented import syntax). `.gemini/GEMINI.md` is treated as a legacy output and removed.
- 2.3: Schema and type validation of `bundle.json` before any write.
- 2.4: The lock is written via a temporary file and `replace()`.
- 2.5: Empty parent directories of removed outputs are pruned, never the repository root.
- 2.6–2.7: Actionable refusal message, acronym-aware display names, and the unused import removed.
- 2.8: New `README.md` and `docs/model-routing.md`.
- 2.9: Per-spawn override documented as the dynamic lever.

Tests: 32 pass, with new cases for the Gemini import, index size, manifest
validation, legacy-directory pruning, and display names.

## Cycle 3: routing design and catalog content

Method: re-check the routing claims against vendor docs (effort support, model
precedence per tool), sweep catalog content for stale cross-references, and
compare the tier assignments with the `model-routing` rules.

| # | Sev | Finding | Evidence |
|---|---|---|---|
| 3.1 | M | In Codex, a model pinned in an agent file **wins over** spawn-time settings, so a repository that maps Codex tiers loses run-time escalation for that agent. The docs presented the per-spawn override as universal. | Codex subagents docs |
| 3.2 | M | `bundle.json` typos (`routing.overrides.scoutt`, `invocation.programming-kbb`, an effort of `extreme`) were silently ignored, so the configuration looked applied but was not. | code reading |
| 3.3 | M | Catalog `routing-effort` values were not validated. | code reading |
| 3.4 | L | The index tier table listed tools whose targets were disabled. | render with `targets: ["claude"]` |
| 3.5 | L | `frontend-clean-architecture` was tagged `deep`, but it is used during routine UI implementation. The planner and `model-routing` already escalate the genuinely architectural work. | tier review |
| 3.6 | L | Main-session routing was undocumented. Claude Code's `opusplan` alias already does "deep for planning, balanced for execution". Effort clamping on unsupported levels was also unstated. | Claude model-config docs |
| 3.7 | — | No stale cross-references to renamed skills (`testing`, `infra-testing`, `python-automation`) remain. The tier assignments agree with the `model-routing` table. Haiku accepts `effort`. | grep sweep, docs |

### Cycle 3 fixes

- 3.1: Documented in `tool-mechanics.md`: to keep escalation in Codex, leave a tier unmapped or delegate to a different agent.
- 3.2–3.3: The renderer rejects unknown override and invocation names and invalid efforts. The validator rejects unknown catalog efforts.
- 3.4: The tier table shows enabled tools only.
- 3.5: `frontend-clean-architecture` changed to `balanced`.
- 3.6: `opusplan`, effort clamping, and the experimental status of `routing.apply.skills: "enforce"` are documented in the README and `tool-mechanics.md`.

Tests: 35 pass.

## Cycle 4: genericity across stacks

Method: for each platform repository type, plus an unrelated Go service,
install the matching packs into an empty scratch repo, render, scan **all
rendered output** with the portability lint, compare the always-loaded index
size with the repository's current `AGENTS.md`, and diff old skill names against
the new catalog.

Result before fixes: 0 leaks in 8 repositories. Index 3.9–6.4 KB **before**
project guidance, against 5.7–10.7 KB for today's files *with* guidance, so a
migrated repo would have carried more always-on text than before.

| # | Sev | Finding | Evidence |
|---|---|---|---|
| 4.1 | M | The index was still too large: full first sentences, per-line source paths, and repeated tier prose. | matrix sizes |
| 4.2 | L | Truncated summaries produced `requirements….`. | go-service index |
| 4.3 | M | Three descriptions (`hybrid-teaching-mode`, `learn-by-doing`, planner) opened with "Use when…", so their summary said nothing about what the skill does. That weakens both the index and model-side skill selection, which keys on the description. | index |
| 4.4 | M | Old names with no same-name entity: `testing` (4 repos), `infra-testing`, `python-automation`, `agent-inspiration`. Without a map, migrating repos would silently lose or misname guidance. | matrix diff |
| 4.5 | — | The catalog covered all 7 active stacks plus an unrelated one with no project-specific text in output. `agent-inspiration` correctly stays out of the catalog: it indexes a host-local corpus. | matrix |

### Cycle 4 fixes

- 4.1–4.2: Index lines are now `` `name` [tier/effort] summary `` (≤110 chars, clean ellipsis), with source paths stated once per section. Measured after re-installing (which also exercised the upgrade path: edited catalog entities arrived as clean `update`s): 2.9–4.4 KB, down 27–33% (Go service 3955 → 2868 B, infra 6390 → 4354 B).
- 4.3: Descriptions rewritten to lead with what the skill does, then when to use it.
- 4.4: `examples/MIGRATION-MAP.md` gives per-repo packs, the overlays to write, and the rename map.

## Cycle 5: safety and consistency (final pass)

Method: threat-model the two scripts as code that writes into many repositories,
re-read every document against the current behaviour, and re-run the pilot from
a fresh copy.

| # | Sev | Finding | Evidence |
|---|---|---|---|
| 5.1 | H | Neither script checked for symlinked path components. If `.claude/` is symlinked to `~/.claude` (a common setup), `render.py` would write into, and delete stale outputs from, user-level configuration. `install` would follow a symlinked `.ai/agents`. | code reading; reproduced in a test |
| 5.2 | M | The new `.agents/` output folder was not in any repository's `.gitignore`, so the first render would show dozens of untracked files. | pilot `git status` reasoning; repo `.gitignore` lists only `.claude/` … `.roo/` |
| 5.3 | M | The archived `imports/README.md` still described its commands relative to the bundle root, which is now wrong. | moved files |
| 5.4 | L | The bundle had no `AGENTS.md`, although the workspace rules require reading one before implementation. | root `AGENTS.md` coordination rules |

### Cycle 5 fixes

- 5.1: `render.contained()` rejects any symlinked component, and every target is validated before the first write or delete. `install` uses the same guard. Two new tests prove nothing outside the repository is touched and nothing is half-written.
- 5.2: README and migration steps say to add `.agents/` to `.gitignore`.
- 5.3: Archive banner with corrected commands. The archive's own 9 tests still pass.
- 5.4: `AGENTS.md` for catalog maintainers.

### Final state

- `aibundle.py validate`: 31 entities, 14 packs, routing tiers, and portability lint clean.
- `tests/`: 37 pass. `imports/tests`: 9 pass.
- Fresh pilot on a scratch copy of `movie-reservation-service`: install 21 managed
  files, render 66 outputs, remove 25 legacy `sync.sh` outputs (including
  `.codex/skills/*`, `.codex/AGENTS.md`, `.gemini/GEMINI.md`) and their empty folders.
  `--check` reports current and `status` reports up to date. The real repository's
  `git status` is unchanged.
- The pilot's `AGENTS.md` is 8.9 KB against 7.8 KB today. The difference is the tier
  table and two new agent entries, and the rules and skills summaries are shorter
  than before.

### Not done / open

- The catalog is still not under version control (1.12), so `bundle-lock.json` records
  `catalog.revision: "unversioned"`. Recommended: `git init` it as its own
  repository and tag releases that consumers install from.
- Overlays exist only for the pilot repository. The other repos need theirs
  written from `imports/` (see `examples/MIGRATION-MAP.md`).
- Skill behaviour in real agent sessions has not been evaluated. Routing tiers are
  reasoned defaults, not measured. `docs/model-routing.md` describes the evidence loop.
- Gemini CLI subagent field names come from secondary sources.

## Follow-up: Roo removed (renderer 2.1.0)

The user decided to drop Roo. `roo` is no longer a target. A `bundle.json` that
still lists it fails with an explicit message rather than being silently ignored.
`.roo/rules/*` and `.roo/skills/*` are legacy outputs: the first render after
upgrading removes any listed in the previous manifest. Cline was not added, and its
instruction and skill locations have not been verified.

## Follow-up: `appsec-review` skill and agent skill links (renderer 2.2.0)

The user asked for one security skill covering three requests:

- guidance on a security topic
- a review of the current PR or branch that reports only newly added risk
- a full audit

It also needed to complement scanners such as Trivy, Semgrep, Snyk, and Checkov.

- **New skill `catalog/skills/appsec-review`** (`deep/high`, in the `review` pack):
  - It has three modes and one shared evidence gate (`confirmed`, `likely`,
    `needs-validation` without severity, `rejected`).
  - It has an explicit do-not-flag list, change-review triage by risk, and a
    full-audit workflow with a coverage ledger, coverage critic, and
    independent verifiers.
  - It has scanner guidance with execution states and data-egress cautions.
- **Sources:** the text is original. It adapts ideas from:
  - Cloudflare's `security-audit-skill` and its AI code review post
  - Trail of Bits (ideas only, because the CC-BY-SA licence is incompatible
    with MIT-0)
  - Sentry, Anthropic's `claude-code-security-review`, and OpenAI's security
    skills
  - the user's knowledge base notes

  Pinned revisions are listed in `references/sources.md`.
- **Name:** `appsec-review`, not `security-review`, because Claude Code ships a
  built-in `/security-review` command.
- **`security-practices` agent:**
  - Access changed from `read-only` to `execute`. Change review needs `git
    diff` and `log`, and Claude read-only agents get only Read, Grep, and Glob.
  - The body allows read-only git and preinstalled scanners only.
  - The agent now has reviewer, unit-reviewer, and verifier roles.
- **New `metadata.skills` for agents:**
  - Claude renders it as the subagent `skills` preload. Explicit-only skills
    fall back to a read-first note, because Claude cannot preload them.
  - Codex, Cursor, and Gemini get a read-first note pointing at
    `.agents/skills/<name>/SKILL.md`.
  - `validate` checks that packs carry the skills their agents use, and
    `install` refuses a manifest that removes one.
- Tests: 42 pass (5 new or changed). Pilot render on a scratch repository with
  `core` and `review`: `--check` reports current.
- **Not done:** the skill has not been evaluated on seeded vulnerable and
  protected samples. Scanner flag forms were checked against current
  documentation from memory and secondary sources, so confirm them with
  `--help` on the installed versions.

## Follow-up: interactive plan review in `principal-engineer-planner`

The user asked for a guided, question-by-question plan review inside the existing
planner skill rather than a new skill.

- **Modes section in `SKILL.md`:** plan authoring (default) and interactive plan
  review. Annotation requests stay in authoring mode. The description now names
  the review trigger.
- **`references/plan-review.md`:**
  - a question queue, built after reading the plan and research, grouped by topic,
    ordered by dependency, and skipping questions the repository already answers
  - one question at a time as `Question M/N — <topic>` with context, tradeoffs, and
    a recommendation; stable `Q-NN` IDs; four statuses (`pending`, `discussing`,
    `decided`, `deferred`)
  - only an explicit user decision settles a question; deferred questions stay
    counted and unresolved
  - plan updates after each decision, with labels separating user decisions,
    recommendations, assumptions, and evidence
  - test agreement and implementation authorization tracked separately
  - a resumable review record at `docs/plans/<plan>-review.md`, linked from the plan
- **Plan template:** a `Review record:` line and a `### Decisions` list.
- **Validation examples:** `evals/evals.json` (skill-creator format) with nine
  cases and fixtures under `evals/files/`. They cover:
  - starting a review
  - clarifications that do not advance `M`
  - adding a question
  - deferring a question
  - ambiguous replies
  - resuming a review
  - completion
  - authorization during a review
  - the boundary with annotation requests
- **`validate`:** checks `evals/evals.json` when present (skill name, unique ids,
  prompts, expectations, files inside the skill). Tests: 43 pass (1 new).
- **Tradeoff:** evals ship with the skill into consuming repositories' skill
  folders. Agents do not load them unless asked.
- **Not done:** the eval cases have not been run against a model yet.

## Follow-up: `pr-walkthrough` skill and reviewer agent rewrite

The user wanted a review that does not overwhelm the reader:

- big picture first
- topics in the order they build on each other
- a `M/N` counter
- a plain-language explanation per topic
- concrete files, lines, and snippets

No published skill did all of this (surveyed 2026-10-24). The closest was
xpepper's `guided-flow-review`.

- **New skill `catalog/skills/pr-walkthrough`** (`deep/medium`, `review` pack):
  - an overview with a map and a topic list
  - topics grouped by idea and ordered building blocks → core behavior →
    integration → supporting → mechanical
  - `Topic M/N — <name>` with "In plain terms", `path:line` bullets, and at most
    two short snippets
  - length budgets, one topic per message, and a gate after each topic
  - review and explain modes
  - findings tagged `blocking`, `should`, `nit`, or `question` and routed by the
    user, with evidence checks and a do-not-flag list
  - a resumable record
  - posting only after the user approves the exact text
- **Sources:** the text is original. Ideas came from `guided-flow-review` (MIT)
  and others, listed in `references/sources.md`.
- **Validation examples:** `evals/evals.json` has nine cases, with a base and
  head fixture of a coupon change. The change has two planted defects: a
  negative total, and a test whose expected value comes from the production
  constant it checks.
- **Reviewer agents rewritten** (`performance-scalability`,
  `readability-maintainability`, `system-design-scalability`, and the voice and
  report of `security-practices`):
  - Before, each agent was a list of keywords plus "findings first". Each now has:
    - a point of view
    - a domain-specific method
    - a bar for what is worth flagging (adapted from OpenAI Codex's review
      rubric: introduced by the change, concrete trigger, the author would fix it)
    - a do-not-flag list (from Anthropic's code-review command:
      linter-catchable, pre-existing, taste)
    - a short report: verdict line, tagged findings with one-paragraph
      scenarios, confidence, code excerpts of at most three lines, and what was
      checked
  - The tags match `pr-walkthrough`, so agent results drop into a walkthrough
    topic.
  - Inspiration surveyed: Anthropic `claude-plugins-official` (code-review,
    pr-review-toolkit) at `5826794`, OpenAI `codex` review rubric at `970111f`,
    VoltAgent `awesome-claude-code-subagents` at `408d3c9`, and wshobson
    `agents` at `0874a27`. The last two are mostly keyword lists, so they served
    as a counterexample.
- **Access:** the three non-security reviewers changed from `read-only` to
  `execute`, so that they can run `git diff` and `log` for a change range, as
  `security-practices` already does. Their bodies allow read-only git and cheap
  existing checks only. One test now uses `scout` as its read-only example.
- Tests: 43 pass. Pilot render with `core` and `review`: `--check` reports current.
- **Not done:** neither the eval cases nor the rewritten agents have been run
  against a model yet.

## Follow-up: `typescript-style` skill

- **Problem:** in a consuming repository, an agent wrote TypeScript with no
  blank lines, deeply nested calls, and no doc comments. That code passed both
  Prettier and ESLint. Prettier keeps blank lines but never adds them, and the
  repository's padding rules did not cover imports or top-level declarations.
  No catalog skill said anything about layout or doc comments.
- **Survey (2026-10-24):** six published TypeScript style and doc skills were
  read in full: pproenca `ts-google` and `typescript`, thenordicone
  `typescript`, perdolique `typescript-conventions`, claude-dev-suite
  `jsdoc-tsdoc`, and kentoshimizu `typescript-style-guide`. None covered layout.
  One covered doc comments, but it required `@example` and `@throws`
  everywhere. Ideas were adapted with provenance in `references/sources.md`; no
  text was copied.
- **New skill `catalog/skills/typescript-style`** (`balanced/medium`,
  `typescript` pack, so `aws-cdk`, `nestjs`, `react`, and `github-actions`
  pull it in):
  - The order of authority is: repository config, then surrounding code, then
    the skill. Formatter and linter fixers and checks run before handing back.
    Untouched files are not reformatted.
  - Explicit blank-line rules, named intermediates, data-flow ordering, guard
    clauses, named constants with units, and a short list of idioms.
  - TSDoc on exports, describing what types cannot (units, side effects, errors,
    invariants), with no types in tags.
  - `references/lint-recipe.md`: `@stylistic` padding and class-member rules,
    `curly`, `one-var`, `jsdoc/require-jsdoc` (with `publicOnly` and
    `enableFixer: false`, so `--fix` does not insert empty stubs), `no-types`,
    `check-param-names`, and `tsdoc/syntax`. The recipe was tested as written
    with ESLint 9.39, `@stylistic` 5.10, `eslint-plugin-jsdoc` 63.3, and
    `eslint-plugin-tsdoc` 0.5 against a dense sample. `--fix` cleared every
    layout error.
  - 5 eval cases with fixtures.
- `typescript` now points to `typescript-style` for layout and comments.
- **Not done:**
  - The evals have not been run against a model.
  - The skill is not installed in any consuming repository; that is a separate
    task there.
