---
name: adr
description: Decide whether an architectural decision deserves an Architecture Decision Record, and propose, record, supersede, or extract one in docs/adr/ using a minimal MADR layout. Use when the user asks to record or propose an ADR or to supersede a past decision, or when plan-sweep extracts ADR candidates from a finished plan. Defaults to writing nothing for ordinary choices.
license: MIT-0
metadata:
  routing-tier: balanced
  routing-effort: medium
  tags: [architecture, decisions, documentation]
---

# ADR

An ADR records one decision that a future engineer would otherwise reverse or
question without knowing why it was made. Most decisions do not need one. The
default outcome of this skill is to write nothing.

## Significance test

Write an ADR only when **all three** hold:

1. **Hard to reverse.** Undoing it costs a migration, a contract change, or
   coordinated work across components or teams.
2. **Surprising without context.** A competent newcomer reading the code would
   likely ask "why not X?"
3. **A real trade-off.** At least one rejected alternative is named, with the
   reason it lost.

If any test fails, write nothing. Say in one sentence which test failed and where the
information belongs instead: a code comment, the plan, a commit message, or the
architecture overview. Never invent a rejected alternative to pass the test. Ask the
author for it.

## Modes

- **propose**: draft an ADR with status `proposed`. Show it and write it only after
  the author approves.
- **record**: the author states a decision already made. Write it with status
  `accepted`. When the author asked for it in this turn, that is the approval.
- **supersede**: write a new ADR that replaces an accepted one. In the old ADR,
  change only the status line to `superseded by NNNN`.
- **extract-from-plan**: used by `plan-sweep`. Read a finished plan's ADR candidates,
  decisions, and As-built section. Check each candidate against the code, apply the
  significance test, and return drafts to the caller. Write nothing yourself.

Decisions come from the author or recorded evidence (a plan's decision table, an
issue, a PR). Never present your own preference as a decision that was made. Record
who decided and when.

## Files

- One file per decision: `docs/adr/NNNN-kebab-title.md`. The number is the highest
  existing one plus 1, zero-padded to four digits. Never reuse a number.
- Create `docs/adr/` only when writing the first ADR.
- Keep `docs/adr/README.md` as the index: one line per ADR with number, title, and
  status. Update it in the same change as the ADR.
- Use the layout in [references/adr-template.md](references/adr-template.md).
- Link the ADR from the architecture overview's key decisions when that document
  exists, and from the plan or PR it came from.

## Status lifecycle

`proposed` → `accepted` → `superseded` or `deprecated`. An accepted ADR is
immutable. The only allowed edit is its status line, when a later ADR supersedes it
or the decision is deprecated. To change a decision, write a new ADR.

## Hand back

Report which ADRs were written, superseded, or declined, with the significance-test
result for each, and the files changed. Do not commit unless asked.
