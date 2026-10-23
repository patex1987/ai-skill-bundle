---
name: plan-validation
description: Validate an implementation against the agreed plan, acceptance scenarios, and repository checks, recording evidence and remaining gaps. Use for final verification or reviewing whether a planned change is complete.
license: MIT-0
metadata:
  routing-tier: balanced
  routing-effort: high
---

# Plan Validation

Assess the actual implementation against the agreed intent. A passing suite is evidence only for the behavior it exercises.

## Build the evidence map

Read repository instructions, the issue, the agreed plan and test scenarios, current diff, and execution results. Identify which code revision and relevant uncommitted changes were checked. Reconcile plan changes with actual user decisions; do not treat unchecked annotations or an agent-written approval label as acceptance.

For each acceptance scenario, map the required behavior to the relevant implementation, test or inspection, and observed result. Inspect tests for meaningful assertions, boundary realism, and uncovered failure modes. Separate test-first evidence reported by execution from evidence you have verified; if the baseline was not captured, do not invent it.

Review the diff for scope drift, compatibility, and risks relevant to this change. Validate risky slices in a context independent of the one that implemented them, at a tier at least as capable as the executor's; record which slices were validated that way. Validation may discover missing tests; adding them now does not retroactively establish a test-first implementation.

## Verify proportionally

Run required repository checks and focused checks missing from the evidence. Reuse trustworthy results for the same code/environment where appropriate; rerun when code changed, evidence is incomplete, or a failure or unresolved risk justifies it. Keep ordinary verification offline when the repository requires it. Live integration checks, deployments, and publication need their existing authorization.

Record exact working directory, command or manual procedure, result, and relevant limitations. Distinguish pass, fail, blocked, and not run. Build/type/lint checks do not replace behavioral verification. If a fix is authorized, return the affected slice to execution and revalidate it; never alter expectations merely to make validation pass.

## Deliver the verdict

Write results into the established plan/log or `docs/validation/<task>.md`. Include:

- Plan and code revision reviewed, with relevant working-tree state.
- Acceptance matrix: scenario ID, evidence, result, and remaining gap.
- Required check results and pre-existing failures distinguished from introduced failures.
- Findings with severity, file/symbol evidence, user impact, and next action.
- Any unverified rollout, runtime, performance, or external-service assumptions relevant to the change.
- Verdict: **verified**, **incomplete**, or **blocked**, with the specific reason.

Use verified only when agreed acceptance and required checks are satisfied. A result scoped to local checks does not establish deployment success. Update task completion accurately and report material limitations in the final handoff. Validation itself does not authorize pushing, merging, or deploying.
