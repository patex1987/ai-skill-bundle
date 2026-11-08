# ADR practice, ADR agent skills, and Mermaid guidance for AI coding agents (as of 2026-11-07)

Research notes for designing (a) an ADR skill and (b) a Mermaid/diagramming skill in the skill-bundle catalog. Web search/fetch was rate-limited partway through; the remaining facts were pulled from GitHub (via `gh api`) and npm registry. Items I could not verify are in the Gaps sections.

---

## 1. ADR formats, location/numbering, lifecycle, immutability

### Takeaway
Three formats cover almost everything: Nygard (Title/Status/Context/Decision/Consequences), MADR 4.0.0 (adds options, drivers, confirmation, with full/minimal x annotated/bare variants), and Y-statements (single-sentence). Convention is one markdown file per decision in `docs/adr/` or `docs/decisions/`, `NNNN-slug.md`, with a status field; "immutable, supersede don't edit" is the stated ideal but the ADR community itself says editing with dated updates works better in practice.

### Cited Findings
- Nygard's 2011 post is the origin; an ADR has title, status, context, decision, consequences. Nygard template text: Status ("proposed, accepted, rejected, deprecated, superseded, etc."), Context ("What is the issue that we're seeing that is motivating this decision or change?"), Decision ("What is the change that we're proposing and/or doing?"), Consequences ("What becomes easier or more difficult to do because of this change?"). — [adr.github.io templates post](https://github.com/adr/adr.github.io/blob/main/_posts/2024-10-25-adr-templates.md); [Nygard template rendering](https://github.com/joelparkerhenderson/architecture-decision-record/blob/main/locales/en-001/templates/decision-record-template-by-michael-nygard/index.md); original: [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html) (could not re-fetch the original page itself; relying on the two secondary renderings above).
- MADR current version is 4.0.0, released 2024-09-17 (previous 3.0.0 in 2022-10-09). Repo `adr/madr` ~2.6k stars, last push 2026-11-02. — [MADR releases](https://github.com/adr/madr/releases), [adr.github.io/madr](https://adr.github.io/madr/)
- MADR 4.0.0 ships four templates: `adr-template.md` (full, annotated), `adr-template-minimal.md`, `adr-template-bare.md`, `adr-template-bare-minimal.md`. — [adr/madr template dir](https://github.com/adr/madr/tree/4.0.0/template)
- MADR full template: optional YAML front matter (`status: proposed | rejected | accepted | deprecated | ... | superseded by ADR-0123`, `date` = when last updated, `decision-makers`, `consulted`, `informed`); sections Context and Problem Statement (required), Decision Drivers (optional), Considered Options (required), Decision Outcome ("Chosen option: X, because ...") with optional Consequences (Good/Bad bullets) and optional Confirmation (how compliance is verified, e.g. ArchUnit/fitness function), Pros and Cons of the Options (optional), More Information (optional). The minimal template is only Context and Problem Statement / Considered Options / Decision Outcome (+ optional Consequences). — [MADR adr-template.md](https://github.com/adr/madr/blob/4.0.0/template/adr-template.md), [adr-template-minimal.md](https://github.com/adr/madr/blob/4.0.0/template/adr-template-minimal.md)
- MADR file convention: `NNNN-title-with-dashes.md`, lowercase, in `decisions/` subfolder, typically `docs/decisions`; other patterns are possible but tooling may not support them. — [adr.github.io/madr](https://adr.github.io/madr/)
- Y-statement short form: "In the context of <use case/user story>, facing <concern> we decided for <option> to achieve <quality>, accepting <downside>." Long form adds "and neglected <other options>" and "because <additional rationale>". The adr org says its guidance is based on the Zdun et al. "Sustainable Architectural Decisions" article which suggests the Y-statement. — [adr.github.io templates post](https://github.com/adr/adr.github.io/blob/main/_posts/2024-10-25-adr-templates.md), [adr.github.io index](https://github.com/adr/adr.github.io/blob/main/index.md)
- Joel Parker Henderson's collection lists many templates: Nygard ("simple and popular"), Tyree/Akerman (more sophisticated), Alexandrian, business case, MADR, Planguage, Larrañaga ITDs, plus Y-statements (Zimmermann). — [joelparkerhenderson/architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record)
- Joel's repo recommends: directory `adr/` or `decisions/` (some teams find "decisions" more approachable and start putting vendor/planning decisions in it too); one markdown file per ADR committed to git; present-tense imperative verb-phrase lowercase-dashes names (e.g. `choose-database.md`). — [Joel Parker Henderson README](https://github.com/joelparkerhenderson/architecture-decision-record)
- adr-tools (Nygard-format bash CLI): default directory `doc/adr`; `adr init`, `adr new "Title"`, `adr new -s 9 "Title"` creates an ADR superseding ADR 9. Repo ~5.8k stars, last push 2024-04-25 (effectively dormant). — [npryce/adr-tools](https://github.com/npryce/adr-tools)
- log4brains: docs-as-code ADR knowledge base with static-site publishing, default template MADR, notably does NOT require numbered filenames (to avoid git merge conflicts), supports global and package-specific ADRs. ~1.6k stars, last push 2024-12-17 (dormant). — [thomvaill/log4brains](https://github.com/thomvaill/log4brains)
- adr.github.io tooling page lists many tools (adr-log keeps an index.md updated; pyadr handles proposal/acceptance/rejection/deprecation/superseding lifecycle; Backstage ADR plugin; adr-tools ports in many languages) and itself says to check status/maturity of each. — [adr.github.io tooling](https://github.com/adr/adr.github.io/blob/main/_posts/2024-10-28-adr-tooling.md)
- Immutability: Joel's guidance says a good ADR is "Immutable: Don't alter existing information in an ADR. Instead, amend the ADR by adding new information, or supersede the ADR by creating a new ADR." Same page, teamwork section: "In theory, immutability is ideal. In practice, mutability has worked better for our teams" - insert new info with a date stamp and a note that it arrived after the decision, producing a "living document". — [Joel Parker Henderson README](https://github.com/joelparkerhenderson/architecture-decision-record)
- Joel's guidance on when NOT to write: not architectural, tiny/single-developer, already covered by standards, temporary (workarounds, PoCs, experiments). Write when future developers need the "why". Also suggests ADR "Consequences" may list follow-up ADRs and teams often review an ADR a month later. — [Joel Parker Henderson README](https://github.com/joelparkerhenderson/architecture-decision-record)
- Definitions: an AD is a justified design choice addressing an architecturally significant requirement (ASR); an ADR captures a single AD and rationale; the collection is the "decision log". — [adr.github.io index](https://github.com/adr/adr.github.io/blob/main/index.md)
- Status vocabularies in practice: Nygard "proposed, accepted, rejected, deprecated, superseded"; MADR "proposed | rejected | accepted | deprecated | ... | superseded by ADR-0123". Joel's page defines no fixed status field. — see sources above

### Inferences
- For an agent-facing catalog skill, MADR-minimal (or Matt Pocock's even leaner form, see section 2) is the best default: the four-field Nygard shape is nearly identical, but MADR's "Considered Options" gives the rejected-alternatives record that agents otherwise omit. Y-statement is a good one-line form for the index/summary line or for tiny decisions.
- Numbered filenames cause merge conflicts in parallel branches (log4brains' stated reason for dropping them). With agents working in parallel worktrees this is a real risk; a skill should say "scan for highest number at write time, expect to renumber on rebase" or allow date-prefixed names. This is my inference from log4brains' rationale, not a tested claim.
- Pragmatic immutability rule for a skill: body of an Accepted ADR is not rewritten; allowed edits are the status line, a "superseded by" pointer, and dated appended notes.

### Gaps
- Could not re-fetch Nygard's original post text in this session (rate limit); relied on secondary renderings. Nygard's own statements on immutability ("if a decision is reversed, we will keep the old one around, but mark it as superseded") and length ("one or two pages") are from my memory and NOT confirmed here.
- Zimmermann's Medium Y-statement article was not read directly; only the adr.github.io summary.
- No authoritative source found for which status values are "standard"; vocabularies differ between Nygard and MADR.

---

## 2. Existing agent skills / prompts for ADRs (read contents)

### Takeaway
There are many ADR skills; the two best-evidenced are Matt Pocock's `domain-modeling` (very lean, strict 3-part significance test, lazy directory creation, ~317k stars for the repo) and affaan-m/ECC `architecture-decision-records` (Nygard-based, approval-gated, index README). Spec-driven frameworks (OpenSpec, spec-kit, Superpowers, GSD) have no first-class ADR step; OpenSpec archives design.md but only syncs spec deltas forward.

### Cited Findings
- **mattpocock/skills** (MIT, ~317k stars, pushed 2026-11-05): ADR logic lives in `skills/engineering/domain-modeling/` (`SKILL.md` + `ADR-FORMAT.md` + `GLOSSARY-FORMAT.md`), also referenced from `grill-with-docs`. — [repo](https://github.com/mattpocock/skills), [SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md), [ADR-FORMAT.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/ADR-FORMAT.md)
  - Location: `docs/adr/`, sequential `0001-slug.md`; create the directory lazily only when the first ADR is needed; scan for highest number and increment; multi-context repos use a `GLOSSARY-MAP.md` with system-wide ADRs in root `docs/adr/` and context-specific ones in each context's `docs/adr/`.
  - Template is just `# {Short title}` plus "1-3 sentences: what's the context, what did we decide, and why." Explicitly: "An ADR can be a single paragraph. The value is in recording that a decision was made and why, not in filling out sections." Optional: Status frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`), Considered Options, Consequences - "only when they add genuine value."
  - Significance test, ALL three must be true: (1) hard to reverse, (2) surprising without context ("a future reader will wonder why on earth they did it this way"), (3) result of a real trade-off (genuine alternatives). "If any of the three is missing, skip the ADR." Skill frames it as "Offer ADRs sparingly" (offers to the user rather than auto-writing).
  - Qualifying categories listed: architectural shape; integration patterns between contexts; technology choices with lock-in ("would take a quarter to swap out"); boundary/scope decisions (explicit no's); deliberate deviations from the obvious path; constraints not visible in code; non-obvious rejected alternatives.
  - Trigger description (frontmatter): "Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a GLOSSARY.md, or recording or editing an ADR." (Third-party catalogs describe an earlier version using `CONTEXT.md`; current repo uses `GLOSSARY.md`.)
- **affaan-m/everything-claude-code** (MIT, ~299k stars, pushed 2026-11-06) `skills/architecture-decision-records/SKILL.md`: — [SKILL.md](https://github.com/affaan-m/everything-claude-code/blob/main/skills/architecture-decision-records/SKILL.md)
  - Trigger: "record this decision", "ADR this", choosing between frameworks/databases, discussing trade-offs, asks "why did we choose X?" (read mode).
  - Format: Nygard-derived with Date/Status (proposed | accepted | deprecated | superseded by ADR-NNNN)/Deciders, Context (2-5 sentences), Decision (1-3 sentences), Alternatives Considered (pros/cons/why-not), Consequences (positive/negative/risks).
  - Workflow: first use asks consent before creating `docs/adr/`, `README.md` index (table: ADR link, Title, Status, Date) and `template.md`; present draft, write only after explicit approval; update index; scan to assign number. Separate "Reading Existing ADRs" flow (check dir, scan index, present Context+Decision).
  - Explicit detection signals: explicit ("let's go with X", "record this as an ADR") vs implicit (framework comparisons, schema choices, auth strategy, deployment infra) - implicit = suggest only, never auto-create.
  - Don'ts: trivial decisions, essays (context > 10 lines too long), omitting alternatives, unmarked backfill, stale superseded ADRs. Suggests integrating with planner (suggest ADR) and code-reviewer (flag architectural PRs without ADR). Weak spot: category table includes "Process", "Testing" "coverage targets" - broad, invites spam; no significance test as strict as Pocock's.
- **wshobson/agents** (MIT, ~42k stars) `plugins/documentation-generation/skills/architecture-decision-records/SKILL.md`: reference-style skill; templates (standard, lightweight, Y-statement, deprecation, RFC) in separate files; statuses Proposed/Accepted/Deprecated/Superseded/Rejected; `docs/adr/` with README index + `template.md`; relies on adr-tools commands (`adr init`, `adr new -s`, `adr generate toc`, `adr link`); "Keep them short" (1-2 pages max), "Don't change accepted ADRs", "Don't hide failures"; write for framework/DB/API/security/integration choices, skip minor upgrades, bug fixes, implementation details, config changes. A third-party directory reports ~3.8k installs (unverified). — [vibeindex listing](https://www.vibeindex.ai/skills/wshobson/agents/architecture-decision-records), [wshobson/agents](https://github.com/wshobson/agents) (content summarized via fetch, not re-read in raw form)
- **ncklrs/startup-os-skills `adr`**: MADR-based; seven modes (`create`, `review`, `check-ready`, `check-done`, `template`, `list`, none); "readiness check" using START criteria and ASR test ("Don't decide too early... Don't decide too late either"); quality evaluation against ECADR criteria; checks drafts against 11 anti-patterns. Heavy, process-oriented (decision-journal framing) - not agent-ergonomic. — [startup-os-skills adr](https://github.com/ncklrs/startup-os-skills) (via fetch summary)
- **OpenSpec** (Fission-AI/OpenSpec, MIT, ~74k stars): no native ADR concept. `design.md` holds "technical approach and architecture decisions" per change and is archived to `changes/archive/` with the change; only spec deltas merge into `openspec/specs/`. Community schema `spec-driven-with-adr` adds a 5th (ADR) artifact stored outside `openspec/` so it persists after archive; a blog suggests a lighter `decision.md` in the archived change folder. — [OpenSpec docs/concepts.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md), [intent-driven.dev post](https://intent-driven.dev/blog/2026/04/29/spec-driven-development-with-adr/), [glukhov.org rejected-proposals convention](https://glukhov.org/ai-devtools/openspec/handling-rejected-proposals/)
- **intent-driven.dev**: ADRs are meant to keep design reasoning available to future proposals after archive; example: Postgres storage ADR lets a later full-text-search proposal build on it instead of re-debating storage. Only guardrail given is "significant architectural changes or decisions"; does not say how to extract from design.md. — [post](https://intent-driven.dev/blog/2026/04/29/spec-driven-development-with-adr/)
- **spec-kit** (github/spec-kit, ~148k stars): has a "constitution" (`.specify/memory/constitution.md`, `speckit.constitution` command) for project principles, but no ADR files found in repo tree. **Superpowers** (obra/superpowers, ~314k stars): plans/specs under `docs/plans/` and `docs/superpowers/specs/`, no ADR skill found in tree. **GSD** (gsd-build/get-shit-done, ~64k stars): has its own `docs/adr/` for its own architecture, but no user-facing ADR skill found in tree. — repo trees via GitHub API: [spec-kit](https://github.com/github/spec-kit), [superpowers](https://github.com/obra/superpowers), [GSD](https://github.com/gsd-build/get-shit-done)
- **anthropics/skills** (~188k stars): no ADR or mermaid skill in repo tree (only e.g. `canvas-design`). — [anthropics/skills](https://github.com/anthropics/skills)

### Inferences
- The ecosystem converges on: `docs/adr/NNNN-slug.md`, Nygard/MADR-lite, README index, statuses proposed/accepted/deprecated/superseded, "ask before writing". Quality differentiator is the significance filter; Pocock's three-part test is the sharpest and most agent-appropriate. ECC's is the more complete workflow (index, read mode, approval).
- No surveyed skill implements "extract ADRs from a finished plan's Decisions list" - that mode would be novel. OpenSpec's archive-loses-design.md problem is the same gap as the user's "no record of post-implementation state".

### Gaps
- Did not read raw SKILL.md for wshobson, ncklrs, softaworks; those are from fetch summaries.
- Popularity of individual skills (as opposed to the repos hosting them) is unverified; stars given are for the host repo, which is a monorepo of many skills. Install counts come from third-party directories.
- Did not search Cursor rules / MCP ADR servers (rate limit hit); the web search did surface registries (skills.browseract.com, vibeindex.ai, claudemarketplaces.com) but no MCP ADR server was evaluated.

---

## 3. Best practice for AI-agent-authored ADRs

### Takeaway
Sourced evidence is thin and comes mostly from skill authors, not studies. The convergent practices: strict significance test, agent proposes and human approves, lazy creation, short ADRs, record alternatives, never silently rewrite accepted ADRs, and keep ADRs (why) separate from specs/architecture docs (what the system looks like now).

### Cited Findings
- Significance test (Pocock): hard to reverse AND surprising without context AND real trade-off; "If a decision is easy to reverse, skip it: you'll just reverse it." — [ADR-FORMAT.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/ADR-FORMAT.md)
- Skip list (Joel): non-architectural, tiny/single-dev, already covered by standards, temporary workarounds/PoCs. Skip list (wshobson): minor version upgrades, bug fixes, implementation details, routine maintenance, config changes. — [Joel](https://github.com/joelparkerhenderson/architecture-decision-record), [wshobson listing](https://www.vibeindex.ai/skills/wshobson/agents/architecture-decision-records)
- Human gate: ECC requires explicit approval before writing; implicit decision signals "suggest only, do not auto-create"; Pocock says "offer". — [ECC SKILL.md](https://github.com/affaan-m/everything-claude-code/blob/main/skills/architecture-decision-records/SKILL.md)
- Brevity: ECC "readable in 2 minutes", context < 10 lines; wshobson 1-2 pages; Pocock "an ADR can be a single paragraph". — same sources
- Backfilled decisions should be marked with the original date; superseded ADRs must link their replacement. — [ECC SKILL.md](https://github.com/affaan-m/everything-claude-code/blob/main/skills/architecture-decision-records/SKILL.md)
- Separation of concerns: OpenSpec says a spec describes observable behavior ("what the system does today"), a design describes how it will be built; implementation detail belongs in design not spec; archived change retains full context "not just what changed, but why". intent-driven.dev frames specs as "what the system does today" and ADRs as "how and why". — [OpenSpec docs/faq.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/faq.md), [intent-driven.dev](https://intent-driven.dev/blog/2026/04/29/spec-driven-development-with-adr/)
- Pocock's skill keeps `GLOSSARY.md` free of implementation decisions ("not a spec, a scratch pad, or a repository for implementation decisions") - an example of deliberately separating living reference docs from decision records. — [domain-modeling SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md)
- Joel: teams review ADRs ~1 month later vs. actual outcomes; ADR consequences can list follow-up ADRs; one AD per ADR. MADR 4.0 "Confirmation" section describes how compliance can be verified (fitness function, ArchUnit, code review). — [Joel](https://github.com/joelparkerhenderson/architecture-decision-record), [MADR template](https://github.com/adr/madr/blob/4.0.0/template/adr-template.md)
- Cross-skill integration idea in ECC: planner suggests ADR; code reviewer flags architectural PRs lacking an ADR. — [ECC SKILL.md](https://github.com/affaan-m/everything-claude-code/blob/main/skills/architecture-decision-records/SKILL.md)

### Inferences
- Anti-spam levers a skill can encode: (1) the three-part test as a hard gate, (2) a cap/batching rule such as "propose at most N ADR candidates per plan, present as a list, user picks", (3) default to NOT writing; write only after approval, (4) prefer folding minor decisions into the architecture overview or plan "Decisions" section rather than a new ADR, (5) require a named rejected alternative (if none, it is not a decision).
- Extract-from-plan: a plan's Decisions list is the natural candidate source; run each through the gate after implementation, and compare against the actual diff (decisions often change during implementation). Link both ways: ADR "More information" -> `docs/plans/<feature>.md` and PR; plan gets a "Resulting ADRs" footer. This workflow design is my inference; no surveyed source implements it.
- Living architecture overview (e.g. `docs/architecture/overview.md`, with Mermaid diagrams) is "current state" and is edited in place; ADRs are "why/when" and are append-only. The OpenSpec design.md-archive gap shows what happens without the latter: reasoning disappears.
- Because the user's repo currently has no post-implementation record, a "backfill" mode (clearly marked with original dates per ECC) may be needed for existing decisions such as those in `PLATFORM_CONTEXT.md`.

### Gaps
- No empirical study or authoritative source found on LLM-authored ADR quality, ADR spam rates, or maintenance burden; all of the above is practitioner opinion.
- No source found on the ADR-to-PR linking convention beyond general "More information" links.

---

## 4. Design options for a catalog ADR skill (recommendation, derived from the above)

### Takeaway
One skill, `adr`, with a lean default template, a hard significance gate, and four modes: propose, record, supersede, extract-from-plan; plus a generated index. Keep MADR-minimal as the default and let consuming repos override template/location via `.ai/overlays`.

### Cited Findings (design inputs)
- Catalog rule: keep content generic; repo paths and project names belong in consuming repo overlays/`bundle.json`; every skill needs `metadata.routing-tier`; tool-specific frontmatter is rendered, not hand-written. — [skill-bundle AGENTS.md](/home/patex1987/development/movie-reservation-platform-lab/skill-bundle/AGENTS.md)
- Reference conventions to align with: default `docs/adr/NNNN-slug.md` (Pocock, ECC, wshobson), or `docs/decisions/` (MADR, Joel). — see sections 1-2

### Inferences (recommended design)
- **Trigger/description**: "Use when recording, proposing, superseding, or auditing an architecturally significant decision, or after implementing a plan to capture its decisions" - include phrases "record this decision", "ADR", "why did we choose", "supersede". Model description on Pocock's concise style; avoid ECC's broad "Process/Testing" categories.
- **Modes**:
  1. *propose*: during planning/discussion, run the 3-part gate; output a candidate list (title + one-line Y-statement-style rationale), write nothing.
  2. *record*: write one approved ADR (status `accepted`, or `proposed` if pending), assign number by scanning highest existing, update index; create `docs/adr/` lazily.
  3. *supersede*: new ADR with `Supersedes: ADR-NNNN`; change old ADR status to `superseded by ADR-MMMM` (only permitted edit besides dated notes); update index.
  4. *extract-from-plan*: read `docs/plans/<feature>.md` Decisions list + the implementation diff/PR; filter via gate; flag decisions that changed during implementation; draft ADRs for approval; add back-links in plan and ADR (`Source: docs/plans/<feature>.md`, PR URL). Also a *read/why* mode (ECC) answering "why did we choose X" from the index.
- **Template** (default, MADR-minimal-plus): front matter `status`, `date`, optional `supersedes`/`superseded-by`, `links` (plan, PR, issue); body `Context and Problem Statement` (2-5 sentences), `Considered Options` (>=2, else not an ADR), `Decision Outcome` (chosen + because), optional `Consequences` and `Confirmation`. Allow collapse to Pocock single-paragraph form for small ones. Put the template in `references/template.md` and the gate in `references/significance-test.md` (progressive disclosure).
- **Index**: `docs/adr/README.md` table (number linked, title, status, date), regenerated/appended by the skill; optionally a tiny script (`scripts/`) that rebuilds the index from front matter and validates: unique numbers, valid status, superseded-by targets exist, links resolve. A validation script is a differentiator vs. all surveyed skills (none ship one).
- **Boundaries to state in the skill**: ADR = why, immutable-ish; architecture overview = current state, edited in place (see Mermaid skill); plan = intent before implementation; research = inputs. Rule: never edit an accepted ADR's decision text.
- **Anti-spam**: cap candidates, default to no-write, human approval gate, "no rejected alternative => not an ADR".

### Gaps
- Not tested against real agent behavior; recommendations are design hypotheses. Suggest a small eval (plan with 6 decisions, 2 significant) before finalizing.

---

## 5. Existing Mermaid skills / guidance for agents

### Takeaway
There are many Mermaid skills, but most are syntax catalogs (diagram-type tables plus per-type reference docs); few emphasize validation, renderer compatibility, or version drift. The most useful pattern is a short SKILL.md with a diagram-type chooser and per-type reference files, plus a render/validate step. Some skills already carry stale advice after Mermaid 12.

### Cited Findings
- **WH-2099/mermaid-skill** (~299 stars, pushed 2026-08-11): `.claude/skills/mermaid/SKILL.md` + ~25 `references/*.md` (flowchart, sequence, class, state, ER, gantt, C4, architecture, block, packet, kanban, radar, treemap, config-theming, config-directives, config-layouts, etc.). Workflow: understand requirement -> pick diagram type -> read the matching reference -> generate -> apply styling. Output rules: fenced ```mermaid, correct syntax, semantic node names. No validation step. — [repo](https://github.com/WH-2099/mermaid-skill), [SKILL.md](https://github.com/WH-2099/mermaid-skill/blob/main/.claude/skills/mermaid/SKILL.md)
- **imxv/Pretty-mermaid-skills** (~1.6k stars, pushed 2026-08-22): single `SKILL.md` repo; highest-starred mermaid skill repo found via `gh search repos "mermaid skill"` (content not read). — [repo](https://github.com/imxv/Pretty-mermaid-skills)
- **softaworks/agent-toolkit `mermaid-diagrams`** (~2.6k stars, last push 2026-03-05): SKILL.md with a diagram-type selection guide (class, sequence, flowchart, ERD, C4, state, git, gantt, pie), references per type (flowcharts, sequence, class, erd, c4, architecture, advanced-features), and a companion agent `mermaid-diagram-specialist`. Notes "Unknown words break diagrams; parameters fail silently." — [SKILL.md](https://github.com/softaworks/agent-toolkit/blob/main/dist/plugins/mermaid-diagrams/skills/mermaid-diagrams/SKILL.md)
- **Cogni-AI-OU/cogni-ai-agent-skills `mermaid`** (~4 stars): "stable v11+" skill emphasizing "clarity first, render compatibility (GitHub, VS Code, Mermaid Live Editor), minimalism, Easy-To-Change, Doc-Rot prevention"; names the Live Editor as primary verification. Its sample config uses `flowchart.defaultRenderer: "elk"`, which Mermaid 12.0.0 removed (see section 7) - evidence of staleness risk. — [SKILL.md](https://github.com/Cogni-AI-OU/cogni-ai-agent-skills/blob/main/mermaid/SKILL.md); removal: [mermaid 12.0.0 release notes](https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4012.0.0)
- Others surfaced by search (descriptions only, not read): Agents365-ai/mermaid-skill (checks for `mmdc` first, falls back to Kroki; repo URL returned 404 via API, so possibly moved/renamed), awesome-skills `mermaid-syntax` ("error-free, v11 support"), wanshuiyin `mermaid-diagram` (20+ types), ccheney/robust-skills `mermaid-diagrams`, rysweet/amplihack `mermaid-diagram-generator`. — [search results via Claude marketplaces/vibeindex listings](https://claudemarketplaces.com/skills/ccheney/robust-skills/mermaid-diagrams)
- Anthropic's own `anthropics/skills` repo has no Mermaid skill. — [anthropics/skills](https://github.com/anthropics/skills)
- A MindStudio article claims Mermaid in skill files compresses context ~3-6x vs prose; this is a vendor claim, not a benchmark. — [MindStudio](https://www.mindstudio.ai/blog/mermaid-diagrams-claude-code-skills-context-compression/)

### Inferences
- The gap in the market: validation-in-the-loop, renderer-compat tables, version awareness, and "when not to draw" guidance. All surveyed skills focus on syntax coverage that the model largely already knows.
- A catalog skill should be small and judgment-focused (choose type, keep it small, validate), pointing at official docs for syntax rather than copying 25 reference files that go stale.

### Gaps
- Did not read Pretty-mermaid-skills, Agents365-ai, awesome-skills, wanshuiyin, ccheney or rysweet SKILL.md contents; star counts for most not verified. Quality assessment is limited to WH-2099, softaworks, Cogni.
- No MCP mermaid validator servers evaluated (search/fetch rate limit).

---

## 6. Practical Mermaid guidance: type choice, pitfalls, limits, theming, validation

### Takeaway
Pick the diagram type by the question being answered; quote labels, avoid lowercase `end`, keep diagrams small; validate by actually rendering with `mmdc` (the `@mermaid-js/parser` package does NOT cover flowchart/sequence/class/state/ER); do not rely on theme/layout defaults because Mermaid 12 changed them.

### Cited Findings
**Official diagram list and stability** — [Mermaid syntax reference](https://mermaid.js.org/intro/syntax-reference.html) (fetched; reflects current docs): marked Beta: Swimlanes, Use Case, Architecture, Radar, Venn, Wardley, Cynefin, TreeView. Unlabelled/stable: Flowchart, Sequence, Class, State, ER, User Journey, Gantt, Pie, Quadrant, Requirement, GitGraph, C4, Mindmap, Timeline, ZenUML, Sankey, XY, Block, Packet, Kanban, Event Modeling, Treemap, Ishikawa. Every diagram begins with its type declaration (frontmatter is the only exception).

**Type selection (from skill guides; there is no single authoritative chooser)**
- softaworks guide: class = domain modeling/OOP; sequence = temporal interactions/API flows; flowchart = processes/algorithms/decisions; ERD = DB schema; C4 = architecture at context/container/component levels; state = lifecycles. — [softaworks SKILL.md](https://github.com/softaworks/agent-toolkit/blob/main/dist/plugins/mermaid-diagrams/skills/mermaid-diagrams/SKILL.md)
- ER docs: entities named with singular nouns; logical models may omit foreign keys since relationships convey them. — [ER docs source](https://github.com/mermaid-js/mermaid/blob/develop/packages/mermaid/src/docs/syntax/entityRelationshipDiagram.md)
- `architecture-beta`: beta since v11.1.0, syntax "may still change in a backwards-incompatible way"; built-in icons only cloud/database/disk/internet/server; identifiers must be declared before use; group IDs can't be edge endpoints (needs `{group}` modifier on services inside); siblings can overlap (issue #6120). — [architecture docs](https://mermaid.js.org/syntax/architecture.html)
- C4 in Mermaid: not labelled experimental, but "layout does not use a fully automated layout algorithm" (placement depends on statement order; default 4 shapes/row, 2 boundaries/row; `UpdateLayoutConfig`), sprites/tags/links/legend unsupported, fixed style with no theme support. — [C4 docs](https://mermaid.js.org/syntax/c4.html)

**Syntax pitfalls (official docs)**
- Lowercase `end` breaks flowcharts (use `End`/`END` or quote) and sequence diagrams (wrap in `()`, `""`, `[]`, `{}`). — [flowchart docs](https://mermaid.js.org/syntax/flowchart.html), [sequence docs](https://github.com/mermaid-js/mermaid/blob/develop/packages/mermaid/src/docs/syntax/sequenceDiagram.md), [syntax reference](https://mermaid.js.org/intro/syntax-reference.html)
- Wrap troublesome label text (parentheses, unicode) in double quotes: `id1["This is the (text) in the box"]`; entity codes like `#quot;` for quotes (base-10 codes; HTML names also work). — [flowchart docs](https://mermaid.js.org/syntax/flowchart.html)
- After an edge, node names starting with `o` or `x` are parsed as circle/cross edge markers (`A---oB`): add a space or capitalize. — [flowchart docs](https://mermaid.js.org/syntax/flowchart.html)
- Comments: `%%` on its own line; avoid `{}` inside `%%` comments (confuses `%%{ }%%` directives). — [syntax reference](https://mermaid.js.org/intro/syntax-reference.html)
- Unknown words and misspellings break a diagram while misspelled parameters/frontmatter keys are silently ignored; malformed frontmatter breaks it; frontmatter opening `---` must be alone on its line. — [syntax reference](https://mermaid.js.org/intro/syntax-reference.html)
- Nested shapes confuse the parser; quote labels. — [syntax reference](https://mermaid.js.org/intro/syntax-reference.html)
- Subgraph: `subgraph id [Title]`; a `direction` inside a subgraph is ignored if any of its nodes link outside it. Subgraph ids with spaces must be quoted in ER subgraphs (v11.17.0+). — [flowchart docs](https://mermaid.js.org/syntax/flowchart.html), [ER docs source](https://github.com/mermaid-js/mermaid/blob/develop/packages/mermaid/src/docs/syntax/entityRelationshipDiagram.md)
- ER attribute comments in double quotes cannot themselves contain double quotes; keys limited to PK/FK/UK. — [ER docs source](https://github.com/mermaid-js/mermaid/blob/develop/packages/mermaid/src/docs/syntax/entityRelationshipDiagram.md)
- External CSS targeting Mermaid's SVG "generally won't work reliably"; use `classDef`. `linkStyle` indexes edges by definition order. Click handlers disabled under `securityLevel: strict` (the default). — [flowchart docs](https://mermaid.js.org/syntax/flowchart.html), [usage docs](https://mermaid.js.org/config/usage.html)

**Size/readability limits**
- Config defaults: `maxTextSize` 50000 characters, `maxEdges` 500 (diagram fails above these). Layout default `elk`, look `classic` in the schema doc (note: per-diagram theme/look defaults differ in v12, see section 7). — [config schema](https://mermaid.js.org/config/schema-docs/config.html)
- No official "readable node count" guidance found. 

**Theming / dark mode**
- Themes: default, neutral, dark, forest, base, plus v12 additions redux, redux-color, redux-dark, redux-dark-color, neo, neo-dark. Only `base` is customizable via `themeVariables`; `darkMode: true` for dark bg; only hex colors accepted (not color names). Set per diagram in frontmatter `config.theme`. — [theming docs](https://mermaid.js.org/config/theming.html)
- mmdc: `-t dark -b transparent` for dark theme transparent PNG; `--cssFile` passes `themeCSS` (CSP may block). — [mermaid-cli README](https://github.com/mermaid-js/mermaid-cli)

**Validation**
- `mermaid.parse(text, {suppressErrors})` returns `{diagramType}` on valid, throws (or returns false with suppressErrors) on invalid; it checks syntax without rendering. — [usage docs](https://mermaid.js.org/config/usage.html)
- `@mermaid-js/parser` (npm 2.0.1) is a Langium-based parser whose `src/language` directory contains only: architecture, common, cynefin, eventmodeling, gitGraph, info, packet, pie, radar, railroad*, treeView, treemap, wardley. It does NOT include flowchart, sequence, class, state or ER (those still use the legacy Jison parsers in the main `mermaid` package). — [packages/parser](https://github.com/mermaid-js/mermaid/tree/develop/packages/parser/src/language)
- mermaid-cli (`@mermaid-js/mermaid-cli` 12.2.0 on npm, GitHub release 2026-11-02, depends on `mermaid ^12.2.0` and `puppeteer ^25`): requires headless Chromium (Linux sandbox issue documented); `mmdc -i in.mmd -o out.svg`, stdin via `--input -`, `-q` quiet; Markdown input (`mmdc -i doc.md -o out.md`) extracts mermaid blocks to SVG and rewrites links; its internal `error()` helper prints to stderr and `process.exit(1)` for missing files/config. Node API "not covered by semver". README does not document exit codes for diagram parse failures; whether a bad diagram yields non-zero exit in every mode (esp. markdown mode) was not confirmed. — [mermaid-cli](https://github.com/mermaid-js/mermaid-cli), [src/index.js](https://github.com/mermaid-js/mermaid-cli/blob/master/src/index.js)
- `accTitle`/`accDescr` in a block become image alt text/title when mmdc converts markdown. — [mermaid-cli README](https://github.com/mermaid-js/mermaid-cli)

### Inferences
- The most reliable low-dependency check step: run `mmdc` on every ```mermaid block (extracted from the markdown file) and fail on non-zero exit; or use `mermaid.parse` in a headless browser/jsdom harness. `@mermaid-js/parser` alone is insufficient for the common types. Needs Chromium: not installed on this machine (`mmdc`, `chromium`, `google-chrome` not found; Node v24.14.0 present), so the skill should make the check optional/degradable and fall back to a "lint by checklist" pass (quotes, `end`, declared IDs).
- Practical size heuristics (my own, not sourced): <= ~15 nodes per diagram, split by level or concern, one question per diagram, `flowchart LR` for pipelines / `TD` for hierarchies, label edges with verbs; use C4-style layering as separate diagrams instead of one mega-diagram. Treat as design suggestions to test.
- Diagram type -> question mapping that is defensible from the docs above: "who calls whom, in what order" -> sequenceDiagram; "what states can X be in" -> stateDiagram-v2; "what are the data entities" -> erDiagram; "what are the building blocks and boundaries" -> flowchart with subgraphs (or C4 with caveats; architecture-beta only if beta risk acceptable, avoid in GitHub-rendered docs until confirmed); "how does a process branch" -> flowchart; "type/class relationships" -> classDiagram.
- Pin the look explicitly in frontmatter when appearance matters (`theme`, `look`, `layout`) because v12 defaults changed; prefer theme-neutral output (no hard-coded fills) so it renders acceptably in light and dark.

### Gaps
- GitHub-specific: could not retrieve which Mermaid version github.com renders, nor which types it supports (e.g. architecture-beta, C4, v12 features). GitHub docs only say: use ```mermaid fenced block in issues, PRs, discussions, wikis, markdown files; it names flow charts, sequence diagrams, pie charts and says "more"; to check the version, render a ```mermaid block containing `info`; errors may appear with third-party Mermaid plugins. — [GitHub Docs: creating diagrams](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams). Catalog skill should instruct agents to tell users to run an `info` block rather than assume.
- GitLab, VS Code (Markdown preview / Mermaid extension), Obsidian renderer versions and feature gaps: not researched (rate limit).
- `mermaid.parse` in Node without a DOM: known to need DOM shims, but I found no source in this session; unverified.
- No source for how GitHub themes diagrams in dark mode.
- Exact `mmdc` behavior (exit code) on a syntax error: unverified by test; should be tested locally with Chromium before the skill's validation script claims anything.

---

## 7. Mermaid versions as of 2026-11-07

### Takeaway
Mermaid is at 12.3.0 (2026-11-03). v12.0.0 (2026-09) was a breaking release that changed default layout (ELK) and default look/theme (redux-color / neo) and removed `defaultRenderer`; therefore older skill advice and diagrams may render differently, and renderers that lag (GitHub, VS Code) may be on 11.x.

### Cited Findings
- npm `mermaid` dist-tag `latest` = 12.3.0, published 2026-11-03; 12.2.0 on 2026-10-13; 12.1.0 on 2026-10-02; 12.0.0 on 2026-09-10; last 11.x line seen: 11.12.0 (2025-09-18), 11.12.3 (2026-02-17); GitHub release `mermaid@11.17.1` (2026-10-28) shows an 11.x backport line is still being released; npm `backport` tag = 10.9.8; `v13-alpha` tag = 13.0.0-alpha.1. — npm registry ([registry.npmjs.org/mermaid](https://registry.npmjs.org/mermaid)), [GitHub releases](https://github.com/mermaid-js/mermaid/releases)
- 12.0.0 is "a breaking release (ES2024, Safari 17.4+, Node 22.12+)": ELK bundled and default layout (flowchart, state, class, ER, requirement, use-case re-laid out unless `layout: dagre`); new default theme `redux-color` and look `neo` ("Existing flowcharts, state and class diagrams will re-lay out and recolour; add `layout: dagre`, `theme: default` and `look: classic` to keep the old look"); `flowchart/class/state.defaultRenderer` removed in favor of top-level `layout`; new UML use-case diagram. — [mermaid@12.0.0 release](https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4012.0.0)
- 12.3.0: open-arrow and hollow-circle edge markers, BPMN shapes, flowchart step animation (`flowchart.stepDuration`, `flowchart.stepNumbers`). 12.2.0: mindmap `colorBy: depth`. 12.1.0: `elk.orientFeedbackEdges` default on; parse errors show actual message. — [GitHub releases](https://github.com/mermaid-js/mermaid/releases), [flowchart docs source](https://github.com/mermaid-js/mermaid/blob/develop/packages/mermaid/src/docs/syntax/flowchart.md)
- Version-gated features in docs: expanded node shapes `@{ shape: ... }` v11.3.0+; edge IDs v11.10.0+; FontAwesome icon packs v11.7.0+; architecture-beta introduced v11.1.0 (`align` v11.16.0+, `randomize` v11.14.0+); collapsible subgraphs (flowchart) v11.17.0+; ER subgraphs v11.17.0+; optional ER attribute types `?` v11.16.0+; sequence actor create/destroy v10.3.0+; bidirectional sequence arrows v11.0.0+. — [flowchart](https://github.com/mermaid-js/mermaid/blob/develop/packages/mermaid/src/docs/syntax/flowchart.md), [ER](https://github.com/mermaid-js/mermaid/blob/develop/packages/mermaid/src/docs/syntax/entityRelationshipDiagram.md), [sequence](https://github.com/mermaid-js/mermaid/blob/develop/packages/mermaid/src/docs/syntax/sequenceDiagram.md), [architecture](https://mermaid.js.org/syntax/architecture.html)
- mermaid-cli 12.2.0 pairs with mermaid ^12.2.0. — [mermaid-cli package.json](https://github.com/mermaid-js/mermaid-cli/blob/master/package.json)

### Inferences
- The GitHub renderer's version is unknown here; the safe policy is to restrict generated diagrams to long-stable syntax (flowchart, sequenceDiagram, stateDiagram-v2, erDiagram, classDiagram, and basic features) in committed docs, and to avoid features tagged v11.10+ / v12+ and beta types unless the target renderer is confirmed.
- Because v12 changed defaults, the skill should avoid assuming appearance and should not reference `defaultRenderer`.

### Gaps
- GitHub, GitLab and VS Code Mermaid versions (see section 6 Gaps).
- Whether the npm date for 12.0.0 (2026-09-10 on npm; mermaid-cli 12.0.0 release 2026-09-24) vs the GitHub release page ordering has any discrepancy - I only noted the registry timestamps.

---

## 8. Design options for a catalog Mermaid/diagramming skill (recommendation, derived from the above)

### Takeaway
A small `mermaid-diagrams` skill focused on judgment and verification rather than syntax tutorial: when to draw, which type, hard rules to avoid parse errors, a portability profile, and an optional render-check script. Pair it with the ADR skill and plan workflow via explicit "where diagrams belong" guidance.

### Cited Findings (design inputs)
- Existing skills are syntax catalogs with per-type reference files (WH-2099, softaworks) - see section 5.
- Official docs warn of silent-failure behaviors and stale-prone options - see sections 6-7.

### Inferences (recommended design)
- **Scope**: documentation diagrams in markdown (plans, ADRs, `docs/architecture/*.md`, PR descriptions), NOT artifact/SVG hand-drawing (that is covered by the separate Claude artifact-diagramming skill).
- **When a diagram earns its place** (gate, mirroring the ADR gate): it shows structure/flow/state that prose would take >N sentences to convey and that a reader needs to hold at once (service boundaries, request sequences across >=3 participants, state lifecycle with >=4 states, entity relations). Skip for linear 3-step flows, lists, or anything that duplicates a table. Each diagram needs a one-line caption stating the question it answers and, in architecture docs, a "last verified against" note or reference to commit/plan, because diagrams rot (Cogni skill's "Doc-Rot prevention" framing).
- **Where diagrams go**: plans -> only a sequence or flow for non-obvious interactions; ADRs -> at most one small diagram for the chosen structure (or none; text first); `docs/architecture/overview.md` (living, current state) -> C4-style context/container flowcharts and key sequences, edited in place and updated whenever implementation changes structure.
- **SKILL.md body** (short): type chooser table (question -> type), hard rules (quote every label that has punctuation; never lowercase `end`; declare IDs before use; use short ASCII IDs with human labels; `%%` comments on own lines; one idea per diagram; max node count; direction guidance), portability profile (stable types only for GitHub-rendered docs; avoid beta types, v11.10+/v12+ features, `defaultRenderer`; don't hard-code theme colors; pin `theme/look/layout` only when needed), and a workflow: draft -> run check -> fix -> done.
- **References** (loaded on demand): `references/type-chooser.md`, `references/pitfalls.md` (the list in section 6 with failing/fixed pairs), `references/renderer-compat.md` (GitHub/GitLab/VS Code/mmdc with "date checked" - consistent with AGENTS.md rule to record date checked for vendor mechanics), `references/c4-in-mermaid.md` (flowchart-with-subgraphs idiom vs `C4Context` caveats).
- **Validation script** (`scripts/check-mermaid.*`): extract fenced ```mermaid blocks from given markdown files, write each to a temp file, run `mmdc` per block, report file:line of failures; degrade gracefully with a clear "mmdc/Chromium not available; ran static checks only" message; static checks: block starts with a known type keyword, lowercase `end` as a node label, unbalanced brackets/quotes, size vs. 50000 chars / 500 edges. Document that `@mermaid-js/parser` cannot validate flowchart/sequence/class/state/ER. Needs testing with a real Chromium install since none exists on this machine.
- **Routing tier**: low-to-medium (judgment is mostly "do I need a diagram, which type"); consider ADR skill medium since the significance judgment is the hardest decision.

### Gaps
- Need to test the script and the guidance with real renderers (mmdc + GitHub preview) before making compatibility claims.
