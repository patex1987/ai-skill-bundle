# Walkthrough Record

The record keeps the topic map, position, and findings, so a long walkthrough survives
context compaction and can resume in another session. It is a working file for the
reviewer, not part of the change.

## Location

- Respect an existing convention for review notes.
- Otherwise use `docs/reviews/<target>-walkthrough.md`, where `<target>` is
  `pr-<number>`, the branch name with `/` replaced by `-`, or `working-tree`.
- If that path is tracked or holds something else, pick a clearly named variant and
  tell the user.
- Tell the user once that the file is untracked, and that they choose whether to
  commit, share, or delete it.

Create it when the topic order is agreed. Update it whenever a topic is done, a
finding is routed, the topic list changes, or a fix lands. Do not wait until the end.

## Template

```md
# Walkthrough: <PR title or target>

- Target: <PR #, URL | branch vs base | range | working tree>
- Mode: review | explain
- Pinned base: <sha>   Head at start: <sha>
- Started: YYYY-MM-DD
- Position: Topic M/N — <name>
- Status: in progress | complete

## Topics

| # | Topic | Files | Status |
|---|---|---|---|
| 1 | Coupon contract | src/coupons/coupon.ts | done |
| 2 | Total calculation | src/checkout/total.ts, test/total.test.ts | current |
| 3 | Checkout wiring | src/http/routes.ts, src/coupons/repository.ts | pending |

Statuses: pending, current, done, skipped (with reason).

## Findings

### Open
- [ ] **Fixed coupon can make the total negative** (Topic 2, blocking).
      Evidence: `src/checkout/total.ts:25`. Suggestion: clamp at zero; add a test.

### Follow-up

### Questions
- **Can coupons stack?** (Topic 3, question for product owner)

### Dropped
- Topic 1, point 2: naming nit; the convention allows it.

### Done
- (`<sha>` or `uncommitted`) **<fix>** — <check that proved it>.

## Topic changes

- YYYY-MM-DD: split "Checkout" into Topics 3 and 4 (wiring and error handling).

## Not verified

- <claims or behavior you could not check, and why>
```

Number findings by topic in chat (Topic 2, finding 1). In the record, keep them under
their route with the topic reference.

## Resuming

When a record for the same target exists and is not complete:

1. Read it, then compare current `HEAD` and the changed paths with the pinned values.
2. If history was rewritten or new commits arrived, say so. Ask whether to re-pin.
   On re-pin, record the new values and mark topics whose files changed as pending again.
3. Add topics for newly changed files that no topic covers, and say how `N` changed.
4. Keep earlier routing decisions.
5. Send a three-line status (position, open findings, what changed), then resume at
   the current topic with its full topic message.
