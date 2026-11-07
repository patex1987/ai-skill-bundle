---
name: typescript-style
description: Write and review TypeScript that is easy to read and change, covering formatter- and linter-enforced layout, verb-phrase naming, readable statement structure, module cohesion and type size, idiomatic language choices, and TSDoc comments that explain behaviour rather than repeat types. Use whenever writing or editing TypeScript, when generated code comes out dense, badly named, oversized, or undocumented, when adding or reviewing doc comments, or when setting up formatter and lint rules for code style. For type design and runtime validation, use the typescript skill.
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

## Naming

A name tells the reader what to expect without opening the definition.

- **Functions are named for what they do**, with a verb or verb phrase:
  `parseBooking`, `requireText`, `isExpired`, `toSummary`, `loadConfig`. Use the
  prefix consistently. `parseX` returns a value or throws, `requireX` asserts a
  field is present and valid, `isX` and `hasX` return booleans, and `toX` converts
  without validating.
- **Never name a function or variable after a type or global:** `object`, `text`,
  `string`, `number`, `bool`, `boolean`, `date`, `data`. These names say what the
  value is made of, not what it means. They also shadow globals or read as type
  keywords. The ban covers declarations and local import names. A *field* such as
  `{ date: string }` is fine when the domain calls it that.
- **Booleans read as predicates:** `isReady`, `hasExpired`, `canRetry`,
  `shouldNotify`. Do not use `flag`, `status`, or `check` for a boolean.
- **Values are named for their role**, not their shape: `pendingBookings`, not
  `list` or `arr`. Units go in the name when the type cannot carry them:
  `timeoutMs`, `sizeBytes`.

```ts
// Hard to follow: what does object() do? Does text() parse, check, or convert?
function object(value: unknown): Record<string, unknown> { ... }
function text(record: Record<string, unknown>, key: string): string { ... }
const data = object(JSON.parse(raw));
const bool = data.active === true;

// Says what each step does
function parseJsonObject(raw: string): Record<string, unknown> { ... }
function requireText(record: Record<string, unknown>, field: string): string { ... }
const booking = parseJsonObject(raw);
const isActive = booking.active === true;
```

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

## Module and type size

A file that passes every check can still be too much to hold in your head.

- **A module has one reason to change.** Split it when one file mixes several
  of these:
  - field primitives (reusable value checks)
  - record types
  - parsing and I/O mapping (JSON, environment, CLI output)
  - policy (decisions over parsed values)

  A typical split is `fields.ts`, `booking.ts` (types or schema), `parse.ts`, and
  `policy.ts`, with an `index.ts` only if the package needs one public entry point.
  A pure module with no I/O can still need splitting: being free of side effects
  says nothing about cohesion.
- **Name the nested types.** Give a nested object type a named, documented
  `interface` when it appears in more than one place or has more than about five
  fields. Inline object types are fine for small, one-off shapes.

  ```ts
  // Hard to scan, and the address shape cannot be reused or documented
  export interface Booking {
    customer: { id: string; name: string; email: string; phone: string; tier: string; since: string };
    pickup: { street: string; city: string; postcode: string; country: string };
    dropoff: { street: string; city: string; postcode: string; country: string };
  }

  // Named parts, each documented once
  /** Postal address where a parcel is collected or delivered. */
  export interface Address { ... }

  /** The customer who placed the booking. */
  export interface Customer { ... }

  /** A confirmed request to move one parcel. */
  export interface Booking {
    readonly customer: Customer;
    readonly pickup: Address;
    readonly dropoff: Address;
  }
  ```
- **Soft size signals:** about 300 lines per file, or about 50 lines per function.
  Passing one is a prompt to look for a second reason to change, not an order to
  split. Do not split a cohesive file only to get under the number.
- **One source of truth per shape.** When a type and a validator each list the
  same keys, the lists will drift. Derive one from the other (see the
  `typescript` skill on runtime validation).

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
- [ ] Functions are verb phrases. No function or variable is named after a type or
      global (`object`, `text`, `string`, `number`, `bool`, `date`, `data`).
- [ ] Booleans read as predicates (`isX`, `hasX`, `canX`, `shouldX`).
- [ ] Each touched module has one reason to change. Files near 300 lines or
      functions near 50 were checked for a second concern.
- [ ] Nested object types that are reused or have more than about five fields are
      named and documented.
- [ ] No key list is written twice (type and validator). One is derived from the other.
- [ ] Every new or changed export, including interfaces and type aliases, has a
      doc comment that describes behaviour, not types.
- [ ] No comment restates the code, and no comment was left stale by the change.

## When reviewing

Report layout problems as one `nit` per file, and name the lint rule that would
prevent them, instead of commenting on each line. Raise these to `should`:

- a misleading or missing doc comment on a public contract
- names that hide what a function does (type-word or noun names on functions)
- a module that mixes primitives, types, parsing, and policy
- a key list duplicated between a type and its validator

Each of these makes the next change harder, even when the code works today.
Report structure that hides a bug as that bug, not as style.
