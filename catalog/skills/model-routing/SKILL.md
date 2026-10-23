---
name: model-routing
description: Choose the model tier and reasoning effort for delegated or multi-step work, and escalate or de-escalate during execution. Use when planning delegation to subagents, fanning out parallel work, retrying after failed attempts, or deciding whether a task needs a stronger or cheaper model.
license: MIT-0
metadata:
  routing-tier: balanced
  routing-effort: low
---

# Model Routing

Spend capability where it changes the outcome. A tier is a cost hint for one
unit of delegated work. It is not a judgement of the user or the task's importance.

Routing decides three different things. Keep them apart:

1. **What capability the work needs.** You decide this per task with the rules below.
2. **Which model serves that tier in this tool.** Repository configuration decides this:
   the *Model Routing Tiers* table in the generated project guidance, from
   `.ai/routing.json` and `.ai/bundle.json`. Do not hard-code model names in plans.
3. **Whether the result is acceptable.** An independent check decides this: tests, a
   validator, or the user. A cheaper route is only safe when this check is real.

An explicit user or repository choice of model or effort always wins over these defaults.

## Pick the starting tier

| Tier | Work shape | Typical examples |
|---|---|---|
| `fast` | Well-specified, mechanical, and cheap to verify objectively | Repository search and inventory, summarising logs or diffs, extraction into a fixed format, classification, formatting, renames, running checks and reporting failures |
| `balanced` | Routine engineering with clear acceptance criteria | Implementing an agreed slice, writing tests for agreed scenarios, focused review against a checklist, documentation from known facts |
| `deep` | Ambiguous, high-consequence, or hard to verify | Design and planning, security or authorization changes, data migration, concurrency, public contract changes, root-causing after failed attempts, final validation of risky work |

Decide from the hardest decision inside the unit, not its size. A one-line
change to an authorization check is `deep`. A 500-line generated fixture
rename is `fast`.

Reasoning effort is a separate dial. Raise effort when the work is the right kind
for the tier but needs more careful reasoning: long dependency chains,
many constraints, or subtle edge cases. Raise the tier when the model is missing a
capability: it repeatedly misreads the problem, or the work crosses into a
`deep` category. This is a working heuristic, not a measured rule; record what
you tried.

## Cascade only where checking is cheap

Trying a cheaper tier first and escalating on failure (a cascade) saves cost
only when failure is detected cheaply and reliably: tests, type checks, linters,
schema validation, an exact expected output. When acceptance needs expert judgement
(design quality, security reasoning, migration safety), start at the tier that
can do the work. A cheap draft that a strong model must re-derive costs more
than going straight to the strong model.

## Escalate on evidence

Move one tier up, or raise effort, when any of these appear:

- The same check fails twice without new evidence or a changed hypothesis.
- The worker's result contradicts repository evidence, or it reports low confidence.
- The unit turns out to touch a `deep` category: security, authorization, data,
  public contracts, concurrency, or irreversible operations.
- The scope or blast radius is materially larger than the plan assumed.
- Independent review finds a material defect in the worker's output.

Escalate at most once per unit without new information. If the escalated
attempt also fails, stop. Record what was tried and the evidence, then report
the blocker or return to planning. Repeated retries at any tier multiply cost
without adding knowledge. Bound retries across layers: harness, agent loop, and
your own loop.

## De-escalate when uncertainty is gone

- After a `deep` plan defines concrete slices, agreed tests, and commands,
  execute routine slices at `balanced`.
- Hand mechanical follow-ups (doc sync, renames, formatting, changelog entries,
  re-running checks) to `fast`.
- Use `fast` workers to absorb noisy output: search results, long logs, full
  test runs. Ask for a compact summary so the expensive context stays small.

## Delegate deliberately

Delegation has a fixed cost: writing a self-contained brief, the worker
re-reading context, and reviewing its result. Delegate when a unit is
independent, has a clear output contract, and is large or noisy enough to be
worth isolating. Do small, tightly coupled steps yourself.

A good brief states the goal, the inputs or paths, the constraints and
non-goals, the expected output format, and how the result will be checked.
Prefer parallel `fast` workers for independent read-only fan-out, and avoid
parallel writers on the same files.

For risky units, validate with a different agent or context from the one that
did the work. Use a validator at least as capable as the executor. Validation is
independent evidence, not a second opinion from the same context.

## Record routing decisions

In the plan or execution log, record for each delegated unit: the tier and
effort chosen and why, the model actually used when the tool shows it, any
escalation and its trigger, and the verification result. This lets the team
see where cheaper tiers succeed and adjust the repository's tier mapping
from evidence.

## Tool mechanics

Read [references/tool-mechanics.md](references/tool-mechanics.md) when you need
to set a model or effort for a specific tool (Claude Code, Codex, Cursor, or Gemini
CLI), or to check what those settings actually control.
