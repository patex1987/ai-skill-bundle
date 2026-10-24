# Interactive Plan Review

Walk the user through an existing plan as a principal engineer and design partner.
The goal is understanding and a better design, reached through conversation: one
material question at a time, each with context, tradeoffs, and a recommendation.

This mode stays in planning. Discussion, decisions, and plan edits never authorize
implementation.

## Contents

- [Start or resume](#start-or-resume)
- [Build the question queue](#build-the-question-queue)
- [Ask one question at a time](#ask-one-question-at-a-time)
- [Progress and status](#progress-and-status)
- [Adapt the queue](#adapt-the-queue)
- [Settle a decision and update the plan](#settle-a-decision-and-update-the-plan)
- [Acceptance tests and authorization](#acceptance-tests-and-authorization)
- [The review record](#the-review-record)
- [Finish the review](#finish-the-review)

## Start or resume

1. Locate the plan. If the user does not name one and several exist under
   `docs/plans/`, ask which one; do not guess.
2. Look for a review record linked from the plan (`Review record:` near the top) or
   at `docs/plans/<plan-name>-review.md`. If one exists and is not complete,
   **resume** from it instead of starting again.
3. Read the whole plan, the research reports it links, and the repository context
   its decisions depend on. Check that cited files and symbols still exist, and
   note when the working tree or HEAD has moved since the plan or record was written.
4. When resuming, reconcile before asking anything: compare the plan with the
   record's decisions and look for new user annotations. Report in a few lines
   where the review stands (position, decided, deferred, what changed) and
   adjust the queue for any plan changes.

## Build the question queue

Draft the queue only after reading. A question qualifies when its answer
materially changes the design, the risk, the acceptance criteria, or the rollout.

- **Do not queue what the repository already answers.** If code, tests, configuration,
  or docs settle it, record the answer in the plan as evidence (file and symbol)
  and move on. Mention briefly that you resolved it from evidence.
- **Challenge, not just clarify.** Include questions that test weak assumptions, unstated
  constraints, and operational failure modes: partial failure, retries and
  idempotency, concurrency, data loss and recovery, degraded dependencies, rollback,
  observability, abuse, and limits.
- **Group by topic** (for example Scope, Interfaces and contracts, Data and
  consistency, Failure modes and operations, Security, Rollout, Acceptance tests).
  Order topics and questions so that decisions others depend on come first. Scope
  and goals usually come before design details, and design before tests.
- **One decision per question.** Split compound questions; merge duplicates.
- Keep the queue to material questions. If it exceeds about fifteen, say so,
  propose which low-leverage questions to defer, and let the user choose.

Give every question a stable ID (`Q-01`, `Q-02`, …) that never changes or gets
reused, even when the queue is reordered, merged, or trimmed.

Show the queue once at the start: topics, one-line questions, and the total. Then
begin with the first question.

## Ask one question at a time

Each question message follows this shape:

```text
Question M/N — <topic>  (Q-07)

Context: what the plan says now, and the evidence behind it (files, research notes).
Decision: the one thing to decide, phrased so it can be answered.
Options and tradeoffs: two or three realistic options, with consequences, costs,
  and how each fails in operation.
Recommendation: what you would choose and why, and how confident you are.
Then the question itself.
```

- Ask exactly one question, then wait. Do not bundle the next question into the
  same message.
- Keep context sufficient to decide without rereading the plan, and no longer.
- Push back when the user's answer rests on an assumption the evidence contradicts,
  or leaves a failure mode unhandled. Say what would change your recommendation.
- Welcome brainstorming and follow-ups. Explore them under the current question
  until the user settles it, defers it, or the discussion shows it is really a
  different decision.
- When you lack evidence, say so and offer to inspect the code before the user
  decides. Do not invent facts.

## Progress and status

`M` is the position of the current question in the queue's current order, and
`N` is the current number of questions (pending, discussing, decided, and deferred;
removed and merged questions do not count).

- Clarifications and follow-ups within the current question do not advance `M`.
- A distinct new decision that surfaces becomes a new queue entry, not a
  sub-thread.
- When `N` changes, say why in one line before or after the question, for example:
  `N is now 11: added Q-12 (retry budget) from your answer; merged Q-05 into Q-04.`

Each question has exactly one status:

| Status | Meaning |
|---|---|
| `pending` | queued, not yet discussed |
| `discussing` | the current question |
| `decided` | the user settled it explicitly |
| `deferred` | set aside on purpose; still visible and **not** resolved |

A question becomes `decided` only on an explicit user decision, including an
explicit acceptance of your recommendation ("go with your recommendation"). An
ambiguous reply ("hm, ok", "next") is not a decision: confirm in one line, or
mark the question `deferred` if the user wants to move on. Silence never decides.

## Adapt the queue

Revisit the queue after every settled or deferred question:

- **Add** questions the discussion revealed. Place each by dependency, not at the
  end by default.
- **Remove** questions that a decision made moot, and **merge** questions that
  turned out to be one decision. Record the reason; keep the IDs in the log.
- Move a deferred question back into discussion when a later decision depends on
  it, and say so.

Announce each change briefly. Record every change in the review record.

## Settle a decision and update the plan

After each decision, in the same turn:

1. Update every affected plan section coherently: design, alternatives (with the
   decision), interfaces, data, security, reliability, steps and their tiers,
   risks, rollout, and acceptance scenarios. Rewrite superseded text instead of
   appending contradictions.
2. Mark where each statement comes from, so a reader can tell them apart:
   - **Decision (user, Q-07):** settled by the user.
   - **Recommendation:** your proposal, not yet decided by the user.
   - **Assumption:** believed but unconfirmed; say what would confirm it.
   - **Evidence:** established from the repository or research, with a reference.
   Keep a `### Decisions` list in the plan's Requirements and Assumptions section
   that links each decision to its question ID in the review record.
3. Update the review record (below).
4. Summarize the plan change in two or three lines, then ask the next question.

Do not edit code, tests, or configuration outside `docs/plans/` (and the plan's
own linked documents) during this mode.

## Acceptance tests and authorization

Track these as two separate states, both in the plan and in the record:

- **Test agreement:** `proposed`, `agreed`, or `changes requested`, per scenario
  where it differs. Agreement requires the user's explicit agreement to the
  scenarios as written. A decision that changes a scenario's observable behavior
  returns that scenario to `proposed`. Put the agreement on scenarios into the queue
  as its own question (topic Acceptance tests) instead of inferring it.
- **Implementation authorization:** `not given` or `given (scope, date)`. Only an
  explicit user instruction to implement grants it. Settled decisions, an agreed
  test list, a complete review, and a status written by an agent do not.

If the user authorizes implementation mid-review, record it, ask whether open
questions should be deferred or finished first, and hand off per section 8 of
the skill. Do not start coding inside the review.

## The review record

Persist state so another session can resume exactly. Default path:
`docs/plans/<plan-name>-review.md`. Respect an existing location or convention.
Add `Review record: <relative link>` near the top of the plan.

Write the record when the queue is first built, and update it after every status
change, queue change, decision, and plan edit. Do not batch updates until the end.

```md
# Plan Review: <Plan Name>

- Plan: [<plan-name>.md](<plan-name>.md)
- Research: <links>
- Review status: in progress | complete
- Revision reviewed: <commit or "working tree, YYYY-MM-DD">
- Current position: Question M/N, Q-07 (<topic>)
- Test agreement: proposed | agreed | changes requested (details in plan section 13)
- Implementation authorization: not given | given (<scope>, <date>, <quote or link>)

## Queue

| # | ID | Topic | Question | Status | Depends on |
|---|---|---|---|---|---|
| 1 | Q-01 | Scope | Include historical data in the export? | decided | |
| 2 | Q-04 | Data | Snapshot or live read during export? | discussing | Q-01 |
| 3 | Q-06 | Operations | Who is alerted when an export fails? | deferred | |

## Decisions

### Q-01 — Include historical data in the export?

- Decision (user): Only the last 90 days.
- Rationale: <user's reasons and the tradeoffs accepted>.
- Recommendation given: <yours, and whether the user accepted, modified, or rejected it>.
- Plan sections updated: 2, 6, 13 (AC-03).
- Date: YYYY-MM-DD

## Deferred

- Q-06: <why deferred, what it blocks, when to revisit>

## Unresolved points and assumptions

- <open sub-points from discussions, assumptions awaiting confirmation>

## Queue changes

- YYYY-MM-DD: Added Q-07 (from discussion of Q-04). Merged Q-05 into Q-04 (same
  decision). Removed Q-03 (answered by `src/export/limits.ts`).
```

The `#` column is the display order `M`; IDs stay stable.

## Finish the review

The review is complete when no question is `pending` or `discussing`. Deferred
questions may remain. Then:

1. Run the plan validation checklist (section 7 of the skill) over the updated plan.
2. Set the record's status to `complete` and keep it linked from the plan.
3. Summarize for the user:
   - decisions, separating the user's own decisions from accepted recommendations
   - deferred questions, with what each one blocks
   - open assumptions and unresolved points
   - test agreement state, per scenario where mixed
   - implementation authorization state
   - readiness: **ready**, **ready with named risks** (deferred items do not block
     the first slices), or **not ready** (say what blocks it)
   - the next prompt to move forward, for example finishing the deferred
     questions or the implementation handoff prompt
