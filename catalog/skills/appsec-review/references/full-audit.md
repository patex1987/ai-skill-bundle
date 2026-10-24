# Full Audit

A full audit maps the system, plans coverage explicitly, reviews each coverage
unit in isolation, verifies every candidate in a fresh context, and reports only
what survived. It is expensive, so agree the setup with the user before starting.

## Setup (confirm before any fan-out)

| Item | Default |
|---|---|
| Scope | The whole repository, or named paths, subsystems, or a ref range. Out-of-scope areas are recorded as `out_of_scope`, never as covered |
| Source ref | The reviewed commit, plus whether the working tree is dirty |
| Profile | `standard`. See below |
| Budget | A maximum number of agent invocations, proposed from the profile and repository size |
| Output directory | A new directory **outside** the repository, such as the session scratch area or a user-chosen path. Write inside the repository only when the user picks a path that version control ignores |
| Execution policy | Source review plus sandboxed local checks only (see the safety rules in `SKILL.md`) |

Findings are sensitive. Do not commit audit artifacts or attach exploit detail to
public issues unless the user decides to.

### Profiles

- **quick**: a coarse ledger (one unit per surface × attack class), one review
  wave, one critic pass, and one verifier per candidate. Report it as partial
  coverage.
- **standard**: the workflow as written. Repeat waves until a critic pass finds
  no accepted gaps, or the budget stops the run.
- **deep**: split units per subsystem and lifecycle (create, update, delete,
  export, restore, migration). Give previously covered units a second
  independent pass, and use separate verifiers for candidate validation and
  for final record checks.

A profile changes breadth and redundancy, never the evidence bar.

### Budget

One coverage unit is roughly one reviewer invocation. One surviving candidate
is one or two verifier invocations. Before the first wave, reserve:
- the critic passes
- about 30% of the remaining budget for verification

Never spend the verification reserve on more hunting. When the budget runs out:
- mark the untouched units `deferred`
- validate the open candidates you can
- report the run as incomplete, with the reason

## Phase 1: Reconnaissance

Run these briefs in parallel. Use read-only `scout` agents for inventory and
`security-practices` for the controls map. Each returns facts with `path:line`
anchors and writes nothing.

1. **Product and stack:** what the system does, its users and operators, its
   languages, frameworks, runtimes, and deployment shape, its entry points and
   subsystem boundaries, and the offline build and test commands (do not run
   them yet).
2. **Principals and controls:** each actor and what it may do by design; where
   identity is established; how per-resource authorization and tenant scope
   are enforced; workload, CI, plugin, and agent/tool authority; privilege
   changes, revocation, recovery, and fallback paths. Mark each control as
   visible in source or dependent on an unobserved deployment fact.
3. **Entry surfaces and sinks:** HTTP and browser, RPC and messages, files and
   archives, CLI, environment and configuration, webhooks, scheduled jobs,
   CI triggers, cloud events, model context and tool arguments. Follow each one
   through transformations, stored copies, and security-relevant sinks.
4. **Evidence available:** existing tests and fixtures that can check
   boundaries with dummy data, scanner configuration and recent CI results, and
   which commands would fetch dependencies or touch shared state (prohibited).

Synthesize `architecture.md`:
- components and data stores
- trust boundaries
- principals and assets
- entry points
- the controls map
- deployment facts that source cannot establish

To produce a threat model instead of, or before, a hunt, use the threat-model
format in [guidance](guidance.md) and stop there.

## Phase 2: Coverage ledger

`coverage-ledger.json` holds one unit per meaningful combination of entry
surface × trust boundary × attack class (plus subsystem or lifecycle for
`deep`). Take attack classes from [attack surfaces](attack-surfaces.md), and
keep only the ones the architecture makes applicable. Record each excluded
class with its reason.

```json
{
  "id": "POST /orgs/:id/invites::org-membership-check::access-control",
  "surface": "POST /orgs/:id/invites (src/routes/invites.ts:14)",
  "boundary": "org membership check (src/authz/org.ts:40)",
  "attack_class": "access-control",
  "starting_paths": ["src/routes/invites.ts", "src/services/invites.ts"],
  "status": "planned",
  "owner": null,
  "reviewed_paths": [],
  "checks": [],
  "candidates": [],
  "unresolved": []
}
```

