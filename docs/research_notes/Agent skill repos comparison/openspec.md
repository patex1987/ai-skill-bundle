# OpenSpec (Fission-AI/OpenSpec): model, artifact formats, CLI, and fit with a plan/research skill catalog

> Version read: `@fission-ai/openspec` **1.16.1** (published 2026-11-07), repo `main` at commit `0fa4a97` (2026-11-07), shallow-cloned and read locally. Repo metadata via `gh api`: about 74k stars, MIT, Node >=22.12.0 for the npm install. File links below point to `main` on GitHub; paths are repo-relative. Not verified empirically: I tried to install the CLI in a scratch dir to test the "specs-only retrospective change" idea, but the install command was denied by the permission classifier, so every claim about CLI behaviour comes from docs, schema files and source code, not from a run.

## 1. Directory model and exact artifact formats (specs/, changes/, archive/)

### Takeaway
OpenSpec keeps two trees under `openspec/`: `specs/<capability>/spec.md` (the current agreed behaviour, one file per capability, requirements plus scenarios) and `changes/<change>/` (one folder per in-flight change holding `proposal.md`, `design.md`, `tasks.md`, `specs/<capability>/spec.md` deltas and a `.openspec.yaml`). Finished changes move to `changes/archive/YYYY-MM-DD-<change>/`. Specs are deliberately behaviour contracts (what), not implementation plans (how).

### Cited Findings
- Layout: `openspec/specs/` is "source of truth" for current behaviour; `openspec/changes/` holds proposed modifications; each change is a folder with `proposal.md`, `design.md`, `tasks.md`, optional `.openspec.yaml` (schema, created, `skip_specs`, `retire_capabilities`, user `x-*` keys) and `specs/<domain>/spec.md` delta files — [docs/concepts.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)
- `openspec init` creates `openspec/specs/`, `openspec/changes/`, `openspec/config.yaml` plus per-tool skill/command directories — [docs/cli.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md)
- Specs may be nested (`identity/user-auth`) as well as flat; the capability path in a change's `specs/` must mirror the path under `openspec/specs/`; new path segments must be kebab-case — [schemas/spec-driven/schema.yaml](https://github.com/Fission-AI/OpenSpec/blob/main/schemas/spec-driven/schema.yaml), `findSpecUpdates` in [src/core/specs-apply.ts](https://github.com/Fission-AI/OpenSpec/blob/main/src/core/specs-apply.ts)
- Main spec format (title, `## Purpose`, `## Requirements`, `### Requirement:` with SHALL/MUST, `#### Scenario:` with Given/When/Then bullets):
  ```markdown
  # Auth Specification

  ## Purpose
  Authentication and session management for the application.

  ## Requirements

  ### Requirement: User Authentication
  The system SHALL issue a JWT token upon successful login.

  #### Scenario: Valid credentials
  - GIVEN a user with valid credentials
  - WHEN the user submits login form
  - THEN a JWT token is returned
  - AND the user is redirected to dashboard
  ```
  — [docs/concepts.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)
