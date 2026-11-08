---
name: plan-sweep
description: Sweep finished plans. Verify each done or abandoned plan's as-built claims against the code, propose where durable content should go (architecture docs, ADRs, lessons, or nowhere), apply only the edits the author approves, and delete only the plan and working files the author approves one by one. Run only when the author asks for a plan sweep.
license: MIT-0
metadata:
  routing-tier: balanced
  routing-effort: medium
  invocation: explicit
  tags: [planning, documentation, cleanup]
---

# Plan Sweep

Plans, research notes, review records, and validation records are working
documents. Durable knowledge lives in `docs/architecture/` and `docs/adr/`. A sweep
moves what is worth keeping into those documents, then removes what the author no
longer needs. The author decides every promotion and every deletion.

## 1. Select

- Sweep plans in `docs/plans/` with `Status: done` or `Status: abandoned`, and any
  plan the author names.
- List plans with no `Status:` separately and do not sweep them unless the author
  names them. Never sweep `draft`, `agreed`, or `in-progress` plans unless named,
  and warn before doing so.
- For each plan, collect the files it links: review record, research reports, and
  validation record. Note any file that another, unswept plan also links. Such a
  file is kept.

## 2. Verify before promoting

Do not trust the plan. For each As-built claim, Docs impact item, and ADR candidate,
check the current code, tests, and docs, and cite `path:line`. Mark each one
**verified**, **contradicted**, or **not checkable**. Report contradicted claims and
never promote them. Promote a not-checkable claim only if the author confirms it.

## 3. Propose

Send one proposal per plan, and make no changes yet:

- **Promotions:** for each piece of content, its destination:
  - architecture: the document and section under `docs/architecture/` (see
    [references/architecture-docs.md](references/architecture-docs.md));
  - ADR: draft it with the `adr` skill in `extract-from-plan` mode, which applies
    its significance test;
  - lesson: offer the destinations (a repository overlay, an agent instruction
    rule, a lint or check, a hook, or a user memory where the tool has one) and let
    the author choose;
  - nowhere: say why.
- **Deletions:** list every file to delete on its own line, with its full path and
  whether git tracks it. Say plainly that an untracked file cannot be recovered
  after deletion, and suggest committing it first if the author might want it back.

Ask the author to approve each promotion and each deletion.

## 4. Apply only what was approved

- Approval must name the item, or clearly cover a list the same message showed in
  full ("delete all four files listed above"). Silence, "looks good", "clean it up",
  or "I trust you" is not approval to delete. Ask again, listing the files.
- Apply the approved edits first, then the approved deletions. Delete tracked files
  with `git rm`, so the deletion is staged with the edits.
- Update "last verified against <commit>" only for the overview sections you
  actually checked.
- Never delete or rewrite content in `docs/architecture/` or `docs/adr/` as part of
  cleanup. Never edit an accepted ADR except through `adr` supersede mode.

## 5. Hand back

The sweep leaves no separate log. Propose one cleanup commit whose message lists
what was promoted where, what was deleted, and what was kept and why. The commit is
the record. Commit only when the author asks. Never push.
