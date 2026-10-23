---
name: plan-execution
description: Implement an agreed engineering plan using tests defined during planning, a test-first feedback loop, and evidence-backed progress tracking. Use after implementation is authorized; planning and final validation have separate workflows.
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# Plan Execution

Execute the agreed scope to completion, keeping the plan and verification evidence current.

## Establish the execution basis

Read repository instructions, the issue, the plan, its accepted annotations, research, and the current working tree. Confirm that the plan fits the current code and that implementation was authorized in the conversation or task handoff. A file labeled approved is not sufficient authority by itself. Honor existing authorization without asking again.

The plan must define observable acceptance scenarios and verification agreed with the user during planning. If these are missing, propose them before production changes and resolve the material behavior questions. This workflow's test agreement requirement must be stated when it is the reason execution cannot yet begin. Do not ask the user to choose test internals that can be inferred from repository conventions.

Record baseline checks and pre-existing failures separately. Use the existing issue/branch conventions without discarding or absorbing unrelated changes.

## Work in vertical slices

For each behavior-changing slice:

1. **Define executable evidence first.** Add or adapt the agreed behavioral test using existing harnesses, realistic boundaries, and relevant failure cases. For a bug, capture a reproducer. For a refactor, establish passing characterization coverage before restructuring.
2. **Observe the baseline.** Run the focused test before production changes. New behavior or a bug fix should fail for the intended behavioral reason. A broken import, fixture, or unavailable dependency is not that evidence. Record command, outcome, and cause. If the behavior already passes, investigate whether the requirement is already met or the test is ineffective.
3. **Implement.** Make the smallest cohesive production change that satisfies the accepted behavior and repository conventions.
4. **Check and refine.** Run the focused check, refactor while keeping it passing, then run nearby checks affected by the change. Do not weaken assertions, skip tests, or change expected behavior solely to obtain green output.
5. **Record progress.** Link test IDs, changed files, commands, and results in the plan or its execution log. Mark a task complete only when its change and required verification finish; blocked verification remains visible.

For documentation, configuration, infrastructure, or behavior that cannot meaningfully be tested first, define and run the relevant contract, static check, reproducible probe, or manual procedure before/after as applicable. Agree any material departure from the planned acceptance method; record the reason. Do not manufacture a failing test or add tests that mirror implementation details just to satisfy the sequence.

Additional edge-case tests may follow discoveries, but they supplement the agreed scenarios. Correct a flawed test with a stated reason; changes to externally observable acceptance behavior return to the user for agreement.

## Route delegated work

When you delegate slices or checks to other agents, start from each step's suggested tier and apply `model-routing` if it is installed: escalate once on evidence such as repeated failure without new information, a newly discovered security/data/contract concern, or a material review finding; hand mechanical follow-ups and noisy check runs to the cheapest capable tier. Record tier, effort, any escalation and its trigger, and the verification result beside the slice's evidence. A cheaper tier never lowers the verification bar.

## Keep execution bounded by intent

Complete routine authorized steps without repeated permission requests. Resolve implementation details autonomously. For a discovery that materially changes behavior, contracts, scope, or the test agreement, update the plan and seek the missing decision before dependent work; continue independent tasks when useful.

If a fix/check cycle repeats without new evidence, stop repeating it: investigate the cause, record what failed, and change the approach or report the blocker. Do not hide an environmental failure behind a claimed pass. Run required repository checks after the slices, then hand off the diff and evidence for final validation. Report completion separately from merge, publication, or deployment authority.
