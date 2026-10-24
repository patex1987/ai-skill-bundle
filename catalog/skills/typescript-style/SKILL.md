---
name: typescript-style
description: Write and review TypeScript that is easy to read, covering the layout that formatters and linters enforce, readable statement structure, idiomatic language choices, and TSDoc comments that explain behaviour rather than repeat types. Use whenever writing or editing TypeScript, when generated code comes out dense, unformatted, or undocumented, when adding or reviewing doc comments, or when setting up formatter and lint rules for code style. For type design and runtime validation, use the typescript skill.
license: MIT-0
metadata:
  routing-tier: balanced
  routing-effort: medium
  tags: [typescript, style, documentation, formatting]
---

# TypeScript Style

Code is read far more often than it is written. Write TypeScript that the next
engineer can scan quickly: the shape of each file is visible at a glance, each
function reads top to bottom as a short story, and the doc comments say what the
types cannot.

Dense code is the most common failure. A file with no blank lines, nested calls,
and no doc comments can pass every check and still be hard to change. Prettier
keeps the blank lines you write, but it never adds them.

## Order of authority

1. The repository's formatter and linter configuration, and its documented conventions.
2. The style of the surrounding code.
3. This skill.

Follow the repository even where this skill would choose differently, and say so
when the difference matters.

## Layout: let the tools own it

- Find the format and lint commands in the package scripts and the CI workflow.
  Before handing back, run the fixers on the files you touched, then run the checks.
- Do not reformat files you did not otherwise change. That noise hides the real
  change in review. Propose a separate, formatting-only commit instead.
- Write the blank lines yourself:
  - one after the import block
  - one between top-level declarations: functions, classes, interfaces, types,
    and exported or multi-line constants
  - one between class members
  - inside a function body, one between logical steps (read the input, transform
    it, perform the effect, return), and none at the start or end of the body
- When no lint rule enforces these, recommend the recipe in
  [references/lint-recipe.md](references/lint-recipe.md). Do not add tooling or
  dependencies without agreement.

## Readable structure

- **Name intermediate results** instead of nesting calls inside arguments,
  conditions, or return values. A name is a free comment.

  ```ts
  // Hard to read
  return toSummary(filterActive(await repo.list(parseTenant(req.headers))), limit);

  // Easier
  const tenant = parseTenant(req.headers);
  const accounts = await repo.list(tenant);
  const active = filterActive(accounts);

  return toSummary(active, limit);
  ```

  Keep simple expressions inline (property access, `??`, one comparison). Keep
  declarative builders, such as schemas, queries, and fluent configuration, in
  their usual chained form.
- **Order statements by data flow:** input, then transformation, then effect.
- **Guard clauses first.** Return or throw early for invalid cases. Do not write
  `else` after a `return`. Keep nesting to two or three levels.
- **One job per function.** Extract a block when you would otherwise need a
  comment to say what it does. Do not add pass-through wrappers that only call
  another function.
- **Named constants with units** for magic values: `POLL_INTERVAL_MS`, `MAX_RETRIES`.
- **One declaration per statement, and always use braces**, even for one-line bodies.
- **Top-level functions are `function` declarations.** Use arrow functions for
  callbacks and short inline functions.
- **Group long argument lists.** Give a long array of flags or options a named
  constant, or build it in small named parts, rather than one 20-line literal
  inside a call.

## Idioms

- Named exports over default exports. Use `import type` for type-only imports.
- Unions or `as const` objects over `enum`, unless the repository already uses `enum`.
- `unknown` plus narrowing over `any`. Use `satisfies` over `as` for checked literals.
- No floating promises: `await` them, return them, or mark them with `void` and a
  comment that explains why.
- Throw `Error` or a subclass, with a message that says what failed. Treat
  `catch` variables as `unknown`. Never swallow an error silently.
- Use `===`, `for...of` for arrays, `readonly` for fields that are never reassigned,
  and no `I` or `T` prefixes on type names.

The `typescript` skill covers type design and runtime validation boundaries.

## Doc comments

Use `/** TSDoc */` for what a caller needs to know, and `//` comments for why the
implementation looks the way it does. See
[references/doc-comments.md](references/doc-comments.md) for examples.

- Give every exported function, class, interface, type, and non-obvious constant a
  doc comment. Skip one only when the name and type say everything and the
  repository's lint rules do not require it.
- The first sentence says what the symbol does or represents, in the active voice.
- Add what the types cannot express: units, ranges, defaults, invariants, side
  effects (I/O, network, mutation), the errors callers should handle, ordering,
  and idempotency.
- Never repeat types. Write `@param name - description`, with the hyphen and
  without `{type}`. Add `@returns` and `@throws` only when they say something new.
- Add `@example` only for public APIs whose correct use is not obvious.
- Inline comments explain a reason, constraint, or workaround. Do not narrate code
  line by line or restate a name.
- When you change code, update or delete the comments it makes wrong. Do not leave
  commented-out code. A `TODO` names an issue or an owner.

## Before handing back

- [ ] The formatter and linter fixers ran on the touched files, and the checks and type-check pass.
- [ ] Imports, top-level declarations, and logical steps are separated by blank lines.
- [ ] No call is nested more than two deep where a named intermediate would read better.
- [ ] Every new or changed export has a doc comment that describes behaviour, not types.
- [ ] No comment restates the code, and no comment was left stale by the change.

## When reviewing

Report layout problems as one `nit` per file, and name the lint rule that would
prevent them, instead of commenting on each line. Raise a missing or misleading doc
comment on a public contract to `should`. Report structure that hides a bug as that
bug, not as style.
