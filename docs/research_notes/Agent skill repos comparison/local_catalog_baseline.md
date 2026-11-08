# Local skill catalog baseline (research, plan, execute, validate, review; knowledge persistence; context isolation)

Scope: read-only audit of `/home/patex1987/development/movie-reservation-platform-lab/skill-bundle` at HEAD `ee356e1` on `main`. `git status` was clean when audited (see last section). All citations are repository-relative `file:line`. Paths with a leading `catalog/skills/` are abbreviated `S/` in a few tables only where noted. No web sources were used; every claim is from the repository itself.

## 1. What the catalog does today for the research -> plan -> execute -> validate -> review workflow

### Takeaway
The `core` pack ships one skill per phase (codebase-research, external-research, principal-engineer-planner, plan-execution, plan-validation, model-routing) plus two cheap helper agents; the `review` pack adds pr-walkthrough and four reviewer agents. Phases hand off through Markdown files under `docs/` (research, plans, validation), keep everything in one session by documented default, and treat the plan file as the shared state. Test-first execution against acceptance IDs agreed with the user is the distinctive feature.

### Cited Findings

Pack membership
- `core` pack = codebase-research, external-research, principal-engineer-planner, plan-execution, plan-validation, model-routing + agents scout, check-runner. — `packs/core.json:1-15`
- `review` pack = appsec-review, pr-walkthrough + agents security-practices, system-design-scalability, performance-scalability, readability-maintainability. — `packs/review.json:1-12`
- `programming-kb` (local vault retrieval, explicit-only) is its own pack. — `packs/knowledge-base.json:1-6`; `catalog/skills/programming-kb/SKILL.md:7-9`

Phase table (as the repo documents it) — `docs/workflow.md:9-16`
| Phase | Skill / agent | Writes (per doc) |
|---|---|---|
| Research | codebase-research, external-research | `docs/research/<task>-codebase.md`, `docs/research/<topic>-external.md` |
| Plan + annotate | principal-engineer-planner | `docs/plans/<feature>.md` |
| Implement | plan-execution | "code and tests; ticks steps in the plan" |
| Validate | plan-validation | "evidence in the plan or `docs/validation/<task>.md`" |
| Review | pr-walkthrough; four reviewer agents | "findings" |
| Helpers | scout, check-runner, model-routing | search results, check output, tier changes |

Per-skill inputs / outputs / paths

- **codebase-research** (tier balanced, effort medium: `catalog/skills/codebase-research/SKILL.md:6-7`)
  - Input: question, subsystem and exclusions, bounded by issue/request. — `:16`
  - Output: `docs/research/<task>-codebase.md` unless a destination is established. — `:26`
  - Report contents: question, scope, date, repo, branch and HEAD, uncommitted changes observed; behavior and call/data flow; invariants; test coverage and commands; findings with evidence; unknowns; "Implications for planning, with recommendations distinguished from current behavior". — `:28-36`
  - Handoff: summarize, link report, "Invite corrections through annotations without inventing a mandatory approval step"; "When planning follows, reread relevant source if HEAD or the working tree changed. Do not treat this report as an implementation plan". — `:40-42`
  - Read-only by default; may write the report only. — `:12`, `:22`
- **external-research** (balanced/medium: `catalog/skills/external-research/SKILL.md:6-7`)
  - Input: scoped question; optionally `programming-kb` (honours explicit-only policy and `PROGRAMMING_KB_DIR`). — `:18`
  - Output: `docs/research/<topic>-external.md`. — `:32`
  - Depth modes Focused / Deep / Dedicated deep-research service (with an honesty rule not to call a browse pass a deep-research run). — `:26-28`
  - Optional wiki feedback only when the user asks; staged proposal if vault is not writable. — `:38-40`; `catalog/skills/external-research/references/wiki-feedback.md:1-12`
- **principal-engineer-planner** (deep/high: `catalog/skills/principal-engineer-planner/SKILL.md:6-7`)
  - Two modes: plan authoring (default) and interactive plan review. — `:16-24`
  - Stays in planning mode; "Do not implement during this skill." — `:14`, `:42`
  - Inputs: reuses an existing codebase research report ("check its revision and relevant files against the current working tree"), invokes `codebase-research` / `external-research` if available, links rather than copies. — `:85`
  - Gate before finalizing: propose acceptance scenarios, consult user; "silence, elapsed time, and an agent-written status do not" count as agreement. — `:132`
  - Output: `docs/plans/<kebab-case-feature-name>.md` (outputs content in chat if editing is unavailable). — `:136-140`
  - Plan has 18 numbered sections (see section 5 below); ends with a "Handoff Prompt for Implementation Agent". — `:144-300`
  - Hand-off rule: "Record implementation authorization separately from test agreement... Once execution is authorized, hand off to `plan-execution` if available. Final `plan-validation` checks completion against the agreed criteria." — `:321`
  - Annotation cycle stays in authoring mode ("do not treat an annotation request as permission to code"; "Keep the plan a current proposal rather than an accumulation of contradictory drafts"). — `:26-27`, `:317`
  - Interactive review writes `docs/plans/<plan-name>-review.md`, linked from the plan by `Review record:`. — `catalog/skills/principal-engineer-planner/references/plan-review.md:168-170`; template line in plan `SKILL.md:151`