Statuses:
- `planned`
- `in_progress`
- `covered` (reviewed, nothing survived)
- `candidate` (produced a candidate)
- `blocked` (needs a fact or capability that isn't available)
- `deferred` (budget or profile)
- `out_of_scope`

Build each `id` from stable source references, not from line numbers, agent
names, or verdicts, so later runs can match units. Only the lead writes the
ledger.

### Prior runs

If earlier audit output exists, read its ledger and findings first:
- A prior finding is carried forward only after re-verification against current
  source.
- Changed source turns its units back into `planned`.
- Prior `needs-validation`, `deferred`, and `blocked` units become current work.
- A prior `rejected` claim suppresses only that exact claim on unchanged code.
  It does not cover the unit.

## Phase 3: Review waves

Give each reviewer one or a few related units and this brief:

```text
Role: unit reviewer (appsec-review, full audit). Read-only; do not run target code
unless the brief grants a sandbox. Units: <ids with starting paths>.
For each unit: follow the input through parsing, identity, authorization,
normalization, state, derived copies, and the sink. Read sibling, legacy, bulk,
retry, error, and migration paths that reach the same effect. Check sad paths only
where the interface accepts them: empty, duplicate, oversized, stale, revoked,
reordered, concurrent, partially migrated. Stop as soon as the invariant is settled
either way. If a high-impact root cause appears, search your own units for variants.
Return JSON only: {"units":[{"id","status","reviewed_paths","checks","unresolved"}],
"candidates":[{"fingerprint","title","actor","input","control","path","effect",
"counterevidence","proposed_state","anchors"}],"uncovered":[{"surface","reason"}]}
```

Route units by difficulty with the `model-routing` tiers:
- `balanced` (high effort) for routine CRUD and configuration surfaces.
- `deep` for authentication, authorization, tenancy, crypto, payment, and
  agent-authority units.

Run independent units in parallel. The lead merges results into the ledger and
deduplicates candidates by fingerprint.

### Coverage critic

After each wave, a fresh reviewer gets `architecture.md` and the ledger, but no
findings. It returns:
- missing units, such as unmapped entry points, parallel paths, lifecycle
  modes, or unjustified exclusions
- units closed without reviewed paths or checks

It proposes coverage, not findings. The lead accepts or rejects each proposal
with a reason. A `standard` run ends after a critic pass with no accepted gaps
and no `planned` units left.

## Phase 4: Independent verification

Give every unique candidate to a fresh verifier that did not produce it, such as
the `security-practices` agent in verifier role at `deep` tier:

```text
Role: verifier (appsec-review). Try to disprove this claim; do not hunt for new
issues. Claim: <one sentence>. Anchors: <path:line list>. Reviewed commit: <sha>.
Find the strongest control that could prevent it (global guards, data-layer scoping,
framework behaviour, configuration, reachability, tests). Return:
{"fingerprint","state":"confirmed|likely|needs-validation|rejected",
"severity" (confirmed/likely only),"evidence","counterevidence_checked",
"unresolved_fact" (needs-validation only),"fix","regression_test"}
```

If the verifier changes a material fact (path, actor, effect, or severity),
send the corrected record to another fresh verifier. Do not write the report
before verification finishes.

## Phase 5: Records and report

Write `findings.json` with one record per fingerprint, in the format from
[report format](report-format.md). Then derive the reports from the records:

- **`REPORT.md`:**
  - scope, profile, commit, and budget
  - an executive summary
  - findings ordered by severity
  - a coverage summary from the ledger, including deferred, blocked, and
    out-of-scope units
  - tool execution states
  - limitations
- **`NEEDS-VALIDATION.md`:** each open question, the exact fact it depends on,
  and a safe check for the owner.

Keep the prose consistent with the JSON. End in exactly one of two states:
- **Complete:** every planned unit is resolved and every candidate verified.
- **Incomplete:** give the reason (budget, missing sandbox, user stop) and the
  affected units.

Never imply that a single run found everything. Repeated runs typically keep
finding new issues.
