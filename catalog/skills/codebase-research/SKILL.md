---
name: codebase-research
description: Investigate an existing subsystem and write an evidence-backed Markdown context document before design, debugging, migration, or implementation. Use for unfamiliar or substantial code paths; implementation is a separate task.
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# Codebase Research

Produce a bounded, checkable account of how the relevant system currently works. Research may write the requested report; it does not authorize product changes.

## Investigation

1. Read applicable repository guidance, inspect working-tree status, and identify the question, subsystem, and exclusions. Use the issue or user request to bound the investigation.
2. Find entry points and a comparable existing implementation. Trace the relevant path through callers, policy, persistence, integrations, and outputs. Read implementations and consumers, not only declarations.
3. Inspect tests, fixtures, dependency versions, configuration, and CI commands. Identify behavior actually covered by tests and claims that remain unverified.
4. Investigate relevant failure paths, state transitions, compatibility boundaries, and concurrency where they affect the question. Follow dependencies only as far as needed to explain behavior.
5. Separate observed facts from inferences, hypotheses, and unknowns. Cite repository-relative paths, symbols, and useful line numbers. Record commands actually executed and their outcomes; discovering a test file does not mean running it.

Use targeted `rg` searches. Avoid generated output, vendor trees, secrets, and broad repository dumps. Read-only commands are the default; a research request does not authorize live integration probes or deployments. Tests can have side effects: inspect commands before running them.

## Report

Respect an established destination or explicit path. Otherwise write `docs/research/<task>-codebase.md`. Keep independent repositories' evidence clearly attributed.

Include:

- Question, scope, date, repository, branch and HEAD, and relevant uncommitted changes observed at research time.
- Current behavior and a concise call/data flow with evidence at each important boundary.
- Invariants, protected interfaces, ownership boundaries, and comparable patterns to reuse.
- Existing test coverage, test harness constraints, and known verification commands with their working directory.
- Findings with evidence; clearly label suspected defects and untested hypotheses.
- Unknowns, contradictions, gaps, and the next observation that would resolve each material uncertainty.
- Implications for planning, with recommendations distinguished from current behavior.

Prefer a focused explanation over a file inventory. Do not claim exhaustive understanding or that every bug has been found. Report sufficient evidence when the scoped questions are answered; identify remaining limits rather than researching indefinitely.

## Handoff

Summarize the important findings and link the report. Invite corrections through annotations without inventing a mandatory approval step. When planning follows, reread relevant source if HEAD or the working tree changed. Do not treat this report as an implementation plan or authorization to code.
