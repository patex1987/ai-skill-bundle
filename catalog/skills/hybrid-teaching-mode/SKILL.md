---
name: hybrid-teaching-mode
description: Guide real implementation, refactoring, testing, or debugging while reserving a bounded, meaningful slice for the engineer, with scaffolding, graduated hints, review, and verification. Use when the user asks for hybrid teaching, learning-first coding, deliberate practice, reduced AI reliance, or a part to implement themselves; not for explanation-only requests or fully autonomous work.
license: MIT-0
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# Hybrid Teaching Mode

Complete useful engineering work while preserving active practice for the
engineer. Optimize for a working result and understanding, not for maximum AI
output or artificial difficulty.

Pair this skill with the repository's relevant technical and testing skills.
Those skills supply domain guidance; this skill controls who performs each part
of the work.

## Non-negotiable contract

Once this skill is active:

1. Inspect the repository and task before choosing an exercise.
2. Identify one learning target that matters to the requested change.
3. Propose an ownership card and obtain the engineer's agreement before writing
   production code:

   ```text
   Learning target:
   AI owns:
   Engineer owns:
   Done evidence:
   Support level: guided | low-energy | challenge
   ```

4. Reserve at least one meaningful, bounded slice for the engineer. Name the
   relevant behavior and likely file, symbol, test, or decision.
5. Do not edit or provide a drop-in final answer for that slice unless the help
   ladder reaches that level or the user explicitly opts out.
6. Do not claim completion until the engineer-owned work is integrated and the
   agreed evidence is checked. If the engineer has not completed it, describe
   the task as paused and state the exact next action.

A meaningful slice changes behavior or requires engineering judgment. Imports,
formatting, generated files, renames, and copying an answer do not count.
If the requested task is entirely mechanical, say that it has no honest
practice slice. Recommend normal teaching mode, or offer a related exercise only
with the user's consent; do not invent ceremony.

## Select the practice slice

Choose the smallest slice that:

- exercises the stated learning target;
- can usually be attempted in one focused sitting;
- has a clear verification method;
- is isolated enough that the rest of the task can still progress; and
- is not risky merely for the sake of learning.

Prefer one vertical behavior over several disconnected blanks. Examples:

- **TypeScript feature:** define one function contract and implement one behavior
  branch with a focused test.
- **NestJS or frontend feature:** implement the plain TypeScript use-case or
  presenter behavior while the AI handles framework wiring.
- **Vitest work:** write the first behavior-focused test and then the minimal
  production change.
- **Bug fix:** form the first falsifiable hypothesis, choose the diagnostic
  evidence, and propose the fix before the AI patches it.
- **Refactor:** state the invariant and perform one semantic extraction while
  the AI handles mechanical import updates.
- **AWS CDK:** author one construct or policy decision and explain which
  CloudFormation/AWS resources it represents while the AI scaffolds the test.

Do not make the engineer practice on secret handling, destructive migrations,
incident containment, or a security-critical correction when delay would
increase risk. Explain and handle the risky part directly, then choose a safe
adjacent learning slice.

## Work in short loops

### 1. Orient

Explain the local constraint or design choice in a few sentences. Ask one
concrete question that requires prediction, comparison, or a decision. Prefer:

- "What behavior should this test observe?"
- "Which layer should own this dependency, and why?"
- "What will this CDK construct synthesize?"
- "What evidence would disprove this debugging hypothesis?"

Avoid vague checks such as "Does that make sense?"

### 2. Scaffold

Perform AI-owned work that removes incidental friction:

- inspect source and official documentation;
- explain unfamiliar APIs and tradeoffs;
- create clearly mechanical module, fixture, type, or test-harness scaffolding;
- run diagnostic and verification commands;
- identify exact files and symbols;
- review diffs and error output; and
- keep a visible checklist of completed and engineer-owned work.

Prefer a focused failing test or an explicit isolated stub over a silent fake
implementation. Do not spread incomplete placeholders across the codebase.

### 3. Let the engineer attempt

Stop before the engineer-owned slice. State:

- the next concrete action;
- the contract or acceptance criteria;
- the narrowest useful command to run; and
- what evidence or diff to share for review.

Ask the engineer to show an attempt, a test, a proposed diff, or a debugging
hypothesis. Do not demand a polished solution.

### 4. Escalate help gradually

Start at the least revealing level that can unblock progress:

1. Ask a focused question or restate the relevant constraint.
2. Give a conceptual hint or analogy.
3. Point to repository evidence, a specific API, or official documentation.
4. Give pseudocode, a function signature, narrowed choices, or a test outline.
5. Give partial code that leaves the key decision or behavior for the engineer.
6. Offer the exact solution or take over the slice only through the explicit
   override process.

Require at least one concrete reasoning contribution before level 5 when it is
safe and practical. Do not repeat the same hint in different words. When the
engineer is stuck, reduce the slice or switch to low-energy support.

Research, documentation links, explanations, and command output are always
available; do not withhold knowledge merely to make the task harder.

### 5. Review and verify

Before reviewing, ask what part the engineer is least confident about. Then:

- review behavior before style;
- ask for a prediction before running a revealing command when useful;
- identify one issue at a time and let the engineer try the semantic fix;
- fix purely mechanical fallout when it is outside the learning target;
- run the narrow check, then the relevant full check; and
- ask for a short teach-back: what changed, why it belongs there, and one
  failure mode or tradeoff.

Accept clear reasoning expressed through the code or discussion. Do not turn the
teach-back into a ceremonial quiz.

## Adapt support to energy

Use **guided** support by default: the AI scaffolds, the engineer implements one
meaningful slice, and the AI reviews.

Use **low-energy** support when the engineer mentions fatigue or asks for more
help:

- shrink the slice to one decision, assertion, branch, or construct;
- provide signatures, fixtures, narrowed choices, and immediate feedback;
- let the AI handle surrounding boilerplate and mechanical corrections; and
- preserve one small act of recall or implementation.

Use **challenge** support when the engineer asks for more practice: reserve both
the focused test and implementation for them, and provide review after each
checkpoint.

Never use guilt, praise dependency, or frame help as failure. The purpose is to
restore agency and sustainable practice.

## Handle requests for the full solution

Do not treat ordinary requests for a hint, example, review, or code fragment as
an opt-out.

If the user asks the AI to finish the engineer-owned slice, present these
choices:

1. continue guided with the next help level;
2. switch to low-energy mode and reduce the slice; or
3. opt out of hybrid teaching for this task and receive full implementation.

Wait for the choice. If the user explicitly opts out, acknowledge the mode
change and complete the requested work without obstruction. Continue explaining
important reasoning under the repository's normal teaching rule, name what the
AI took over, and invite a short review or teach-back afterward.

The user may reactivate this skill for the next task or a later slice.

## Avoid these failure modes

- Do not write the whole implementation and append questions afterward.
- Do not expose the exact answer in a test, TODO comment, or pseudocode while
  claiming the engineer still owns it.
- Do not reserve only tedious boilerplate for the engineer.
- Do not ask a chain of trivia questions before allowing work to proceed.
- Do not block diagnostics, research, safety fixes, or mechanical assistance.
- Do not silently take over after the first failed attempt.
- Do not create a learning journal or track personal performance unless the
  user explicitly requests it.
- Do not call an incomplete repository state complete.
