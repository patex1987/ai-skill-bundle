# Plan: Plan lifecycle, durable project memory, and missing workflow skills

Status: draft (no implementation authorized yet).
Test agreement: **proposed** (the author has not yet agreed the scenarios in section 9).
Planning depth: design review (new skills, changes to the core workflow skills, a script, and a validator change).

## 1. Summary

A comparison of this catalog with the leading skill repos (Pocock's skills,
Superpowers, GSD, OpenSpec; research dated 2026-11-07) found that the catalog is
ahead on human gates (user-agreed acceptance tests, a written annotation cycle,
independent validation, tier routing across four tools) and behind on **memory**
and **isolation**:

- Nothing records what was actually built, what decisions were made, or what the
  architecture looks like now. Plans have no status, and stay in `docs/plans/` as
  they are, so the current state has to be reverse-engineered from code.
- Research and planning always run in the same session, with no per-phase choice of
  a fresh-context subagent.
- There is no debugging skill, ADR skill, diagramming guidance, size budget, or
  deterministic plan check.

The recommended approach is a small, human-gated lifecycle, not an adopted spec
framework: plans are working documents with a `Status:`; durable knowledge lives in
`docs/architecture/` and `docs/adr/`; the author periodically runs a **sweep** that
promotes what matters from finished plans and deletes only what they approve.

Research record (local, currently untracked, not required to execute this plan):
`docs/reports/Agent skill repos comparison.md` and `docs/research_notes/Agent skill repos comparison/`.

## 2. Goals

- G1. Record post-implementation state and decisions so a new session can read the
  repo's current shape without rereading the code.
- G2. Keep plans and research as short-lived working documents, without losing
  anything worth keeping.
- G3. Let the author choose, per phase, whether work runs inline or in a
  fresh-context subagent that reads only the previous phase's written output.
- G4. Add the missing skills: `adr`, `debugging`, `mermaid-diagrams`,
  `branch-workflow`, and `plan-sweep`.
- G5. Add a customer-first step to planning for user-facing work.
- G6. Add deterministic checks: a plan lint script and a size budget in `validate`.

## 3. Non-goals

