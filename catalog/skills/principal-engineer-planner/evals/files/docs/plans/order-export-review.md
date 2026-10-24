# Plan Review: Order Export

- Plan: [order-export.md](order-export.md)
- Research: [order-export-codebase.md](../research/order-export-codebase.md)
- Review status: in progress
- Revision reviewed: working tree, fixture
- Current position: Question 3/6, Q-03 (Failure modes)
- Test agreement: proposed
- Implementation authorization: not given

## Queue

| # | ID | Topic | Question | Status | Depends on |
|---|---|---|---|---|---|
| 1 | Q-01 | Scope | Export all historical orders, or a bounded date range? | decided | |
| 2 | Q-02 | Interfaces | Return `202` with polling, or notify when ready? | decided | |
| 3 | Q-03 | Failure modes | How does the worker stay correct when the queue redelivers a job mid-export? | discussing | |
| 4 | Q-04 | Data | Make paging stable when `createdAt` is not unique? | pending | |
| 5 | Q-05 | Security | Who can use the signed URL, and for how long? | pending | |
| 6 | Q-06 | Acceptance tests | Agree AC-01..AC-03 as revised? | pending | Q-01..Q-05 |

## Decisions

### Q-01 — Export all historical orders, or a bounded date range?

- Decision (user): last 24 months only.
- Rationale: older orders live in an archive store the API does not read.
- Recommendation given: bounded range; accepted with a different window.
- Plan sections updated: 2, 5, 13 (AC-02).

### Q-02 — Return `202` with polling, or notify when ready?

- Decision (user): polling only for now.
- Rationale: notifications are a separate feature.
- Recommendation given: polling; accepted.
- Plan sections updated: 6, 8.

## Deferred

None.

## Unresolved points and assumptions

- Q-03: retrying "from the start" may upload a duplicate or partial object.

## Queue changes

- Removed: maximum rows per export (answered by `config/exports.json`).
