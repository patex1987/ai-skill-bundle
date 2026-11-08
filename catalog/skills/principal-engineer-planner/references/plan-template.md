# Plan Template

The structure for `docs/plans/<feature>.md`, used by `principal-engineer-planner`
in authoring mode.

`Status:` records what has actually happened to the plan, never an intention:

| Value | Set by | When |
|---|---|---|
| `draft` | planner | The plan is being written, annotated, or reviewed. |
| `agreed` | planner | The author agreed the acceptance scenarios and authorized implementation. |
| `in-progress` | `plan-execution` | Execution started. |
| `done` | `plan-validation` close-out | Validation returned **verified**. |
| `abandoned` | planner, on the author's instruction | The author dropped the plan. Record why in As-built. |

Plans written before this field existed may have no `Status:`; treat them as unknown,
not as done.

````md
# Implementation Plan: <Name>

Status: draft

## 1. Summary

Brief description of the change and the recommended approach.

Review record: <link, if an interactive review exists>

## 2. Goals

- ...

## 3. Non-goals

- ...

## 4. Current State

Describe the relevant existing architecture, behavior, files, APIs, data flows, tests, and constraints.

## 5. Requirements and Assumptions

### Confirmed Requirements

- ...

### Decisions

- <decision> — Decision (user, <date or Q-ID>)

### Assumptions

- ...

### Open Questions

- ...

## 6. Proposed Design

Describe the recommended design, including main components, responsibilities, data flow, API boundaries, and why this design is preferred.

## 7. Alternatives Considered

### Alternative A: <name>

- Pros:
- Cons:
- Decision:

### Alternative B: <name>

- Pros:
- Cons:
- Decision:

## 8. API / Interface Changes

Describe changes to public APIs, internal interfaces, CLI commands, events, contracts, types, routes, or schemas.

## 9. Data Model / Persistence Changes

Describe schema changes, migrations, data compatibility, backfill, and rollback strategy. Write "None" if not applicable.

## 10. Security, Privacy, and Abuse Considerations

Include auth/authz, validation, secrets, injection, data exposure, auditability, and threat scenarios.

## 11. Performance, Scalability, and Reliability Considerations

Include expected bottlenecks, concurrency concerns, caching, resource usage, failure modes, retries, and degradation behavior.

## 12. Implementation Steps

Each step must be concrete and ordered. For each behavior-changing slice, put agreed tests and their baseline run before production changes, followed by implementation, focused verification, and refactoring. Link acceptance IDs. Record progress as a checklist. Suggest a model tier per step from its hardest decision: `deep` for security, data, contract, or concurrency decisions; `balanced` for routine slices with agreed tests; `fast` for mechanical follow-ups. Tiers are hints for whoever executes; they never relax verification.

1. <Step name>
   - Change:
   - Files/modules likely affected:
   - Notes:
   - Verification:
   - Suggested tier: fast / balanced / deep, with the reason (see `model-routing`)

2. <Step name>
   - Change:
   - Files/modules likely affected:
   - Notes:
   - Verification:
   - Suggested tier:

## 13. Testing Strategy

Include unit, integration, end-to-end, regression, contract, migration, performance, and security tests as applicable. Use only levels relevant to the change.

| ID | Setup / action | Observable expected result | Level / file | Command and directory | Pre-change expectation |
|---|---|---|---|---|---|
| AC-01 | ... | ... | ... | ... | Fails for missing behavior, or passes for characterization |

Test agreement: proposed / agreed / changes requested. Record the user's actual agreement or link to the relevant issue discussion; never invent it.

List harness prerequisites, baseline failures, manual checks, and deferred checks with reasons. Define what evidence completes each criterion. Material acceptance changes during execution require renewed agreement; extra tests that preserve the agreed behavior do not.

## 14. Rollout / Migration Plan

Include feature flags, phased rollout, backward compatibility, operational checks, rollback, and monitoring.

## 15. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---:|---:|---|
| ... | ... | ... | ... |

## 16. Done Criteria

- ...

## 17. Review Checklist

- [ ] Requirements are explicit
- [ ] Non-goals are explicit
- [ ] Existing code conventions were checked
- [ ] Alternatives were considered
- [ ] Security implications were reviewed
- [ ] Scalability and reliability implications were reviewed
- [ ] Testing strategy is complete
- [ ] Observable acceptance scenarios were discussed and agreed with the user
- [ ] Tests and baseline checks precede production changes in each applicable slice
- [ ] Rollout and rollback are defined
- [ ] Implementation steps are ordered and concrete
- [ ] Each step has a suggested model tier with a reason
- [ ] Docs impact is listed, or "None" for a light plan

## 18. Docs Impact

Forecast of the durable documents this change will touch. Close-out reconciles it
with what was built. Write "None" for a light plan.

- Architecture: <document under docs/architecture/ and the section that changes, or "None">
- ADR candidates: <decision>; rejected alternative: <alternative and why>. List only
  decisions that are hard to reverse, surprising without context, and a real
  trade-off (see `adr`). Usually none.
- Behaviour or contract changes: <change>; tests in <file>
- Other docs: <README, runbooks, guides, or "None">

## 19. As-built

Not started. `plan-validation` writes this at close-out: deviations from the plan
with their reasons, the Docs impact reconciliation, and a link to the validation record.

## 20. Handoff Prompt for Implementation Agent

Copy/paste this prompt into a coding agent:

```text
Implement the plan in docs/plans/<file>.md.

Constraints:
- Stay within the scope of the plan.
- Do not introduce new dependencies unless the plan explicitly allows it.
- Preserve existing public behavior unless the plan explicitly changes it.
- Follow existing project conventions.
- Implement the agreed tests first and run them before production changes.
- Use plan-execution if available; otherwise follow the test-first sequence in this plan.
- Record focused check results and finish with required validation against acceptance IDs.
- Update the docs listed in Docs Impact.
- If implementation reality differs from the plan, stop and update the plan or ask for approval before changing scope.

Relevant files/modules:
- ...

Expected verification commands:
- ...
```
````