- Adopting OpenSpec or any other external spec framework (parked; see section 8).
- Making external skills (for example `diagram-design`) catalog dependencies.
- Running the new evals against a model (they are written, not run; see section 9).
- Installing into or rendering in a consuming repository (a separate task, in that
  repository's own issue, branch, and PR).
- Auto-deleting plans, or writing documents without the author's approval.
- Project-specific content in the catalog: no mention of any particular platform's
  files (for example an orchestration workspace's context file).

## 4. Current state (evidence)

All from the audit in `docs/research_notes/.../local_catalog_baseline.md` (cites are file
and line at audit time):

- Workflow skills: `codebase-research`, `external-research`,
  `principal-engineer-planner` (371 lines, about 15 KB), `plan-execution` (44),
  `plan-validation` (39), `model-routing`, all in the `core` pack.
- Files written: `docs/research/*`, `docs/plans/<feature>.md`,
  `docs/plans/<feature>-review.md`, `docs/validation/<task>.md`. Nothing records the
  as-built state, a decision log, or a current architecture.
- The planner template has no `Status:` field, no archival step, and no section
  about docs to update, although its handoff prompt says "Update docs described in
  the plan" (`principal-engineer-planner/SKILL.md:291`).
- `docs/workflow.md` says to keep research, planning, and implementation in one
  session. Subagents appear only as `scout`, `check-runner`, and independent
  validation or review.
- `bundle.json` rejects unknown top-level keys (`scripts/aibundle.py:296-298`).
  Overlays (`.ai/overlays/<skill>.md`) are the zero-code way to carry a per-repo
  setting.
- A skill folder under `.ai/skills/` that the catalog does not provide is a local
  entity and renders like any other. This was tested on a scratch repo with a
  third-party skill (2026-11-08) and is now documented in `README.md`
  ("Adding skills from other sources", uncommitted at the time of writing).
- Five skills have evals (`principal-engineer-planner`, `pr-walkthrough`,
  `typescript`, `typescript-style`, `rust-style`); the core workflow skills
  `plan-execution`, `plan-validation`, and `codebase-research` have none.
  `validate` has no size check.

Peer findings that shaped the design (versions read 2026-11-07): Superpowers 7.0.2
deletes its run workspace and offers a subagent-driven versus inline choice at plan
handoff; GSD (now `open-gsd/gsd-core`) writes a per-plan `SUMMARY.md` and updates
`STATE.md` and `PROJECT.md`; OpenSpec 1.16.1 merges delta specs into
`openspec/specs/` at archive but never checks them against code; Pocock's repo
gates ADRs on three tests and requires a fresh context for every subagent.

## 5. Requirements, decisions, and assumptions

### Decisions (author, in the planning Q&A of 2026-11-07/08)

| ID | Decision |
|---|---|
| D1 | Durable state lives per repository in the `docs/architecture/` folder, hand-managed and written at the end of finishing work or on demand. `overview.md` is the entry point and further architecture documents can be added to the folder. Plans carry a `Status:` field. |
| D2 | Stale plans are removed by a **sweep** that the author runs. Plans stay in place until then. The sweep promotes useful content (architecture, ADRs, lessons) and deletes only what is approved. |
| D3 | The plan gets a **Docs impact** forecast. Close-out reconciles it against what was built. The doc diff in the PR is the delta; there is no separate delta file. Deviations go in the plan's as-built section. |
| D4 | Per-phase isolation is a choice, implemented first as overlay text (no `bundle.json` key). Defaults: research and validation in a fresh-context subagent; planning and execution inline. Overridable per task at handoff or per repository. |
| D5 | An `adr` skill. The planner lists ADR candidates; the ADR is written at sweep or on demand. Minimal MADR format, `docs/adr/NNNN-title.md`, a three-part significance test, default to writing nothing. |
| D6 | A small `mermaid-diagrams` skill for documentation. `diagram-design` and similar tools stay optional per-repository additions. |
| D7 | A customer lens inside the planner, for user-facing and new-capability work only. |
| D8 | A `debugging` skill built on a reproduce-first ladder and an explicit "cannot reproduce locally" rule. |
| D9 | A size-budget check in `validate` now; each new skill ships with evals. |
| D10 | Close-out is the last step of `plan-validation`. Sweep is its own explicit-invocation skill. |
| D11 | In scope: a phase-boundary guide, a plan lint script, and a worktree and finish-branch flow. OpenSpec is parked. |
| D12 | The planner's plan template moves into `references/plan-template.md` to hold the size budget (answer to former Q1). |
| D13 | `docs/architecture/` is a folder. `overview.md` is its entry point, and more architecture documents are added as needed (answer to former Q2). |
| D14 | The sweep leaves no separate record. The cleanup commit is the record (answer to former Q3). |
| D15 | The names `plan-sweep`, `adr`, `debugging`, `mermaid-diagrams`, and `branch-workflow` are accepted. A rename is cheap if `adr` confuses anyone (answer to former Q4). |

### Assumptions (mine; correct them in review)

- A1. Add the new entities (`plan-sweep`, `adr`, `debugging`, `mermaid-diagrams`,
  `branch-workflow`; names accepted, D15) to the `core` pack. The Mermaid skill may
  fit better in its own pack; decide when it is written (slice 3).
- A2. `Status:` values: `draft`, `agreed`, `in-progress`, `done`, `abandoned`.
  Sweep considers `done` and `abandoned` plans, or any plan the author names.
- A3. Close-out is skipped for light plans (Docs impact "None" and no deviations).
- A4. `plan-sweep` is explicit-invocation only (`metadata.invocation: explicit`).
- A5. Suggested tiers: `adr` balanced/medium, `plan-sweep` balanced/medium,
  `debugging` balanced/medium (escalate to deep for concurrency and data bugs),
  `mermaid-diagrams` fast/medium, `branch-workflow` fast/low. Final values follow
  the `model-routing` rules when the entities are written.
- A6. The plan lint script is Python standard library only, like `render.py`.
  It warns (not fails) on a missing `Status:` for pre-existing plans unless run
  with `--strict`.
- A7. The "Five Questions" are attributed cautiously: they come from secondary
  sources, not from Amazon's own pages.

### Open questions

None. The four questions raised in the first draft are answered as D12 to D15.

## 6. Proposed design

### Slice 1 — Lifecycle (planner, plan-validation, plan-sweep, adr)

- **Planner** (`principal-engineer-planner`): add `Status:` (A2) to the plan header;
  add a **Docs impact** section (architecture sections that will change; ADR
  candidates, each with the decision and the rejected alternative; behaviour or
  contract changes and where their tests live; "None" for light plans); add an
  empty **As-built** section placeholder. Move the plan template into
  `references/plan-template.md` (D12) so these additions do not grow the skill.
- **`plan-validation`**: after a `verified` verdict, a close-out step: set
  `Status: done`; write the **As-built** section (deviations from the plan, with
  reasons); reconcile Docs impact (each item done, or dropped with a reason);
  propose edits to the `docs/architecture/` documents (usually `overview.md`) for the
  author's approval.
  Skipped for light plans (A3). It deletes nothing.
- **`plan-sweep`** (new, explicit invocation): reads plans with Status `done` or
  `abandoned` (or ones the author names) plus the research, review, and validation
  files they link. It checks the plan's as-built claims against the code first, and
  does not trust them. For each plan it proposes where content should go:
  architecture overview, an ADR (via `adr`), a lesson, or nowhere. A lesson's
  destination is the author's choice among a repository overlay, an agent
  instruction rule, a lint or check, a hook, or a user memory where the tool has
  one. It edits only after approval and deletes only files the author approves, per
  file. It leaves no separate record: the cleanup commit is the record (D14).
- **`adr`** (new): modes `propose`, `record`, `supersede`, and `extract-from-plan`
  (used by sweep). Significance test (all three): hard to reverse, surprising
  without context, a real trade-off. Default is to write nothing. Needs a named
  rejected alternative. Minimal MADR layout, lazy creation of `docs/adr/`, an index,
  sequential numbering, status lifecycle (`proposed`, `accepted`, `superseded`,
  `deprecated`), accepted ADRs immutable except through a superseding ADR.
- **Architecture documents convention**: `plan-sweep/references/architecture-docs.md`,
  linked from `plan-validation`. It describes the `docs/architecture/` folder (D13):
  `overview.md` as the entry point, with further documents added as needed. The overview's sections: purpose and boundaries, components, data
  and control flow, external dependencies, key decisions (links to ADRs), known
  gaps, and "last verified against <commit>".

### Slice 2 — Debugging, isolation setting, phase boundaries

- **`debugging`** (new): trigger on bugs and unexpected failures. Gate: no
  hypotheses until a command that fails on this exact bug has been run.
  Reproduction ladder, cheapest first: failing unit or characterization test;
  synth or assertion test for infrastructure; running the CI script or workflow
  locally; local container or emulator; a real environment last, read-only first
  and with the smallest probe. Each rung records the evidence it gives and the
  boundary it leaves untested. Hypotheses carry a state (`needs verification`,
  `likely`, `confirmed`, `rejected`), and `confirmed` requires a reproduction or a
  probe observation. For failures that cannot be reproduced locally (identity and
  access, networking, managed-service behaviour), the skill names what cannot be
  reproduced and the smallest real-environment probe that would settle it, and asks
  before running anything that changes state. Then root cause before fix, and a
  regression test. Links to `cdk-infra-testing`, `github-actions-authoring`, and the
  testing skills when installed. Optional hint: consult the user's knowledge base
  through `programming-kb` if it is enabled (explicit invocation rules still apply).
- **Isolation setting**: a short "Isolation" paragraph in `codebase-research`,
  `external-research`, `principal-engineer-planner`, `plan-execution`, and
  `plan-validation`, stating the default (D4), that an overlay or the handoff
  choice overrides it, and the delegation contract: the subagent receives file
  paths, not pasted text; reads only the named inputs; and writes its output to a
  named file. The planner's handoff asks which mode to use and records the answer in
  the plan. A promotion to a validated `bundle.json` key is deferred until two or
  more repositories use the setting.
- **Phase-boundary guide**: a section in `docs/workflow.md` giving, for each phase
  boundary, when to continue, clear context, hand off to a fresh subagent, or
  compact. Documents per-tool differences from `tool-mechanics.md` (for example that
  a Codex agent's pinned model blocks per-spawn escalation).

### Slice 3 — Diagrams, customer lens, external skills docs

- **`mermaid-diagrams`** (new): scope is documentation diagrams in markdown. When a
  diagram earns its place; a type chooser; pitfalls with failing and fixed pairs;
  a portability profile that uses stable diagram types for GitHub-rendered docs;
  where diagrams belong (plans, ADRs, the overview); a caption stating the question
  each answers. `scripts/check-mermaid.py` extracts fenced `mermaid` blocks and runs
  static checks (known type keyword, lowercase `end` as a node label, unbalanced
  brackets or quotes, size), and runs `mmdc` per block when available, with a clear
  message when it is not. Renderer-compatibility notes carry a "date checked".
  `diagram-design` is named as an optional per-repository companion.
- **Customer lens** in the planner (D7): for user-facing and new-capability work, a
  short section answering five questions (customer, problem, most important benefit,
  how we know, experience), each with an evidence tag (observed, reported, assumed,
  unknown), plus 5-8 hostile questions of which at least one stays unanswered.
  Unknowns feed the planner's questions. Skipped for refactors, infrastructure,
  dependency upgrades, and bugs with a clear reproduction.
- **README**: the "Adding skills from other sources" section (already drafted).

### Slice 4 — Tooling and branch flow

- **Plan lint script** (`principal-engineer-planner/scripts/lint-plan.py`): checks
  that `Status:` is present and valid, Docs impact is present, every AC ID used in
  steps has a row in the acceptance table, every step names a verification and a
  tier, and the handoff prompt exists. Exit 1 with one line per finding.
- **Size budget in `validate`**: fail when a `SKILL.md` exceeds a character limit
  chosen from measurement (candidate 20,000, the re-attach limit Superpowers tests
  against, with a lower warning threshold). A test covers a fixture over the limit.
- **`branch-workflow`** (new): `isolate` (a git worktree or branch per issue) and
  `finish` (run the agreed checks, then present options: open a PR, keep, or
  discard). It never pushes, merges, closes issues, or deletes branches without
  explicit user instruction.

## 7. Interfaces, data, security

- New files and frontmatter only. `bundle.json` and the lock schema are unchanged.
- Every new entity needs `metadata.routing-tier` and joins a pack; the portability
  lint must stay clean (no host paths, project names, or vendor model IDs).
- Security and abuse: `plan-sweep` and `branch-workflow` can delete or discard
  files, so both require per-item approval and never act on silence. `debugging`
  must not run state-changing operations against real environments without asking.
  The Mermaid script runs `mmdc` only on extracted fenced blocks and never executes
  document content. Third-party skills are reviewed before use (README).
- Performance: the main cost is always-loaded text. Keep each new `SKILL.md` small
  and move detail to `references/`. The generated index grows by one line per skill.

## 8. Alternatives considered

| Option | Decision |
|---|---|
| Adopt OpenSpec for the current-state snapshot | Rejected for now. Its specs describe behaviour, which acceptance tests already cover and keep honest. It adds a CLI dependency, can collide with `.ai/` rendering, and its archive model keeps every change forever, against the sweep model. Nothing checks specs against code. Untested here. Revisit if a service becomes a contract other repositories depend on. |
| Auto-delete plans at close-out | Rejected by the author: the sweep lets them pull useful content from plans before deletion, and also feeds lessons. |
| Always-on fresh-context subagents (GSD-style) | Rejected as a default: GSD's own docs concede cold-start overhead and a reported high token cost. Kept as a per-phase choice. |
| A validated `bundle.json` isolation key now | Deferred. It needs changes to `aibundle.py`, `render.py`, tests, and docs, for a setting no repository has used yet. |
| A separate delta file per change | Rejected: the plan's Docs impact plus the doc diff covers it, and a delta file would be deleted with the plan. |
| Full Working Backwards (PR/FAQ) skill | Deferred: the lens is cheaper, and a brief would be a new document type for the sweep. Revisit if the lens grows. |

## 9. Testing strategy and acceptance scenarios (proposed, not agreed)

The new skills are prose, so structure is tested automatically and behaviour only
through evals that are **written but not run against a model** (same limitation as
the earlier TypeScript plan and the review log's "behaviour not evaluated" note).
Any claim that a skill changes agent behaviour stays unproven until evals are run.

Common commands run from the `skill-bundle` root.

| ID | Setup / action | Observable expected result | Level / file | Command | Pre-change expectation |
|---|---|---|---|---|---|
| AC-01 | Catalog with all new entities | `validate` passes: names unique, tiers present, packs resolve, portability lint clean | catalog, `scripts/aibundle.py` | `python3 scripts/aibundle.py validate` | Fails or lacks the entities |
| AC-02 | Fixture skill whose `SKILL.md` exceeds the size limit | `validate` fails naming the skill; every current catalog skill passes | unit, `tests/` | `python3 -m unittest discover -s tests` | Oversized skill passes |
| AC-03 | Scratch repo, `core` pack installed and rendered | New skills appear under `.claude/skills` and `.agents/skills`; `plan-sweep` is explicit-only; `render.py --check` is clean | integration, scratch repo | `aibundle.py install`, `.ai/render.py`, `.ai/render.py --check` | Skills absent |
| AC-04 | A complete fixture plan | `lint-plan.py` exits 0 | unit, fixture | `python3 catalog/skills/principal-engineer-planner/scripts/lint-plan.py <fixture>` | Script missing |
| AC-05 | Fixture plans missing Status, Docs impact, or an AC row referenced by a step | Exit 1, one line per finding naming the section | unit, fixtures | same | Script missing |
| AC-06 | Markdown with valid and broken Mermaid blocks (lowercase `end` node, unbalanced bracket, unknown type), run with and without `mmdc` | Each defect reported with file and line; without `mmdc` the script says it ran static checks only | unit, fixtures | `python3 catalog/skills/mermaid-diagrams/scripts/check-mermaid.py <fixture>` | Script missing |
| AC-07 | Each new skill and the `plan-validation` close-out step | An `evals.json` exists with at least three scenarios, including one negative (should not write, delete, or trigger); structure validated by a test | unit | `python3 -m unittest discover -s tests` | Missing |
| AC-08 | Planner `SKILL.md` after changes | Within the size budget and under 500 lines, with the template in `references/` (D12) | unit | `validate` plus line count | Currently about 15 KB; would grow without the template move |
| AC-09 | Docs and README links | `README.md`, `docs/workflow.md`, and `docs/REVIEW-LOG.md` describe the lifecycle, sweep, isolation setting, and phase boundaries; relative links resolve | manual plus link check | reviewer reads the diff | Not described |

Evidence that completes each criterion: command output for AC-01 to AC-08 and a
reviewer's read of the diff for AC-09. Behavioural claims are recorded as "evals
written, not run". Material acceptance changes during execution need renewed
agreement. Extra tests that preserve the agreed behaviour do not.

## 10. Implementation steps

Four slices, each its own issue, branch, and PR. Order matters: slice 1 first,
because slices 2 and 3 edit the same planner file. Tests and baselines come first in
every slice. Tiers are hints and never relax verification (see `model-routing`).

**Slice 1 — Lifecycle**
1. Baseline: run `validate` and the unit tests; record the planner size. Tier: fast.
2. Move the planner template into `references/plan-template.md` first, as its own
   commit, and confirm the planner still triggers and validates. Tier: balanced.
3. Tests first: AC-01 and AC-07 structure checks for the new entities (expected to
   fail). Tier: balanced.
4. Write `adr`, `plan-sweep` (with `references/architecture-docs.md`), the
   planner changes (Status, Docs impact, As-built, optional template move), and the
   `plan-validation` close-out step; add to packs with tiers. Tier: deep for the
   sweep and close-out wording (deletion and promotion decisions); balanced for the
   rest.
5. Write evals for the new and changed skills (AC-07). Tier: balanced.
6. Update `README.md`, `docs/workflow.md`, `docs/REVIEW-LOG.md`. Run AC-01, AC-03.
   Tier: fast.

**Slice 2 — Debugging and isolation**
7. Tests first (structure and evals). Tier: balanced.
8. Write `debugging` and its references; write the Isolation paragraphs; add the
   phase-boundary section to `docs/workflow.md`. Tier: deep for the isolation
   contract and the "cannot reproduce" rule; balanced otherwise.
9. If tool-specific claims change, update `tool-mechanics.md` with the date
   checked. Verify AC-01, AC-03, AC-07.

**Slice 3 — Diagrams, customer lens, README**
10. Tests first: AC-06 fixtures for `check-mermaid.py` (expected to fail). Tier:
    balanced.
11. Write `mermaid-diagrams` and the script; verify against a real `mmdc` and a real
    GitHub render before writing any renderer-compatibility claim, otherwise mark
    it untested. Tier: balanced.
12. Add the customer lens to the planner. Commit the README section on external
    skills. Tier: balanced.

**Slice 4 — Tooling and branch flow**
13. Tests first: AC-02, AC-04, AC-05 (expected to fail). Tier: balanced.
14. Implement the size budget in `validate`, `lint-plan.py`, and `branch-workflow`.
    Tier: balanced; fast for the fixtures.
15. Final pass: AC-01 to AC-09; record in `docs/REVIEW-LOG.md` what was added and
    what is untested. Tier: balanced.

## 11. Rollout

The catalog is a git repository, so each slice merges independently. Existing
plans remain valid: `Status:` and Docs impact are optional for them (A6). Consuming
repositories pick up changes on their next `install`. Locally edited managed
entities block the update, as designed. Rollback is a revert of the slice's PR.

## 12. Risks and mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Close-out becomes a second source of truth, or records intent instead of reality | Medium | Medium | Sweep verifies as-built claims against code; overview carries "last verified against <commit>" |
| Ceremony on small changes | Medium | Medium | Skip close-out for light plans (A3); Docs impact "None" allowed |
| ADR spam | Medium | Medium | Three-part test, default to writing nothing, a rejected alternative required, candidates capped |
| Planner grows past its budget | Medium | High | Template moved to `references/` (D12); size check in `validate` |
| Sweep deletes something still needed | High | Low | Per-file approval, only on explicit instruction, and plans are in git history if the plan was ever committed |
| New skills do not change agent behaviour | Medium | Medium | Evals written for later runs; behavioural claims marked unproven |
| Mermaid script or compatibility claims are wrong | Low | Medium | Test with real `mmdc` and GitHub before claiming; otherwise mark untested |
| Fresh-context delegation behaves differently per tool | Medium | Medium | Defaults documented with per-tool caveats; keep the setting as overlay text first |
| Research claims were partly second-hand | Low | Medium | The plan rests on repository evidence and the author's decisions; the peer facts are context only. Known caveats: the Reddit page text was never read; GSD's original repository is archived and a compromise claim is unverified; OpenSpec was read but never run |

## 13. Done criteria

- AC-01 to AC-09 satisfied with the recorded evidence.
- `python3 scripts/aibundle.py validate` and `python3 -m unittest discover -s tests`
  pass on each slice branch.
- Behaviour changes are described in `docs/REVIEW-LOG.md` or the PR, with untested
  behaviour called out.
- This plan has `Status: done` and its as-built section filled in at the end,
  following the process it defines.

## 14. Review checklist

- [x] Requirements and decisions are explicit
- [x] Non-goals are explicit
- [x] Existing conventions were checked
- [x] Alternatives were considered
- [x] Security and abuse implications were reviewed
- [x] Rollout and rollback are defined
- [x] Steps are ordered, with a tier and verification
- [ ] Acceptance scenarios agreed with the author (currently **proposed**)
- [x] Open questions answered (D12 to D15)
- [ ] Implementation authorized (not yet)

## 15. Docs impact

- `README.md`: new entities and packs; external skills section committed.
- `docs/workflow.md`: lifecycle (Status, close-out, sweep), isolation defaults,
  phase boundaries.
- `docs/REVIEW-LOG.md`: entry per slice.
- `docs/model-routing.md` / `catalog/skills/model-routing`: only if tier
  assignments change the table.
- ADR candidates: none expected; the decisions above are recorded in this plan.

## 16. As-built

Not started.

## 17. Handoff prompt for an implementation agent

```text
Implement slice <N> of docs/plans/workflow-memory-and-lifecycle.md. Do not start
until the author has agreed the acceptance scenarios (section 9) and authorized
implementation.

Constraints:
- One slice per branch and PR. Do not push, merge, or close issues.
- Edit only catalog/, packs/, routing/, scripts/, tests/, docs/, README.md. Never
  edit imports/.
- Catalog content stays generic: no host paths, project names, or vendor model IDs.
- Canonical frontmatter uses portable fields only; every new skill or agent needs
  metadata.routing-tier.
- Write the tests listed for the slice first and run them to see the expected
  failures before changing catalog content.
- Run `python3 scripts/aibundle.py validate` and
  `python3 -m unittest discover -s tests` before handing back.
- If reality differs from the plan, stop and update the plan or ask first.
- Describe behaviour changes in docs/REVIEW-LOG.md, and say what is untested.
```