- **plan-execution** (balanced/medium: `catalog/skills/plan-execution/SKILL.md:6-7`)
  - Inputs: repo instructions, issue, plan, accepted annotations, research, working tree; authorization "in the conversation or task handoff. A file labeled approved is not sufficient authority by itself." — `:16`
  - Precondition: plan must contain acceptance scenarios agreed with the user; if absent, propose before production changes. — `:18`
  - Vertical-slice loop: define evidence first, observe baseline (must fail for the intended reason), implement, check and refine, record progress. — `:24-30`
  - "Record progress. Link test IDs, changed files, commands, and results in the plan or its execution log." (no path is defined for an "execution log"). — `:30`
  - Delegation: start from each step's suggested tier, apply `model-routing`; "Record tier, effort, any escalation and its trigger, and the verification result beside the slice's evidence." — `:36-38`
  - Ends: "Run required repository checks after the slices, then hand off the diff and evidence for final validation. Report completion separately from merge, publication, or deployment authority." — `:42`
- **plan-validation** (balanced/high: `catalog/skills/plan-validation/SKILL.md:6-7`)
  - Inputs: instructions, issue, agreed plan and scenarios, diff, execution results; "do not treat unchecked annotations or an agent-written approval label as acceptance". — `:16`
  - Builds per-scenario evidence map; separates execution-reported test-first evidence from validator-verified evidence ("if the baseline was not captured, do not invent it"). — `:18`
  - Output: "Write results into the established plan/log or `docs/validation/<task>.md`". — `:30`
  - Verdict vocabulary: verified / incomplete / blocked. — `:37`
  - Authorizes nothing: "Validation itself does not authorize pushing, merging, or deploying." — `:39`
- **model-routing** (balanced/low: `catalog/skills/model-routing/SKILL.md:6-7`): three tiers fast/balanced/deep (`:28-32`); cascade only where checking is cheap (`:45-52`); escalate on evidence at most once per unit (`:54-69`); de-escalate after a deep plan defines slices (`:71-78`); record routing decisions "In the plan or execution log" (`:96-102`); explicit user/repo choice wins (`:24`).
- **pr-walkthrough** (deep/medium: `catalog/skills/pr-walkthrough/SKILL.md:6-7`)
  - Interactive, read-only, one `Topic M/N` per message; pins base/head SHAs. — `:13-18`, `:32-46`, `:50-66`
  - Writes a walkthrough record at `docs/reviews/<target>-walkthrough.md` (target = `pr-<number>`, branch, or `working-tree`), described as "a working file for the reviewer, not part of the change", untracked, user decides whether to commit/share/delete. — `catalog/skills/pr-walkthrough/references/record.md:3-15`
  - Reads "linked issue or plan if referenced". — `SKILL.md:70`
  - Close: summary of findings, "PR description claims that are wrong or missing"; offers fixes, specialist agents, posting comments; posts nothing without approved exact text. — `:121-132`; `catalog/skills/pr-walkthrough/references/findings.md:88-98`