- Scenario syntax rules from the shipped schema instruction: `#### Scenario: <name>` must be exactly four hashtags ("3 hashtags or bullets will fail silently"); every requirement needs at least one scenario; each scenario needs a WHEN/GIVEN and a THEN step (otherwise a warning that fails `validate --strict`); requirement description text (before first scenario) should be <=500 chars (warning); use SHALL/MUST for normative statements — [schemas/spec-driven/schema.yaml](https://github.com/Fission-AI/OpenSpec/blob/main/schemas/spec-driven/schema.yaml), constants in [src/core/validation/constants.ts](https://github.com/Fission-AI/OpenSpec/blob/main/src/core/validation/constants.ts) (`MIN_PURPOSE_LENGTH=50`, `MAX_REQUIREMENT_TEXT_LENGTH=500`, `MAX_DELTAS_PER_CHANGE=10`, `REQUIREMENT_NO_SHALL` message)
- Scenario step wording in the shipped template is `- **WHEN** ... / - **THEN** ...`; the concepts doc and many docs use `GIVEN/WHEN/THEN/AND`. Both are accepted; the validator only checks for a trigger (WHEN/GIVEN) and an outcome (THEN) — [schemas/spec-driven/templates/spec.md](https://github.com/Fission-AI/OpenSpec/blob/main/schemas/spec-driven/templates/spec.md), [CHANGELOG 1.16.0](https://github.com/Fission-AI/OpenSpec/blob/main/CHANGELOG.md)
- Delta spec file (inside a change) uses `## ADDED / MODIFIED / REMOVED / RENAMED Requirements`; the shipped example:
  ```markdown
  # Spec Delta

  ## Purpose
  Lets users take their data out of the product in a portable format.

  ## ADDED Requirements

  ### Requirement: User can export data
  The system SHALL allow users to export their data in CSV format.

  #### Scenario: Successful export
  - **WHEN** user clicks "Export" button
  - **THEN** system downloads a CSV file with all user data

  ## REMOVED Requirements

  ### Requirement: Legacy export
  **Reason**: Replaced by new export system
  **Migration**: Use new export endpoint at /api/v2/export
  ```
  Rules: MODIFIED "MUST include full updated content" (copy the whole existing requirement block incl. all scenarios, then edit); REMOVED MUST include **Reason** and **Migration**; RENAMED uses `FROM:` / `TO:` lines; `## Purpose` in a delta is only used when the capability is brand new — [schemas/spec-driven/schema.yaml](https://github.com/Fission-AI/OpenSpec/blob/main/schemas/spec-driven/schema.yaml), [docs/concepts.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)
- `proposal.md` template sections today: `## Why`, `## What Changes` (mark `**BREAKING**`), `## Capabilities` (`### New Capabilities` / `### Modified Capabilities`, each a bullet `` `<capability-path>`: description ``), `## Impact`. The Capabilities list is "the contract between proposal and specs phases" — one delta spec file per listed capability — [schemas/spec-driven/templates/proposal.md](https://github.com/Fission-AI/OpenSpec/blob/main/schemas/spec-driven/templates/proposal.md)
- `design.md` template sections: `## Context`, `## Goals / Non-Goals` (with **Goals:** / **Non-Goals:**), `## Decisions` ("with rationale and alternatives considered"), `## Risks / Trade-offs` (`[Risk] -> Mitigation`). The schema instruction also names `Migration Plan` and `Open Questions`. design.md is meant to be optional ("create only if" cross-cutting, new dependency, security/migration complexity, ambiguity) — [schemas/spec-driven/templates/design.md](https://github.com/Fission-AI/OpenSpec/blob/main/schemas/spec-driven/templates/design.md), [schemas/spec-driven/schema.yaml](https://github.com/Fission-AI/OpenSpec/blob/main/schemas/spec-driven/schema.yaml)
- `tasks.md` template: `## 1. <Group>` headings with `- [ ] 1.1 ...` checkboxes. The apply phase parses checkboxes; only a box containing `x`/`X` counts as done (`- [~]`, `- [-]`, `- []` are "unfinished"). Current instruction requires each task to state how it is verified and forbids a catch-all "tests/docs" last group; archive/follow-up steps go as plain bullets under `## Workflow follow-up` — [schemas/spec-driven/schema.yaml](https://github.com/Fission-AI/OpenSpec/blob/main/schemas/spec-driven/schema.yaml)
- `.openspec.yaml` in a real change is minimal, e.g. `schema: spec-driven` / `created: 2026-02-17` — [openspec/changes/simplify-skill-installation/.openspec.yaml](https://github.com/Fission-AI/OpenSpec/blob/main/openspec/changes/simplify-skill-installation/.openspec.yaml)
- Archive destination: `openspec/changes/archive/YYYY-MM-DD-<name>/` with all artifacts preserved (proposal, design, tasks, delta specs). The repo itself is built with OpenSpec (about 44 specs, 108 archived changes at `main`) and is the best real-format reference — [openspec/](https://github.com/Fission-AI/OpenSpec/tree/main/openspec)
- Spec-vs-design boundary the project enforces: avoid in specs "internal class/function names, library or framework choices, step-by-step implementation details"; quick test: "if implementation can change without changing externally visible behavior, it likely does not belong in the spec." Progressive rigor: "Lite spec (default)" vs "Full spec" for cross-team/API/migration/security work — [docs/concepts.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)
- Validation limits in code: change needs `Why` of 50-1000 chars and non-empty `What Changes`; zero-delta change fails unless `.openspec.yaml` has `skip_specs: true`; more than 10 deltas triggers a "consider splitting" warning — [src/core/validation/constants.ts](https://github.com/Fission-AI/OpenSpec/blob/main/src/core/validation/constants.ts), [docs/cli.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md)

### Inferences
- The OpenSpec spec format is far narrower than our plan format: it holds only observable behaviour (requirements + scenarios) and has no place for steps, rollout, or alternatives outside `design.md`. Our `AC-01..` acceptance tests are the closest analogue to OpenSpec scenarios.
- Because `MODIFIED` needs the full block and scenario names are matched, stable requirement names matter (they are the merge key). Our AC-IDs would need to be turned into stable requirement/scenario names.

### Gaps
- I did not find a machine-readable JSON schema for the delta/spec grammar; the authoritative definition is the parser code (`src/core/parsers/requirement-blocks.ts`), which I only skimmed.

---

## 2. Commands, workflow and the 2026 changes (legacy /openspec:*, OPSX /opsx:*, schemas)

### Takeaway
Pre-1.0 OpenSpec had three phase-locked commands (`/openspec:proposal|apply|archive`) plus `openspec/project.md` and `openspec/AGENTS.md`. OpenSpec 1.0.0 (2026-01-26, "The OPSX Release") replaced them with action-based `/opsx:*` commands driven by a schema-defined artifact dependency graph; since 1.7 the default install is a small `core` profile (`explore, propose, apply, update, sync, archive`) with the rest opt-in.

### Cited Findings
- Timeline from GitHub releases: v0.10.0 2025-10-12, v0.23.0 2026-01-21, **v1.0.0 2026-01-26**, v1.1.0 2026-01-30, v1.3.0 2026-04-11, v1.5.0 2026-06-28, v1.7.0 2026-07-29, v1.10.0 2026-08-19, v1.12.0 2026-09-03, v1.14.0 2026-09-30, v1.16.0 2026-10-30, v1.16.1 2026-11-07 — `gh api repos/Fission-AI/OpenSpec/releases`; changelog at [CHANGELOG.md](https://github.com/Fission-AI/OpenSpec/blob/main/CHANGELOG.md)
- 1.0.0 breaking changes: old `/openspec:proposal|apply|archive` removed; tool-specific instruction files (`CLAUDE.md`, `.cursorrules`, `AGENTS.md`, `project.md`) no longer generated; instructions are now assembled dynamically from three layers: Context (config.yaml), Rules (per-artifact), Template. AI queries the CLI for artifact state — [CHANGELOG.md 1.0.0](https://github.com/Fission-AI/OpenSpec/blob/main/CHANGELOG.md), [docs/migration-guide.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/migration-guide.md)
- Migration: `openspec/project.md` is not auto-deleted; its content should move into `config.yaml` `context:`. Reason given: project.md was passive (agents "might read it, might not"), config context is "actively injected into every OpenSpec planning request" — [docs/migration-guide.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/migration-guide.md)
- Default `core` profile commands: `/opsx:propose` (create change + all planning artifacts), `/opsx:explore` (thinking partner, no code), `/opsx:apply`, `/opsx:update` (revise planning artifacts coherently, never edits code), `/opsx:sync`, `/opsx:archive`. Expanded set (enable with `openspec config profile` then `openspec update`): `/opsx:new`, `/opsx:continue`, `/opsx:ff`, `/opsx:verify`, `/opsx:bulk-archive`, `/opsx:onboard` — [docs/commands.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md)
- `/opsx:propose` = `new` + `ff`; `/opsx:continue` creates the next ready artifact (reads dependency files); `/opsx:ff` creates all artifacts until `apply.requires` artifacts exist; `/opsx:apply` works through `tasks.md` checkboxes and resumes from the first unchecked task; `/opsx:verify` checks Completeness, Correctness, Coherence and reports CRITICAL/WARNING/SUGGESTION but "does not block archive"; `/opsx:bulk-archive` archives several changes, resolves spec conflicts "by checking what's actually implemented", in chronological order — [docs/commands.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md)
- `/opsx:explore` can now scaffold a change and write artifacts when you say yes (earlier it only talked) — [docs/commands.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md), 1.12.0 notes on explore guidance in [CHANGELOG.md](https://github.com/Fission-AI/OpenSpec/blob/main/CHANGELOG.md)
- Command spelling varies per tool: `/opsx:propose` (Claude Code, Gemini CLI, Crush...), `/opsx-propose` (Cursor, Copilot IDE, Trae...), `@opsx-propose` (Amazon Q), `$openspec-propose` (Codex, skills-only), `/openspec-propose` (skills-only tools), `/skill:openspec-propose` (Kimi) — [docs/supported-tools.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/supported-tools.md)
- Built-in `spec-driven` schema dependency graph: `proposal` (requires []) -> `specs` (requires proposal) and `design` (requires proposal) -> `tasks` (requires specs, design); `apply: requires [tasks], tracks tasks.md`. "Dependencies are enablers, not gates": you can skip design; `requires` only determines what is *possible* and OpenSpec only checks that artifact files exist — [schemas/spec-driven/schema.yaml](https://github.com/Fission-AI/OpenSpec/blob/main/schemas/spec-driven/schema.yaml), [docs/concepts.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md); the "only checks files exist" caveat is stated in the anvil community schema header ([jikkujoyce/openspec-schemas](https://github.com/jikkujoyce/openspec-schemas/tree/main/schemas/anvil))
- Agent-facing CLI: `openspec status --change X --json` (artifact states `done|ready|blocked`, `isPlanningComplete`, `artifactPaths`), `openspec instructions <artifact|apply|archive> --change X --json` (template + context + rules + dependency content), `openspec templates`, `openspec schemas`, `openspec new change <id> [--schema S]` — [docs/cli.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md), [docs/agent-contract.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/agent-contract.md)
- Changes during 2026 (from CHANGELOG): `skip_specs: true` marker for zero-delta changes (merged 2026-07-22, PR "feat(validate): accept zero-delta changes that declare skip_specs") after issue #1212 showed the fast path (`propose`/`ff`) could finish and archive with `openspec/specs/` never updated; `retire_capabilities: true` to delete a capability whose last requirement is removed; `operations.apply|archive.guidance` in config (1.7.0); workflow skills published as static `skills/<name>/SKILL.md` so `npx skills add Fission-AI/OpenSpec` works (1.7.0); Codex became skills-only (1.7.0); new `update` command and "stores" (beta) for planning in a separate repo; single-binary install without Node (1.15.0, installer at openspec.dev, 1.16.0); `validate` warnings for scenarios lacking WHEN/THEN (1.16.0); tasks must state their verification (1.10.0); Node 20 dropped, now >=22.12.0 (1.16.0, breaking for npm installs) — [CHANGELOG.md](https://github.com/Fission-AI/OpenSpec/blob/main/CHANGELOG.md), [issue #1212](https://github.com/Fission-AI/OpenSpec/issues/1212)
- Legacy commands still described in docs as "older all-at-once workflow", but CHANGELOG 1.0.0 says they were removed; the commands doc's "Legacy Commands" section is therefore partly stale — [docs/commands.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md) vs [CHANGELOG.md 1.0.0](https://github.com/Fission-AI/OpenSpec/blob/main/CHANGELOG.md) (contradiction in sources)

### Inferences
- Our planner is conceptually `/opsx:explore` + `/opsx:propose` combined into one doc; our research skills correspond to `/opsx:explore` (which writes nothing unless asked). OpenSpec has no research artifact in its default schema.
- The "specs not produced by default fast path" failure (#1212) is directly relevant to a "specs after implementation" design: the spec step is the one that tends to be skipped, so an explicit gate is needed.

### Gaps
- Exact date and content of the first public "OPSX" experimental release (before 1.0.0) not checked; only the 1.0.0 changelog entry was read.

---

## 3. How archive merges deltas so specs/ reflects current implemented state (validate, archive, list/show, brownfield bootstrapping)

### Takeaway
`specs/` is kept current by a deterministic merge at archive time: `openspec archive <change> --yes` validates the change, applies each delta file's operations to the same-path main spec in the fixed order RENAMED -> REMOVED -> MODIFIED -> ADDED, then moves the folder to `archive/<date>-<name>/`. The agent-driven `/opsx:sync` and `/opsx:archive` do an "intelligent" merge instead. Crucially, OpenSpec does not verify that code matches the spec; "current implemented state" is only true if the delta was written (or corrected) to match what was actually built before archive. Brownfield bootstrap is incremental: no command back-fills specs from existing code, and the docs advise against it.

### Cited Findings
- CLI archive steps: validate (unless `--no-validate`); confirm (unless `--yes`; an agent/CI without stdin must pass `--yes`); claim the archive destination; validate and merge active delta specs into `openspec/specs/`; move to `openspec/changes/archive/YYYY-MM-DD-<name>/`; roll back specs if the merge or move fails — [docs/cli.md `openspec archive`](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md)
- Merge algorithm (code): applies operations in the order **RENAMED -> REMOVED -> MODIFIED -> ADDED**. Pre-checks: duplicate headers within a section, a requirement present in two sections (e.g. MODIFIED and ADDED), unpaired `FROM:`/`TO:`, requirements placed under an unrecognized `## ... Requirements` heading (hard error since 1.16.1). For a spec that does not exist yet, only ADDED is allowed (MODIFIED/RENAMED error; REMOVED ignored with warning) and `## Purpose` from the delta seeds the new spec, else placeholder `TBD - created by archiving change <name>. Update Purpose after archive.` — [src/core/specs-apply.ts](https://github.com/Fission-AI/OpenSpec/blob/main/src/core/specs-apply.ts) (`buildUpdatedSpec`)
- MODIFIED replaces the entire requirement block under the matching header (matching is whitespace-insensitive) and aborts if the current main spec contains scenarios missing from the modified block ("Refresh the change spec before archiving to avoid dropping scenarios") — this is the built-in drift guard against stale deltas — [src/core/specs-apply.ts](https://github.com/Fission-AI/OpenSpec/blob/main/src/core/specs-apply.ts)
- Idempotence ("early-sync" pattern): re-applying an already-synced ADDED/MODIFIED/REMOVED/RENAMED is a no-op rather than an error, so `/opsx:sync` before archive is safe — [src/core/specs-apply.ts](https://github.com/Fission-AI/OpenSpec/blob/main/src/core/specs-apply.ts)
- Retire a capability: put `retire_capabilities: true` in the change's `.openspec.yaml` next to `schema:`; otherwise archive stops before changing any files if a REMOVED would empty a spec — [docs/cli.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md)
- Agent-driven sync: `/opsx:sync` "is an **agent-driven** operation - you will read delta specs and directly edit main specs", allowing e.g. adding one scenario without restating the requirement; sync leaves the change active; `/opsx:archive` offers to sync if not yet synced; delta source is only `artifactPaths.specs.existingOutputPaths` from `openspec status --json` — [src/core/templates/workflows/sync-specs.ts](https://github.com/Fission-AI/OpenSpec/blob/main/src/core/templates/workflows/sync-specs.ts), [docs/customization.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md)
- Archive does not block on incomplete tasks, only warns; `openspec validate --archived` is a separate CI/pre-commit lint that fails if archived changes have unchecked tasks — [docs/commands.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md), [docs/cli.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md)
- `openspec validate [name] [--all|--changes|--specs] [--strict] [--json]`: structural validation of changes and specs, plus a check of a change's MODIFIED requirements against the main specs they would replace; `--strict` turns warnings (missing WHEN/THEN, Purpose <50 chars, requirement text >500 chars) into failures — [docs/cli.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md), [schemas/spec-driven/schema.yaml](https://github.com/Fission-AI/OpenSpec/blob/main/schemas/spec-driven/schema.yaml)
- Browsing: `openspec list` (active changes with task counts), `openspec list --specs`, `openspec show <name> [--type spec|change] [--json] [--requirements|--no-scenarios|-r N]`, `openspec view` (TUI dashboard). The schema's proposal instruction tells the agent to use `openspec list --specs` and `openspec show "<id>" --type spec --json --no-scenarios` to find existing capabilities before naming new ones — [docs/cli.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md), [schemas/spec-driven/schema.yaml](https://github.com/Fission-AI/OpenSpec/blob/main/schemas/spec-driven/schema.yaml)
- Pre-archive reconciliation guidance: "at archive time, your specs become the truth of record. So before you archive, make the specs honest about what the code does." If code diverged, update the delta spec to what shipped; `/opsx:verify` surfaces mismatches — [docs/editing-changes.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/editing-changes.md)
- Brownfield bootstrap: "You do not document your whole codebase to start. You write specs only for what you're about to change." `openspec/specs/` "starts nearly empty and accumulates." Existing PRDs are "source material for exploration, not specs to convert." Explicit caution: "Resist the urge to back-fill everything... Those specs go stale, because nothing forces them to track reality." The first change on a capability must use ADDED (MODIFIED needs an existing spec) — [docs/existing-projects.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/existing-projects.md), [src/core/specs-apply.ts](https://github.com/Fission-AI/OpenSpec/blob/main/src/core/specs-apply.ts)
- I found no built-in "generate specs from code" command in `docs/` or `src/commands` (grep for back-fill/reverse-engineer only returned the above caution). A community hosted service (Entalpa) imports existing `openspec/specs/` trees but does not generate them from code — [docs/community.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/community.md)
- Precedent for specs written after implementation: community schema `ml-research` (idealo) orders `proposal -> design -> evaluation -> tasks -> apply -> specs`, with the instruction "this is written POST-RESULTS... never up front", plus a `## Code State` section in the main spec describing "what the capability's code currently does... as it stands... edit in place rather than appending history" — [idealo/openspec-schemas ml-research](https://github.com/idealo/openspec-schemas/tree/main/openspec/schemas/ml-research) (schema read via GitHub API; also listed in [docs/customization.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md))
- Parallel changes: two changes can touch the same spec file without conflict if they modify different requirements; if they touch the same requirement, bulk-archive resolves by inspecting the code — [docs/concepts.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md), [docs/commands.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md)

### Inferences
- Reading the code, a minimal "post-implementation state record" flow is mechanically possible with the real CLI: write a change that contains only `proposal.md` (Why >=50 chars, What Changes, Capabilities) plus delta specs describing what was built, tick or omit tasks, then `openspec validate <change> --strict` and `openspec archive <change> --yes`. Untested (see version note); the proposal requirement comes from validation constants (`CHANGE_WHY_TOO_SHORT`, `CHANGE_WHAT_EMPTY`) so a bare delta without proposal.md would likely fail validation unless `--no-validate` is used (which also disables capability retirement).
- Honest limit: nothing machine-checks that specs match code (even `/opsx:verify` is an LLM search and non-blocking). For the "specs/ = current implemented state" claim to hold, the workflow must make the implementer (or a fresh-context reviewer) author or correct the delta *after* code is final.
- Because ADDED-only is permitted for new capabilities and later changes use MODIFIED with full blocks, a post-implementation record for an existing capability is written as MODIFIED/ADDED/REMOVED relative to what is already in `specs/`, which requires reading the current spec first.

### Gaps
- Could not run the CLI in this session, so exact validator output for a "proposal + delta only" change and for an empty tasks.md is unverified.
- Whether `openspec archive` fails when `tasks.md` is absent entirely: I did not find a documented answer (the archive skill template says it warns on incomplete tasks and uses `openspec list --json` counts; `list` shows "No tasks" for changes without tasks).

---

## 4. Configuration: config.yaml, context and rules injection, schema customization

### Takeaway
`openspec/config.yaml` has `schema:`, a free-text `context:` injected into every artifact prompt, per-artifact `rules:` injected only for the matching artifact, and (since 1.7) `operations.apply|archive.guidance`. Teams can fork or write schemas (`openspec/schemas/<name>/schema.yaml` + `templates/`) to add, remove or reorder artifacts, e.g. add a `research` or `plan` artifact.

### Cited Findings
- Example config and injection format (context in `<context>`, rules in `<rules>`, template in `<template>`; "Context appears in ALL artifacts; Rules ONLY appear for the matching artifact"):
  ```yaml
  schema: spec-driven
  context: |
    Tech stack: TypeScript, React, Node.js, PostgreSQL
    Testing: Jest + React Testing Library
  rules:
    proposal:
      - Include rollback plan
    specs:
      - Use Given/When/Then format
  operations:
    apply:
      guidance:
        - Run focused tests before the full suite
  ```
  — [docs/customization.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md)
- Real-world example: OpenSpec's own [openspec/config.yaml](https://github.com/Fission-AI/OpenSpec/blob/main/openspec/config.yaml) has `context:` (stack, "write specs in user-facing product behavior language", cross-platform requirements) and `rules:` for `specs`, `tasks`, `design`.
- Context is "a required prompt-level input"; operation guidance is "optional additive advice" and "not an enforceable check" — conflicting guidance is reported/not followed — [docs/customization.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md)
- Schema resolution order: `--schema` flag > change `.openspec.yaml` > project `config.yaml` > default `spec-driven`. User-level schemas live in `~/.local/share/openspec/schemas/` — [docs/customization.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md)
- Schema authoring: `openspec schema init <name>`, `openspec schema fork spec-driven <name>`, `openspec schema validate` (syntax, templates exist, no cycles), `openspec schema which --all`. A schema artifact has `id`, `generates` (globs allowed), `description`, `template`, `instruction`, `requires`; plus top-level `apply: {requires, tracks, instruction}`. Artifact list order decides which ready artifact comes first — [docs/customization.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md)
- Custom schema example in docs: `research-first` = `research` (requires []) -> `proposal` -> `tasks`, skipping specs/design — [docs/concepts.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)
- Community schemas catalog (not vendored): `intent-driven` (ADR manifest), `superpowers-bridge`, `nanopm`, `e2e-runbooks`, `anvil` (fresh-context read-only reviewer + test-plan mapping every scenario to a named test), `ml-research`, `epic-driven` — [docs/customization.md "Community Schemas"](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md)
- Multi-language: set a language instruction in `context:` or `openspec init --language` — [docs/multi-language.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/multi-language.md), CHANGELOG 1.10.0
- `x-*` top-level keys in `.openspec.yaml` are ignored by OpenSpec, allowing tool-specific metadata (e.g. a plan link) without breaking `validate --strict` — [docs/cli.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md)

### Inferences
- A thin custom schema is the sanctioned extension point for us: e.g. `plan` artifact with `generates: ../../docs/plans/...` is NOT supported (generated paths are kept inside the change directory per 1.14.3 "Keep glob artifact paths inside the change directory"), so an external `docs/plans/<feature>.md` would have to be referenced, not generated, by OpenSpec. This is an inference from the changelog line; the exact validation of `generates` paths was not tested.
- `config.yaml` `rules.specs` / `context` can carry our own conventions (e.g. "scenario names are AC-NN: ...") without schema changes.

### Gaps
- No documentation found on referencing external files from a schema artifact (e.g. reading `docs/research/*.md` as context); only `context:` free text and dependency artifacts inside the change directory are documented.

---

## 5. Supported tools and installation

### Takeaway
OpenSpec is a Node CLI (or single-file binary) that writes skills (`.../skills/openspec-*/SKILL.md`) and per-tool command files into the repo for 30+ assistants, including Claude Code, Codex, Cursor, Gemini CLI, Copilot, Kiro, OpenCode. The slash commands are thin generated prompts that call the `openspec` CLI for state; the CLI does no LLM work itself.

### Cited Findings
- Install: `curl -fsSL https://openspec.dev/cli/install.sh | sh` (macOS/Linux), `irm https://openspec.dev/cli/install.ps1 | iex` (Windows), `npm install -g @fission-ai/openspec@latest` (Node >=22.12.0), Homebrew `brew install openspec`, plus pnpm/yarn/bun/Nix — [README.md](https://github.com/Fission-AI/OpenSpec/blob/main/README.md)
- `openspec init [--tools claude,cursor|all|none] [--profile core|custom] [--language X] [--force]` creates `openspec/` and tool files; `openspec update` regenerates tool files after CLI upgrade or profile change (`--dry-run` since 1.15.0); `openspec config profile` selects workflows — [docs/cli.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md)
- Tool paths, e.g. Claude Code: skills `.claude/skills/openspec-*/SKILL.md`, commands `.claude/commands/opsx/<id>.md`; Codex: `.agents/skills/openspec-*/SKILL.md` only (invoked `$openspec-*`); Cursor: `.cursor/skills/...` and `.cursor/commands/opsx-<id>.md`; Gemini: `.gemini/commands/opsx/<id>.toml`; Copilot: `.github/prompts/opsx-<id>.prompt.md` (IDE only, not Copilot CLI); Zed and shared `agents` target use `.agents/skills/` — [docs/supported-tools.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/supported-tools.md)
- Delivery mode config: `skills`, `commands` or `both`; default `both` with `core` profile — [docs/cli.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md), [docs/supported-tools.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/supported-tools.md)
- Skill names generated: `openspec-propose`, `openspec-explore`, `openspec-apply-change`, `openspec-archive-change`, `openspec-sync-specs`, etc. (workflow templates in [src/core/templates/workflows/](https://github.com/Fission-AI/OpenSpec/tree/main/src/core/templates/workflows)); the skills are also published as static `skills/<name>/SKILL.md` for `npx skills add Fission-AI/OpenSpec` (CHANGELOG 1.7.0)
- Telemetry: anonymous command names/version only; off in CI; opt-out `OPENSPEC_TELEMETRY=0` or `DO_NOT_TRACK=1` — [docs/faq.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/faq.md)
- Because skills use the same `SKILL.md` format, OpenSpec's generated `openspec-*` skills could be installed next to our own catalog skills in `.claude/skills/` / `.agents/skills/` without a name clash (all prefixed `openspec-`).

### Inferences
- OpenSpec generating files into `.claude/`, `.agents/` etc. overlaps with our own render pipeline (`.ai/` -> tool folders). Installing OpenSpec in a platform repo would need to be decided against that renderer (e.g. use `openspec init --tools none` plus the static `skills/` from the OpenSpec repo, or exclude `openspec-*` from our rendering). This is a design consideration, not a documented procedure.

### Gaps
- No documented `--tools none` + manual skills copy path; I did not verify that the `skills/` folder in the repo is complete for all core workflows.

---

## 6. Context isolation and subagent use

### Takeaway
OpenSpec itself does not spawn subagents and has no built-in fresh-context reviewer. Its "fresh context" story is file-based: all plan state lives in change-folder files, so you can clear context and resume with `/opsx:apply`. Subagent/fresh-context behaviour exists only in third-party schemas that delegate to other tools (superpowers-bridge, anvil).

### Cited Findings
- Grep of `src/core/templates`, `docs`, `schemas` for subagent/sub-agent/fresh context found no OpenSpec-native mention; the only hits are the community schema rows in [docs/customization.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md) (and a `.agents` note in supported-tools.md about "subagent definitions" for the shared agents directory).
- FAQ: "you can clear your context, start a fresh AI session, and pick up with `/opsx:apply`; it reads the artifacts and resumes from the first unchecked task... Keeping a clean context window also produces better results; clear it before implementation." — [docs/faq.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/faq.md)
- README/FAQ recommend high-reasoning models for both planning and implementation (Codex 5.5, Opus 4.7 named) but there is no per-phase model routing — [docs/faq.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/faq.md)
- `/opsx:ff` "tracks progress via todo list" but runs in one session; `/opsx:bulk-archive` does "agentic" conflict resolution inline — [docs/commands.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md)
- `anvil` community schema: `review` artifact "is written by a fresh-context, read-only reviewer (a second model when one is available)" emitting a `VERDICT:` line that gates `test-plan`, `tasks`, `apply`; "OpenSpec only checks that artifacts exist, so enforce the gate with your own CI or hook"; `test-plan` maps every spec scenario to a named test and `verify` audits it — [docs/customization.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md), [anvil schema.yaml](https://github.com/jikkujoyce/openspec-schemas/tree/main/schemas/anvil)
- `superpowers-bridge` community schema: `brainstorm -> proposal -> design -> specs -> tasks -> plan -> verify -> retrospective`; apply uses git worktrees + `superpowers:subagent-driven-development`; it states it "does not support runtimes without subagent support" and prechecks that required Superpowers skills exist — [JiangWay/openspec-schemas superpowers-bridge/schema.yaml](https://github.com/JiangWay/openspec-schemas/tree/main/superpowers-bridge)

### Inferences
- Our catalog's fresh-context reviewers/subagents would be additive: OpenSpec offers no competitor feature, so there is no conflict. The anvil pattern (reviewer artifact gating later steps via a `VERDICT:` line) shows how a review gate can be modelled in a schema while enforcement stays external.

### Gaps
- Did not read the generated `apply-change` / `verify-change` skill bodies in full for any "launch a Task agent" language; the grep suggests none.

---

## 7. Criticisms, limits, and how teams combine OpenSpec with other workflows

### Takeaway
Most-cited limits: ceremony overhead on small changes, and spec drift because nothing mechanical ties specs to code; OpenSpec itself says do not back-fill and keep specs "lite". Community write-ups typically pair it with Superpowers (OpenSpec = what/archive, Superpowers = how/TDD), and the reported failure mode is duplicate planning artifacts (two plans, two task lists) unless one tool is told to own planning.

### Cited Findings
- Official positioning: "fluid not rigid"; "OpenSpec is lighter" than Spec Kit (README comparison); for "a one-character typo fix, the ceremony probably isn't worth it" — [README.md](https://github.com/Fission-AI/OpenSpec/blob/main/README.md), [docs/faq.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/faq.md)
- Drift is acknowledged by the project: "Those specs go stale, because nothing forces them to track reality" (on back-filling) and the editing guide on hand-edited code — [docs/existing-projects.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/existing-projects.md), [docs/editing-changes.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/editing-changes.md)
- GitHub issue #1212 (closed): with `propose`/`ff` + `apply` + `archive`, the change was "fully implemented, tested, and archived — but leaves `openspec/specs/` permanently out of date. No warning is raised"; cause: `applyRequires` for `spec-driven` does not include delta specs. Mitigated by `skip_specs` + validate requiring either deltas or the explicit opt-out (PR merged 2026-07-22) — [issue #1212](https://github.com/Fission-AI/OpenSpec/issues/1212), [src/core/validation/constants.ts](https://github.com/Fission-AI/OpenSpec/blob/main/src/core/validation/constants.ts)
- Third-party review (CodeMySpec) lists: specs don't self-update; "validate checks structure only, and verify 'won't block archive'"; Given/When/Then optional; no behavioral verification; overhead on small work; no multi-agent orchestration; reports ~250 lines per change for OpenSpec vs ~800 for Spec Kit (figure attributed to an Augment Code roundup and labeled "reported"); quotes a Hacker News user who stopped syncing because specs "keep drifting and drifting until you have duplication and contradictions across specs" — [codemyspec.com/blog/openspec-vs-spec-kit](https://codemyspec.com/blog/openspec-vs-spec-kit) (secondary source; anecdotal)
- Search-snippet-level reports (not fetched in full): one user producing a 100+ line spec for a 10-line change and building a lighter "fast lane"; a 2026 review saying a drift check now aborts archive when the change spec is stale, though parallel changes can still cause it — [HN thread](https://news.ycombinator.com/item?id=49734264), [vibecodinghub review](https://vibecodinghub.org/blog/openspec-review) (treat as anecdotal; not verified)
- Combining with Superpowers (Austin Xu write-up): "Superpowers designs and builds; OpenSpec tracks and archives." Sequence per feature: `superpowers:brainstorming` -> `opsx:propose` (uses brainstorm output to produce proposal/design/tasks) -> Superpowers TDD executes tasks in batches with review -> `opsx:apply` verifies tasks checked -> `opsx:archive` merges delta into main spec. Reports tasks.md (~60 lines, one sentence per task) vs a superpowers plan.md (~1300 lines) sharing the same spec as source of truth; suggests diffing them as a completeness check. Reported failure: Superpowers "silently dropped existing desktop functionality" when implementing against a mock without re-reading the spec — [austinxyz.github.io blog](https://austinxyz.github.io/blogs/blog/openspec-superpowers-combined)
- Hands-on test of 3 OpenSpec+Superpowers connection points, 2 failed: the spec reviewer checked superpowers' plan file instead of OpenSpec `specs/`; `writing-plans` ignored `tasks.md` and generated its own 7-task plan, so two task lists never sync; mapping WHEN/THEN to TDD never triggered — [besthub.dev article](https://besthub.dev/articles/openspec-superpowers-integration-3-connection-points-tested-2-failed-a-hands-on-review-46e64163b70d) (single-author secondary source)
- Search summary (unfetched) of other combination write-ups: one rule says "start new features with `/opsx:propose` and do not run Superpowers brainstorming or writing-plans because OpenSpec owns planning"; another maps stages Open (openspec-explore+propose) / Design (superpowers brainstorm + writing-plans) / Build (subagent-driven-development) / Verify (openspec-verify-change + finishing-a-development-branch) — [heyuan110.com](https://www.heyuan110.com/posts/ai/2026-06-28-openspec-superpowers-workflow/), [austinxyz blog](https://austinxyz.github.io/blogs/blog/openspec-superpowers-combined) (these were only seen as search results, not read in full)
- Official bridge: `superpowers-bridge` community schema integrates the two inside OpenSpec's artifact graph and adds an evidence-first `retrospective` artifact — [docs/customization.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md)
- No GSD-specific integration found in OpenSpec docs or the community-schema table; `nanopm` (PM-first, upstream of implementation) and `epic-driven` are the other documented bridges — [docs/customization.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md)
- Multi-repo: README/docs say single-repo OpenSpec is the default; "Stores" (beta) let planning live in its own repo shared across code repos (`openspec store setup`, `--store <id>`, `store:` pointer in config) and "Command names, flags, file formats, and JSON output may still change" — [README.md](https://github.com/Fission-AI/OpenSpec/blob/main/README.md), [docs/stores-beta/user-guide.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/stores-beta/user-guide.md); older issue [#725](https://github.com/Fission-AI/OpenSpec/issues/725) requested multi-repo spec management and is open

### Inferences
- Observed pattern across sources: the integration breaks when two tools both write a plan/task list. A design where OpenSpec holds *only* the post-implementation behaviour record, while our planner keeps `docs/plans/`, avoids that duplication by construction.
- Drift risk is highest if specs are written first (before implementation) and not revisited; writing/reconciling them after implementation removes the main drift window but moves the risk to "agent describes what it intended rather than what exists" — mitigated by a fresh-context reviewer comparing delta to code (verify-style).
- The platform lab is a multi-repo workspace (service/web/agent/MCP repos); OpenSpec's in-repo `openspec/` fits one repo each, and the cross-repo "stores" feature is still beta, so per-repo `openspec/specs/` is the lower-risk option.

### Gaps
- Could not read the HN thread or vibecodinghub review in full; those claims are search-snippet-level.
- No measured data (time, tokens, bug rates) on OpenSpec overhead or drift; all evidence is anecdotal or opinion.
- No GSD + OpenSpec write-up found.

---

## 8. Mapping OpenSpec artifacts to our plan sections, and the lightest integration

### Takeaway
Our plan sections map cleanly onto `proposal.md` (goals/non-goals/scope), `design.md` (design, alternatives), `tasks.md` (steps) and delta specs (acceptance tests as requirements+scenarios), with rollout fitting `design.md`'s Migration Plan. The lightest, least-duplicating integration is to keep `docs/plans/<feature>.md` and `docs/research/*.md` as the pre-implementation artifacts and use OpenSpec only for `openspec/specs/` (current behaviour) plus an archive of change records, written or reconciled after implementation.

### Cited Findings
Mapping table, built from the template/instruction files cited in sections 1-3 ([schemas/spec-driven/](https://github.com/Fission-AI/OpenSpec/tree/main/schemas/spec-driven)):

| Our plan section | Nearest OpenSpec artifact | Notes |
|---|---|---|
| Goals | `proposal.md` -> `## Why` + `## What Changes` | |
| Non-goals | `proposal.md` scope / `design.md` `**Non-Goals:**` | The shipped template has Non-Goals in design.md only; concepts.md's proposal example has "Out of scope". |
| Design | `design.md` -> `## Context`, `## Decisions` | |
| Alternatives | `design.md` -> `## Decisions` ("Include alternatives considered for each decision") | |
| Acceptance tests AC-01.. | delta/main spec `### Requirement:` + `#### Scenario:` (WHEN/THEN) | Strongest overlap; scenarios are explicitly "potential test cases". anvil's `test-plan` maps scenarios to named tests. |
| Steps | `tasks.md` (`## N.` groups, `- [ ] N.M` with verification) | Apply tracks completion via checkboxes. |
| Rollout | `design.md` -> `Migration Plan` (rollback strategy) | Part of schema instruction, not in template skeleton. |
| Risks | `design.md` -> `## Risks / Trade-offs` | |
| (research notes) | none in default schema; custom `research` artifact (`research-first` example) or `/opsx:explore` (no artifact unless asked) | |
| (post-implementation state) | `openspec/specs/**/spec.md` after archive; archive folder is the change record | The unique capability. |

Evidence behind "lightest integration" options (each option's mechanics are documented above):
- Option A, specs-only after implementation: the pieces exist in the CLI — change folder, delta spec, `validate`, `archive --yes` — but proposal is required by validation (Why >=50 chars, What Changes) unless the change is `skip_specs` (which defeats the purpose). `ml-research` is a published precedent of putting `specs` last in the artifact order ([schema](https://github.com/idealo/openspec-schemas/tree/main/openspec/schemas/ml-research)).
- Option B, `x-*` metadata link: `.openspec.yaml` allows user `x-*` keys that OpenSpec never reads or reports ([docs/cli.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md)), usable to link a change to `docs/plans/<feature>.md`.
- Option C, custom schema: `openspec schema fork spec-driven <name>`, then reorder or drop artifacts (e.g. `proposal` -> `tasks` -> `specs` with `specs` instructed to be written post-implementation from the plan's AC list), configured via `schema:` in `config.yaml` ([docs/customization.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md)).
- Option D, keep only `specs/` + `archive/`: nothing in the CLI requires `changes/` to be retained beyond archive; archive is where the change record lives, so `changes/archive/` plus `specs/` is exactly the "two-tree" minimum. Active `changes/` is empty between features.

### Inferences
- Recommended lightest path (inference, not documented by OpenSpec): (1) planner and research skills unchanged; (2) after implementation, a new "record-state" step spawns a fresh-context agent that reads the plan's AC list, the diff and the tests, and writes a delta spec per affected capability (ADDED for new, MODIFIED with the full existing block for changed, REMOVED with Reason/Migration), plus a short `proposal.md` whose Why/What Changes point at `docs/plans/<feature>.md` instead of restating it; (3) `openspec validate <change> --strict` then `openspec archive <change> --yes`; (4) a reviewer pass using verify-style Completeness/Correctness/Coherence against the code before archive. This keeps AC-IDs as stable scenario names and avoids duplicate plan/task lists, the failure mode reported in the Superpowers write-ups.
- Do not adopt `design.md`/`tasks.md` generation: they duplicate the plan's Design/Steps sections and are the source of the "two plans" problem. Keep them as optional/empty in a custom schema, or set the schema's `apply.requires` to nothing the plan already covers.
- Consider alternatives in order of effort: (a) only borrow the format (hand-maintained `docs/specs/<capability>.md` with Requirement/Scenario blocks, no OpenSpec dependency) — cheapest, loses automatic delta merge; (b) adopt just `openspec validate`+`archive` for merge mechanics; (c) full OpenSpec with a custom schema.
- Granularity guidance for our repos: capabilities per service API surface (reservation, seat-hold, payments, recommendations) as nested paths, one `openspec/` per repo; avoid cross-repo capabilities until stores leave beta.
- Install collision check needed: OpenSpec writes into `.claude/skills/`, `.agents/skills/`, etc., which our `.ai/` renderer owns; use `openspec init --tools none` or a dedicated scratch repo first (per skill-bundle AGENTS.md, installing/rendering in a real platform repo is a separate issue/PR).

### Gaps
- No empirical test of Option A; confirm in a scratch repo that `validate` and `archive` accept a proposal-light change and that `tasks.md` can be omitted or empty.
- Whether a custom schema can legally have no `tasks`/apply artifact (so `/opsx:apply` is irrelevant) was not checked; `apply.requires` is documented as a schema field but its behaviour when empty is unverified.
- Whether `generates` can point outside the change directory (e.g. `docs/plans/`): changelog 1.14.3 suggests glob paths are kept inside the change directory; not verified in code.
