# Research → Plan → Annotate → Implement

How to run one feature through the catalog's workflow skills. The workflow follows
Boris Tane's [How I use Claude Code](https://boristane.com/blog/how-i-use-claude-code/)
(read 2026-10-24). Its core rule: **no code until you have reviewed and approved a
written plan.** The `core` pack provides one skill per phase, and the `review` pack
adds independent reviewers.

| Phase | Skill / agent | Writes |
|---|---|---|
| Research | `codebase-research`, `external-research` | `docs/research/<task>-codebase.md`, `docs/research/<topic>-external.md` |
| Plan + annotate | `principal-engineer-planner` | `docs/plans/<feature>.md` |
| Implement | `plan-execution` | code and tests; ticks steps in the plan |
| Validate | `plan-validation` | evidence in the plan or `docs/validation/<task>.md` |
| Review | `pr-walkthrough`; agents `security-practices`, `system-design-scalability`, `performance-scalability`, `readability-maintainability` | findings |
| Helpers | `scout`, `check-runner`, `model-routing` | search results and check output, tier changes |

Prompts below are examples. The skill names in them make the skills trigger
reliably.

## Setup (once per task)

1. **Open the session from the repository**, not from a parent workspace. Create
   the issue and branch first.
2. **Pick the model.** Plan with the strongest model, for example Opus, or Claude
   Code's `opusplan` alias (Opus while planning, Sonnet while executing). Keep
   research, planning, and implementation in one session, so that the context
   built during research carries into the later phases.

## Phase 1: Research

3. **Research the code deeply.**

   > Use codebase-research. Read `<folder or subsystem>` deeply and in great detail:
   > how it works, its specifics, its edge cases. Write the report. Don't change code.

   Words like "deeply" and "in great detail" are there on purpose: they stop the
   agent from skimming signatures.
4. **Research outside the repository if needed** (a library, a cloud service, a pattern):

   > Use external-research on `<question>`.

   Add "use programming-kb" to search the local knowledge base too. That skill
   runs only when you name it, unless the repository sets
   `"invocation": {"programming-kb": "auto"}`.
5. **Read and correct the report.** This is the most important review: a wrong
   research report leads to a wrong plan.

## Phase 2: Plan

6. **Ask for the plan.**

   > Use principal-engineer-planner to write a detailed plan for `<feature>`, based
   > on the research doc. Read the source files before suggesting changes. Don't
   > implement yet.

   The plan covers requirements, alternatives and trade-offs, risks, agreed
   acceptance tests, ordered steps with a suggested model tier for each, and rollout.
   If you have a reference implementation, from your code or from open source,
   paste it in or give its path.

## The annotation cycle

7. **Annotate the plan in your editor.** Write notes directly into
   `docs/plans/<feature>.md`, next to the part they concern. Use them to correct
   assumptions, reject approaches, add business constraints, cut scope ("remove
   the export feature"), and protect interfaces.
8. **Send the agent back to the document.**

   > I added notes to the plan. Address all of them and update the document. Don't
   > implement yet.

   The planner revises the whole plan coherently instead of appending drafts, and
   lists any open questions.
9. **Repeat steps 7–8** (typically one to six rounds) until you have nothing left to change.
10. **Make the steps granular.** If needed:

    > Turn the step list into a granular todo checklist. Don't implement yet.

**Guided review instead of, or after, annotating.** When you want the planner to
lead, ask:

> Use principal-engineer-planner to review `docs/plans/<feature>.md` with me. Ask
> one question at a time.

It shows `Question M/N — <topic>` with context, tradeoffs, and a recommendation,
challenges assumptions and failure modes, and skips anything the repository already
answers. After each decision it updates the plan. It tracks the queue, decisions,
and deferred questions in `docs/plans/<feature>-review.md`, so "continue the plan
review" resumes in a new session. It never starts implementation.

Steer through the document, not through chat. The plan is the shared state that
survives context compaction and goes into the PR.

## Phase 3: Implement

11. **Authorize implementation.**

    > Implement `docs/plans/<feature>.md` with plan-execution. Implement it all.
    > Mark each step done in the plan as you go. Don't stop until every step is
    > done. Run typecheck and tests continuously. No unnecessary comments.

    That message is the authorization. `plan-execution` does not treat an
    "approved" label in the file as permission by itself. It works test-first,
    against the acceptance tests agreed in the plan.
12. **Keep corrections short:** "you didn't implement `X`", "match the existing
    users table", or a screenshot. The design decisions were already made in the
    plan, so implementation should be mechanical.
13. **Revert instead of patching a wrong direction.** Discard the changes with
    `git restore`/`git reset`, fix the plan, and repeat step 11. Patching a flawed
    approach costs more than restarting from a corrected plan.

## Beyond the article

14. **Validate.**

    > Use plan-validation against the plan.

    It checks the result against the acceptance tests and repository checks, and
    records the evidence and gaps.
15. **Review.** To understand the change and review it together, walk through it:

    > Use pr-walkthrough on this branch.

    It starts with an overview and a topic list, then goes through `Topic M/N`, one
    topic at a time. Each topic has a plain-language explanation, `path:line`
    references, short snippets, and tagged findings. For a one-shot specialist
    check of changes that touch security, data, contracts, or performance, run the
    matching `review` agents instead, or from inside the walkthrough. Agents are
    rendered with `enforce` routing, so each runs on its own tier's model.
16. **Ship small.** Commit the research, the plan, and the code in one small PR,
    so the reasoning stays with the change.

Along the way, delegate broad searches to `scout` and noisy test or lint runs to
`check-runner`, both `fast` agents, to keep the expensive session's context clean.
`model-routing` decides when to escalate (repeated failure without new evidence,
a new security or data concern) and caps escalation at once per step.

## Differences from the article

- **No built-in plan mode.** The article prefers markdown plan files to Claude
  Code's plan mode. `docs/plans/` serves that purpose and works in every rendered tool.
- **Tests come from the plan.** The article implements, then typechecks. Here,
  acceptance tests are agreed during planning, and implementation is test-first.
- **Independent validation and review.** The article reviews by hand. Here,
  `plan-validation` and the review agents add a separate check before the PR.