- **Reviewer agents** (read the repo's agent instructions, review a diff/module/design, return findings; no file-write instruction found): e.g. `catalog/agents/security-practices.md:1-30` (roles: change reviewer, unit reviewer, verifier), `catalog/agents/system-design-scalability.md:1-20`, `catalog/agents/readability-maintainability.md:1-20`. Tiers: security-practices deep/high, system-design-scalability deep/high, readability-maintainability balanced/medium.
- **appsec-review** has its own artifacts for full audits: `architecture.md`, a coverage ledger, per-candidate verification records, written to a new directory "outside the repository" and not committed. — `catalog/skills/appsec-review/references/full-audit.md:12`, `:14`, `:68-74`

Overall flow and defaults as documented in `docs/workflow.md`
- Core rule: "no code until you have reviewed and approved a written plan." — `docs/workflow.md:4-5`
- Setup: open session from the repository; create the issue and branch first. — `:23-24`
- Annotation cycle: user writes notes directly into `docs/plans/<feature>.md`, then "I added notes to the plan. Address all of them and update the document. Don't implement yet." — `:64-74`; repeat typically 1-6 rounds — `:75`
- Optional granular todo checklist step. — `:76-79`
- Guided review alternative writes `docs/plans/<feature>-review.md`; "'continue the plan review' resumes in a new session". — `:80-90`
- "Steer through the document, not through chat. The plan is the shared state that survives context compaction and goes into the PR." — `:92-93`
- Implement prompt: "Mark each step done in the plan as you go." That message "is the authorization". — `:99-105`
- "Revert instead of patching a wrong direction... fix the plan, and repeat step 11." — `:109-111`
- Validate: "Use plan-validation against the plan." — `:115-120`
- Review: `pr-walkthrough` or the review agents (run "from inside the walkthrough" or standalone). — `:121-130`
- "Ship small. Commit the research, the plan, and the code in one small PR, so the reasoning stays with the change." — `:131-132`
- Differences from the Boris Tane article: no built-in plan mode (docs/plans instead), tests come from the plan, independent validation and review. — `:139-146`
- The workflow is described as manual prompt sequencing ("Prompts below are examples"): the user names each skill to trigger it. — `:18-19`

### Inferences
- The catalog is a set of loosely coupled skills sequenced by the user's prompts and by each skill's closing "hand off to X if available" sentence, not a pipeline with a state machine; the only durable state is Markdown files.
- Directory names (`docs/research`, `docs/plans`, `docs/validation`, `docs/reviews`) are hard-coded in skill text (a grep of catalog for these strings finds them in external-research, planner + plan-review, plan-validation, pr-walkthrough record, codebase-research), so changing the layout per repository today relies on the "Respect an established destination" clauses (`codebase-research/SKILL.md:26`, `plan-review.md:169`, `record.md:9`) or overlays.
- Execution-time evidence has no defined file: plan-execution says "the plan or its execution log" (`plan-execution/SKILL.md:30`) and plan-validation says "established plan/log or `docs/validation/<task>.md`" (`plan-validation/SKILL.md:30`).

### Gaps
- Behavior of these skills in real sessions is stated as not evaluated per skill. — `README.md:173-174`. Only principal-engineer-planner (interactive review) and pr-walkthrough carry eval fixtures (`catalog/skills/principal-engineer-planner/evals/evals.json:1-12`, `catalog/skills/pr-walkthrough/evals/evals.json`); plan-execution, plan-validation, codebase-research have no evals directory.

---

## 2. Persistence of knowledge AFTER implementation

### Takeaway
No skill writes a record of what was actually built, the resulting architecture, or ADR-like decisions after implementation, and none updates a living architecture or spec document. plan-execution and plan-validation leave only per-task evidence (progress checkboxes, test/command results, an acceptance matrix, a verdict). The plan stays in `docs/plans/` unchanged in location, with no status field in its template, no archival step, and no "as built" reconciliation section. The closest mechanisms are (a) the plan's `Decisions` list and review record, which are pre-implementation, (b) optional KB wiki feedback in external-research, and (c) the handoff line "Update docs described in the plan", which depends on the plan having described docs.

### Cited Findings

What plan-execution persists
- Progress ticks and evidence "in the plan or its execution log": test IDs, changed files, commands, results; routing tier/effort/escalation per delegated unit. — `catalog/skills/plan-execution/SKILL.md:30`, `:38`
- Report completion "separately from merge, publication, or deployment authority"; no instruction to write an as-built summary or update any architecture/docs. — `:42`
- If implementation diverges: "stop and update the plan or ask for approval before changing scope" (planner handoff prompt). — `catalog/skills/principal-engineer-planner/SKILL.md:293`; execution says "update the plan and seek the missing decision". — `plan-execution/SKILL.md:42`. This updates the plan for scope change, not as a post-hoc as-built record.

What plan-validation persists
- Written into plan/log or `docs/validation/<task>.md`: revision reviewed, acceptance matrix (scenario ID, evidence, result, remaining gap), check results with pre-existing vs introduced failures, findings with severity, unverified rollout/runtime/performance assumptions, verdict verified/incomplete/blocked. — `catalog/skills/plan-validation/SKILL.md:30-37`
- "Update task completion accurately and report material limitations in the final handoff." — `:39`
- No step to promote validated outcomes into architecture docs, decision records, or a changelog.

Where the plan goes after completion
- The plan template has no `Status:` field. Section list: Summary, Goals, Non-goals, Current State, Requirements and Assumptions (Confirmed Requirements / Decisions / Assumptions / Open Questions), Proposed Design, Alternatives, API, Data, Security, Performance, Implementation Steps, Testing Strategy, Rollout, Risks, Done Criteria, Review Checklist, Handoff Prompt. — `catalog/skills/principal-engineer-planner/SKILL.md:144-299`
  - Only state-like fields: `Test agreement: proposed / agreed / changes requested` (`:243`), `Review record:` link (`:151`), `- [ ]` checklist items in section 17 (`:263-274`), and "Record progress as a checklist" for steps (`:219`).
- No instruction anywhere in the plan, execution, or validation skills to archive, move, rename, or mark a plan "implemented". Plans stay at `docs/plans/<feature>.md`, and the workflow says the plan "goes into the PR" and to commit "the research, the plan, and the code in one small PR, so the reasoning stays with the change". — `docs/workflow.md:92-93`, `:131-132`
- The repo's own hand-written plan does use a free-form status line: "Status: implemented (authorized in the request... ). Acceptance checks AC1-AC6 pass; see `docs/REVIEW-LOG.md`." — `docs/plans/typescript-naming-cohesion-validation.md:3`. This is the maintainer's convention, not specified in the planner template. The plan's section numbering also differs from the skill template (its sections are Goal, Evidence checked, Alternatives, Changes, Acceptance checks, Steps, Risks: `docs/plans/typescript-naming-cohesion-validation.md:6,25,55,63,94,105,117`).
- Post-implementation record for that work lives in `docs/REVIEW-LOG.md` ("Follow-up: naming, module cohesion, and schema-first validation", "Plan: `docs/plans/...`", with a "Not done" list: evals not run, not installed anywhere). — `docs/REVIEW-LOG.md:366-378` (approximate range printed by `sed -n 360,380p`). The bundle's own contributing rule: "Describe behaviour changes in `docs/REVIEW-LOG.md` or the PR." — `AGENTS.md` (skill-bundle) "Before handing back" section. This is a repository convention for this catalog, not a skill behaviour.

Decisions (ADR-like) during planning, not after
- Plan carries a `### Decisions` list: "`<decision> — Decision (user, <date or Q-ID>)`". — `catalog/skills/principal-engineer-planner/SKILL.md:171-173`; the interactive review keeps it linked to question IDs. — `plan-review.md:141-142`
- Review record keeps `## Decisions` with Decision (user), Rationale, Recommendation given, Plan sections updated, Date; plus Deferred, Unresolved points, Queue changes. — `plan-review.md:175-216`
- Review record status flips `in progress | complete`. — `plan-review.md:180`, `:226`. This is the only "complete" status in the planning artifacts, and it applies to the review, not the implementation.
- Statements are tagged Decision (user, Q-xx) / Recommendation / Assumption / Evidence. — `plan-review.md:136-141`
- These decisions stay inside the plan/review files; no skill promotes them to a repo-level ADR directory or architecture doc (grep of the catalog for ADR/architecture.md/"living"/"post-implementation"/"lessons"/"retro" found only appsec-review's per-audit `architecture.md`, a threat-model synthesis kept outside the repo, `catalog/skills/appsec-review/references/full-audit.md:68-74`).

Other persistence mechanisms
- Handoff prompt line: "Update docs described in the plan." — `catalog/skills/principal-engineer-planner/SKILL.md:291`. The plan template has no section that lists docs to update (the template sections at `:144-299` contain no documentation/docs-impact section; section 8 covers API/interface changes only, `:201-203`), so this line only fires if the planner wrote such text elsewhere.
- Planner "Done Criteria" section is a bulleted list with no template content. — `:257-259`
- walkthrough record "is a working file for the reviewer, not part of the change"; user decides what to do with it. — `catalog/skills/pr-walkthrough/references/record.md:3-5`, `:14-15`
- Knowledge-base feedback: external-research only when asked; "Separate reusable knowledge from facts true only of the researched codebase. Keep repository-specific behavior in that repository's docs." — `catalog/skills/external-research/references/wiki-feedback.md:5`; "Research alone does not request KB edits." — `external-research/SKILL.md:40`. It covers external research findings, not implementation outcomes.
- `programming-kb` can recommend KB updates when stale, but writes only on request: "preserve raw sources, update generated pages surgically, refresh `index.md`". — `catalog/skills/programming-kb/SKILL.md:84`, `:99-103`
- Model-routing "evidence loop" is explicitly future: records of tier/escalation per unit should be reviewed "after a few weeks"; a deterministic recorder (a SubagentStop hook writing JSONL) "is not implemented here". — `docs/model-routing.md:74-81`
- Repository-level always-on knowledge goes in `.ai/project-guidance.md` (hand-written) and `.ai/overlays/<skill>.md` (paths, commands, decisions): "It records this repository's paths, commands, and decisions". — `README.md:60-62`; `scripts/render.py:296-300`; `scripts/render.py:481-484`. These are human-maintained; no skill updates them.

### Inferences
- There is a clear hole between plan-validation (verdict, per task) and any durable, repo-level "current state of the system" artifact. After a PR merges, the knowledge lives in code, the plan file (whose "Current State" and "Proposed Design" sections describe the pre-change world and intent), research reports (dated snapshots tied to a HEAD), and optional validation/review files.
- Because plans and research are snapshots tied to a revision (`codebase-research/SKILL.md:30`), nothing marks them stale after the code changes. Later sessions reading `docs/plans/` cannot tell implemented from abandoned from proposed, except by the ad-hoc "Status:" line the maintainer wrote by hand.
- Overlays and project-guidance are the existing sink for "durable repository decisions and conventions", but nothing in the workflow tells an agent to propose edits to them.

### Gaps
- No skill defines an "as-built" or "delta against plan" section, ADR format, spec/living architecture update step, or plan lifecycle status. This absence is based on reading the seven requested skills plus a catalog-wide grep; I did not read every reference of every unrelated skill (e.g. nestjs, fastapi) line by line.
- Did not check whether consuming repositories (e.g. `examples/movie-reservation-service`) add overlays that cover post-implementation docs: the example overlays only cover clean-architecture, nestjs, typescript, vitest-testing (`examples/movie-reservation-service/.ai/overlays/`).

---

## 3. Context isolation: subagents, fresh context, user-selectable switches, per-repo configuration

### Takeaway
The workflow default is explicitly one shared session for research, planning, and implementation. Subagent use is advisory and narrow: `scout` and `check-runner` as cheap context absorbers, independent validation of risky slices, and fresh verifiers in appsec-review. No research or planning phase is specified to run in a fresh-context subagent, and there is no inline-vs-delegated switch. `bundle.json` has a closed schema (unknown top-level keys are an error at install), and no existing key governs workflow behavior; the closest per-repo levers are `invocation` (auto/explicit), `routing.*`, `local`, per-skill overlays, and `project-guidance.md`.

### Cited Findings

Where the docs say to keep context shared
- "Keep research, planning, and implementation in one session, so that the context built during research carries into the later phases." — `docs/workflow.md:26-28`
- "The plan is the shared state that survives context compaction." — `docs/workflow.md:92-93`
- Counter-signal: interactive plan review and pr-walkthrough both persist a record "so another session can resume exactly" / "survives context compaction and can resume in another session". — `plan-review.md:168`; `catalog/skills/pr-walkthrough/references/record.md:3-5`. `docs/workflow.md:88-90` ("'continue the plan review' resumes in a new session").

Where skills do instruct delegation or independence
- Helper agents for context hygiene: "delegate broad searches to `scout` and noisy test or lint runs to `check-runner`, both `fast` agents, to keep the expensive session's context clean." — `docs/workflow.md:134-135`
- scout: read-only explorer, returns "Answer / Evidence / Not found", under about 40 lines; description "so the lead agent's context stays small". — `catalog/agents/scout.md:3`, `:15-23`
- check-runner: runs only named commands, reports pass/fail/error/not run with at most ~20 lines of failure output; may not edit files, install deps, or contact external services. — `catalog/agents/check-runner.md:3`, `:9-24`
- model-routing "Delegate deliberately": delegate when a unit is "independent, has a clear output contract, and is large or noisy enough to be worth isolating"; "A good brief states the goal, the inputs or paths, the constraints and non-goals, the expected output format, and how the result will be checked"; "Prefer parallel `fast` workers for independent read-only fan-out, and avoid parallel writers on the same files." — `catalog/skills/model-routing/SKILL.md:80-90`
- "For risky units, validate with a different agent or context from the one that did the work. Use a validator at least as capable as the executor. Validation is independent evidence, not a second opinion from the same context." — `catalog/skills/model-routing/SKILL.md:92-94`
- plan-validation: "Validate risky slices in a context independent of the one that implemented them, at a tier at least as capable as the executor's; record which slices were validated that way." — `catalog/skills/plan-validation/SKILL.md:20`. This is the only workflow-skill sentence requiring fresh context, and it is scoped to risky slices (not all validation).
- plan-execution delegation is conditional: "When you delegate slices or checks to other agents..." — `catalog/skills/plan-execution/SKILL.md:38`. It never instructs spawning; it assumes delegation may occur.
- pr-walkthrough: "For a large change, delegate file listing and noisy searches to a cheap `scout` agent if one is available"; offers to delegate topics to security/design/performance/maintainability agents. — `catalog/skills/pr-walkthrough/SKILL.md:73-75`, `:136-141`
- appsec-review is the only skill with a systematic fresh-context pattern: independent falsification "the `security-practices` agent in verifier role, or a fresh subagent that gets only the claim and the pointers" (`catalog/skills/appsec-review/SKILL.md:106-109`); orchestration table with parallel reviewers, fresh verifier per surviving candidate, lead deduplicates (`:135-142`); full audit uses coverage critic with "no findings" and fresh verifiers that did not produce the candidate (`catalog/skills/appsec-review/references/full-audit.md:156-168`); agent budget and output directory agreed first (`:8-14`).
- principal-engineer-planner, codebase-research, external-research: no occurrence of subagent/delegate/fork/fresh in their SKILL.md or references (grep across `catalog/skills/{principal-engineer-planner,plan-execution,plan-validation,codebase-research,external-research,model-routing,pr-walkthrough}` for `subagent|delegate|fork|fresh|independent context` returned hits only in plan-execution:36-38, plan-validation:20, model-routing, pr-walkthrough:73-75,138).

User-selectable switches (existing)
- None named for inline vs delegated execution. No sentence in the audited skills lets the user choose "run this phase in a subagent".
- `invocation: auto | explicit` per skill (default auto): set in skill `metadata.invocation` or overridden in `bundle.json` `invocation`; renders to Claude/Cursor `disable-model-invocation`, Codex `allow_implicit_invocation: false`, or an "Explicit only" note. — `scripts/render.py:222-224`, `:321-322`, `:341-353`, `:292-295`; `README.md:75`. Used only for `programming-kb`: `catalog/skills/programming-kb/SKILL.md:9`, `examples/movie-reservation-service/.ai/bundle.json:8`.
- `metadata.context: fork` makes a skill run in its own subagent with its tier's model and effort: `scripts/render.py:230` (`'fork': meta.get('context') == 'fork'`), `:323-328`; `catalog/skills/model-routing/references/tool-mechanics.md:15-18` (Claude Code: "That is the only way a skill gets its own model without changing the main session"), `:82-83`. No catalog skill sets `context: fork` today (grep found only the tool-mechanics mentions). `context` is an allowed metadata key. — `scripts/aibundle.py:30`
- Routing: `routing.apply.skills|agents: advisory | enforce` (defaults advisory/enforce) so agents get pinned model/effort and skills stay advisory; `routing.models`, `routing.overrides`. — `scripts/render.py:180-193`; `docs/model-routing.md:29-48`; `README.md:96-104`
- Fork-mode note: the doc-level reason for keeping inline skills advisory is that in Claude Code a skill's `model` changes the main session for the current turn. — `docs/model-routing.md:29-48`

bundle.json schema and where a per-repo "workflow options" setting could fit
- Install-time validation (`aibundle.py read_manifest`) allows only top-level keys `schema_version, packs, local, targets, routing, invocation` plus `skills|agents|rules` (each `{add, remove}`); any other key raises `BundleError(... unknown keys ...)`; schema_version must be 2; `routing` and `invocation` must be objects (contents not validated at install). — `scripts/aibundle.py:292-309` (the allowed set is at line 296-298 in the file, the dict checks at ~`:313-318`)
- Render-time (`render.py load_config`) reads only `targets`, `routing.models`, `routing.apply`, `routing.overrides`, `invocation`; it does not reject other top-level keys, but validates `routing.apply` values and `routing.overrides`/`invocation` names against known entities. — `scripts/render.py:169-194`, `:262-270`
- Example manifest: `examples/movie-reservation-service/.ai/bundle.json:1-15` (packs core, review, knowledge-base, teaching, nestjs; `invocation: {programming-kb: explicit}`; routing apply/models/overrides).
- Per-skill repository facts are carried today by overlays: `.ai/overlays/<skill>.md`; rendered skills get a "read `.ai/overlays/<name>.md` before applying" note that "takes precedence". — `README.md:60-62`; `scripts/render.py:226`, `:296-300`; unknown-overlay names are an error. — `scripts/render.py:271-274`
- Always-on repo context: `.ai/project-guidance.md` is prepended to the generated index (`CLAUDE.md`/`AGENTS.md`/`GEMINI.md`). — `scripts/render.py:478-484`; `README.md:27`, `:34`
- Portability rule: catalog content must be generic; repository paths, project names, model IDs belong in overlays or `bundle.json`; enforced by `catalog/lint.json`. — `AGENTS.md` (skill-bundle) "Working here"; `README.md:134-136`
- Metadata keys allowed in catalog frontmatter: `routing-tier, routing-effort, invocation, context, agent, tags, max-turns, skills`; unknown keys fail validate. — `scripts/aibundle.py:30`, `:221-222`; tool-specific fields must be generated. — skill-bundle `AGENTS.md`

### Inferences
- A per-repo "workflow options" setting (e.g. `phase isolation: inline | delegated`, `record post-implementation docs: yes/no`, doc directory overrides) has three plausible homes, in increasing cost:
  1. Overlay for the relevant skill (`.ai/overlays/principal-engineer-planner.md`, `plan-execution.md`, ...): no code change; works because overlays are read first and "take precedence"; but each skill's text must tolerate "unless the overlay says otherwise", and settings are prose, not validated, and spread over several files.
  2. `project-guidance.md`: no code change; one place, always loaded, but also prose and unvalidated.
  3. New structured key in `bundle.json` (e.g. `workflow`): requires adding it to the allowed set at `aibundle.py:296-298` and a type check beside `:313-318`; `render.py` would have to read it in `load_config` (`:169-194`) and emit it into the generated index (`render_index`, `:478-`) because skills have no other channel to see `bundle.json`; README schema docs and `tests/` would need updating. This gives validation and a single place, and it is consistent with how `invocation` and `routing` already work (rendered into every tool's guidance).
- The cleanest existing primitive for "delegated vs inline" per skill is `metadata.context: fork` (static, catalog-level), but it is not repository-selectable and the renderer reads it from skill metadata, not `bundle.json`; `routing.overrides` and `invocation` are the only per-repo, per-skill overrides and neither covers `context`.
- Tool capabilities (section 4) mean a "delegated" mode is only mechanically enforceable on Claude Code (skill `context: fork` or agent spawn) and, for agents, on Codex/Cursor/Gemini; skills there run inline.

### Gaps
- Not verified that `bundle.json` unknown keys are checked anywhere beyond `read_manifest`; the tests directory was not read (e.g. whether a test pins the key set).
- Did not check `scripts/aibundle.py cmd_init` / schema docs beyond README to see whether schema documentation exists outside `README.md:27` and `docs/`.

---

## 4. Tools that render the catalog and their subagent primitives

### Takeaway
Four tools are rendered (Claude Code, Codex, Cursor, Gemini CLI) plus `AGENTS.md`. All four have subagent definitions in files; only Claude Code is documented with a skill-level fork (`context: fork`) and a per-spawn model override; Codex pins model in agent files so spawn-time escalation does not work; Cursor has no documented effort field; Gemini subagent field names are unverified.

### Cited Findings
- Targets and outputs: index at `.claude/CLAUDE.md` (Claude), `AGENTS.md` (Codex, Cursor), `GEMINI.md` -> `@./AGENTS.md`; skills to `.claude/skills/` or `.agents/skills/` (+ `agents/openai.yaml` for Codex); agents to `.claude/agents/*.md`, `.codex/agents/*.toml`, `.cursor/agents/*.md`, `.gemini/agents/*.md`. — `README.md:67-76` (table at `:69-75`); example targets list `examples/movie-reservation-service/.ai/bundle.json:9`
- Verification date for field names: 2026-10-23 (tool-mechanics), 2026-10-24 for alternatives survey. — `catalog/skills/model-routing/references/tool-mechanics.md:3`; `README.md` "Alternatives to evaluate"
- Claude Code (`tool-mechanics.md:7-37`):
  - Subagents in `.claude/agents/*.md`; `model` = haiku/sonnet/opus/ID/inherit; `effort` low..max; precedence per-invocation model, agent `model`, `CLAUDE_CODE_SUBAGENT_MODEL`, session model. — `:9-14`
  - Skills: `effort` applies while active, `model` for the current turn only; `context: fork` runs the skill in a subagent. — `:15-18`
  - Subagent `skills` field preloads full skill content at startup; read-only agents do not get the `Skill` tool, so `render.py` emits `skills` from `metadata.skills` or a read-first note for explicit-only skills. — `:19-24`
  - Dynamic adjustment: the spawn call can pass `model` (and `effort` where exposed) overriding the agent file for one invocation. — `:25-28`
  - Session: `/model`, `/effort`, `opusplan` alias (Opus in plan mode, Sonnet for execution). — `:40-44`
- Codex (`:39-53`): agents in `.codex/agents/*.toml` with `model`, `model_reasoning_effort`; file values beat spawn-time values, so "A model pinned in an agent file therefore cannot be escalated at spawn time"; subagents inherit parent sandbox and approvals, `sandbox_mode` in the agent file does not make it read-only; skills in `.agents/skills/`; `allow_implicit_invocation: false` for explicit-only.
- Cursor (`:55-62`): `.cursor/agents/*.md` with `model` inherit/ID and `readonly: true` blocking edits; also reads `.claude/agents/` and `.codex/agents/` (`.cursor/` wins); skills in `.agents/skills/` and `.cursor/skills/` plus compatibility paths; "No documented reasoning-effort field."
- Gemini CLI (`:63-71`): `.gemini/agents/*.md`, `model` defaults to inherit, restrict `tools` because subagents "may run tools without confirmation"; skills in `.gemini/skills/` or `.agents/skills/`; context file `GEMINI.md`; "Field names come from launch material and secondary guides. Verify them against <https://geminicli.com/docs/> before depending on them." — `:70-71`
- Renderer behavior: tier -> model/effort via `routing/tiers.json`; unmapped tiers render as `inherit`; only Claude has default model mappings (haiku/sonnet/opus) and efforts list; Codex has an empty `models` map and efforts list; Cursor and Gemini have empty efforts. — `catalog/skills/model-routing/references/tool-mechanics.md:73-84`; `routing/tiers.json:18-36`; `docs/model-routing.md:58-64`
- Agents carry an `access` level (`read-only` for scout, `execute` for check-runner and reviewers) that the renderer maps to tool fields (tools, readonly); Codex cannot enforce read-only per agent. — `catalog/agents/scout.md:4`, `catalog/agents/check-runner.md:4`; `tool-mechanics.md:46-48`; `docs/REVIEW-LOG.md` cycle-1 finding 1.7.

### Inferences
- For fresh-context delegation, the portable primitive across all four tools is the rendered agent file (named subagent). Skills that must run in fresh context would need `context: fork`, which the repo documents only for Claude Code; the other tools' skill-fork equivalents are not documented here.
- Escalation-at-spawn works on Claude Code; on Codex the pinned model blocks it unless the tier is left unmapped (`tool-mechanics.md:41-44`).

### Gaps
- Vendor facts are second-hand (from the repo's notes, checked 2026-10-23); I did not re-verify against vendor docs. Gemini subagent fields are explicitly unverified by the repo.
- No data on whether a skill can invoke a named subagent by name in Codex/Cursor/Gemini; the repo does not say.

---

## 5. Document-format differences that matter

### Takeaway
Plan, review record, walkthrough record, validation report, and research report each have a different structure; only the plan and the two interactive records are given templates. Validation has a content list but no template or file template; codebase and external research have content lists only. Acceptance IDs (`AC-nn`) link plan, execution, and validation.

### Cited Findings

Plan template (planner `SKILL.md:144-300`)
- 18 sections in this order: 1 Summary (with `Review record:` line), 2 Goals, 3 Non-goals, 4 Current State, 5 Requirements and Assumptions (Confirmed Requirements; Decisions; Assumptions; Open Questions), 6 Proposed Design, 7 Alternatives Considered (Pros/Cons/Decision), 8 API/Interface Changes, 9 Data Model/Persistence, 10 Security/Privacy/Abuse, 11 Performance/Scalability/Reliability, 12 Implementation Steps, 13 Testing Strategy, 14 Rollout/Migration, 15 Risks and Mitigations (table), 16 Done Criteria, 17 Review Checklist (12 checkboxes), 18 Handoff Prompt for Implementation Agent. — `:144-299`
- Implementation step fields: Change, Files/modules likely affected, Notes, Verification, Suggested tier (fast/balanced/deep with reason). Steps tracked as a checklist; per slice: tests and baseline before production change. — `:219-233`
- Planning depth classes: Light / Standard / Design review plan. — `:67-71`. The depth is not recorded as a field in the template.
- Acceptance-test table in section 13: columns `ID | Setup / action | Observable expected result | Level / file | Command and directory | Pre-change expectation`; ID like `AC-01`; "Fails for missing behavior, or passes for characterization" as pre-change expectation example. — `:239-241`; scenario content requirements at `:134`
- Test agreement line: `proposed / agreed / changes requested`; "Record the user's actual agreement or link to the relevant issue discussion; never invent it." — `:243`
- "Material acceptance changes during execution require renewed agreement; extra tests that preserve the agreed behavior do not." — `:245`
- Decision provenance markers in the plan: `Decision (user, <date or Q-ID>)` (`:173`); in review mode also Recommendation / Assumption / Evidence. — `plan-review.md:136-141`
- Deviation from the template exists in the repo's own plan (different headings, `Status:` and `Planning depth:` lines, a simpler AC table `ID | Check`): `docs/plans/typescript-naming-cohesion-validation.md:3-4`, `:94-103`. Likewise the eval fixture plan uses AC rows with fewer columns: `catalog/skills/principal-engineer-planner/evals/files/docs/plans/order-export.md:73`. This shows templates are loosely followed or loosely applied.

Review record format (`plan-review.md:175-216`)
- Header fields: Plan link, Research links, Review status (in progress | complete), Revision reviewed, Current position (`Question M/N, Q-07 (<topic>)`), Test agreement, Implementation authorization (`not given | given (<scope>, <date>, <quote or link>)`).
- Sections: Queue table (`# | ID | Topic | Question | Status | Depends on`; statuses pending/discussing/decided/deferred, `:101-108`), Decisions (per Q-ID: Decision (user), Rationale, Recommendation given, Plan sections updated, Date), Deferred, Unresolved points and assumptions, Queue changes.
- Question message format: `Question M/N — <topic> (Q-07)` with Context / Decision / Options and tradeoffs / Recommendation. — `:67-76`
- Closing summary: user's decisions vs accepted recommendations; deferred items; open assumptions; test agreement; implementation authorization; readiness **ready / ready with named risks / not ready**; next prompt. — `:220-236`

Validation report (`plan-validation/SKILL.md:28-37`): a bullet content list only, no template: revision reviewed with working-tree state; acceptance matrix (scenario ID, evidence, result, remaining gap); required checks and pre-existing vs introduced failures; findings with severity, file/symbol evidence, user impact, next action; unverified rollout/runtime/performance assumptions; verdict verified / incomplete / blocked. Results are pass / fail / blocked / not run. — `:26`, `:30-37`. Verdict vocabulary differs from the review record's readiness vocabulary and from pr-walkthrough finding tags.

Execution record: no format; "Link test IDs, changed files, commands, and results in the plan or its execution log" (`plan-execution/SKILL.md:30`); routing record fields tier, effort, model used, escalation trigger, verification result (`model-routing/SKILL.md:96-102`).

Research reports
- Codebase: content list at `codebase-research/SKILL.md:28-36`; observed facts vs inferences/hypotheses separated (`:20`); records executed commands (`:20`).
- External: content list at `external-research/SKILL.md:34-36`; distinguishes checked citations from leads; KB paths with access dates.

Walkthrough record (`pr-walkthrough/references/record.md:22-66`): header (Target, Mode, Pinned base/Head at start, Started, Position, Status), Topics table (# | Topic | Files | Status), Findings (Open / Follow-up / Questions / Dropped / Done), Topic changes, Not verified. Finding tags and routes are defined in `findings.md`.

### Inferences
- Common keys across artifacts: stable IDs (AC-nn, Q-nn), `Revision reviewed`-style pinning, explicit status vocabularies (differing between artifacts), and explicit "authorization" separate from "agreement".
- There is no cross-artifact link convention except: plan -> review record (`Review record:`), review record -> plan and research, planner -> research reports ("Link reports rather than copying", `SKILL.md:85`); validation -> plan by scenario ID; no link from plan to validation report is specified.

### Gaps
- No template exists for the post-implementation/as-built content (section 2 above), nor for plan lifecycle state.

---

## 6. The user's uncommitted work

### Takeaway
Not relevant at audit time: the working tree was clean, and the items named in the task are already committed.

### Cited Findings
- `git status` at audit time: "On branch main... nothing to commit, working tree clean". `docs/plans/typescript-naming-cohesion-validation.md` is tracked (added in commit `deeb657`, "Add TypeScript naming, cohesion, and schema-first validation guidance"); the new typescript references are in that and the later `ee356e1` (rust-style) commits. `research_notes/Agent skill repos comparison/` was an empty directory (created Nov 7) when audited; this file is the first content in it.
- The only relevance of `docs/plans/` is as a worked example of how plans are used after implementation (hand-written `Status: implemented` line and a pointer to `docs/REVIEW-LOG.md`): `docs/plans/typescript-naming-cohesion-validation.md:3`.

### Inferences
- The task description's "uncommitted work" appears to refer to material that was committed before this audit, or the git state changed between task creation and execution.

### Gaps
- Did not inspect other repos in the parent workspace.

---

## Citation caveats
- Line numbers for `docs/model-routing.md` and `README.md` come from per-file `grep -n`; a few ranges for `scripts/aibundle.py:292-318` and `docs/REVIEW-LOG.md:360-378` are approximate to within a few lines because they were read via `sed` windows. File and function names are exact.
- Where a statement says "grep found no occurrence", the grep covered `catalog/skills/{principal-engineer-planner,plan-execution,plan-validation,codebase-research,external-research,model-routing,pr-walkthrough,programming-kb,appsec-review}/SKILL.md`, all `catalog/skills/*/references/*.md`, and `catalog/agents/*.md`, excluding evals.
