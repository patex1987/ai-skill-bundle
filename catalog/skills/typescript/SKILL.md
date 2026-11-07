---
name: typescript
description: Design or refactor TypeScript types, function signatures, modules, and runtime validation boundaries, and explain compile-time versus runtime guarantees. Prefers schema-first validation (types inferred from a schema such as zod, strict objects, field-naming error messages) and checks that consumers ship the runtime dependency. Use for TypeScript type design, replacing any, parsing untrusted input, module and export structure, or strictness questions in any TypeScript codebase.
license: MIT-0
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# TypeScript

Use explicit types where they make the code easier to read, or where they stop
untrusted values from being treated as trusted.

## Focus areas

- Explicit types that improve readability, and clear function signatures.
- Safe alternatives to `any`: `unknown` plus narrowing, generics, or focused types.
- Interfaces versus type aliases, chosen by the existing codebase convention.
- Closed sets of values as unions, `as const` objects, or readonly maps.
- Branded or nominal identifiers where mixing two ID types would be a real bug.
- Module boundaries, exports, and ESM/CJS import style.

## Guidance

- Keep `strict` enabled. Do not loosen compiler options to make an error go away.
- Treat environment variables, JSON, HTTP responses, storage, URL parameters, and
  process output as `unknown`. Validate them at runtime before narrowing. A type
  assertion is not validation.
- Prefer types that make the code easier to explain. When introducing a type,
  say which bug or confusion it prevents.
- Distinguish what TypeScript checks at compile time from what still needs runtime
  validation, authorization, or schema checks.
- Preserve observable errors and exit behaviour when refactoring entrypoints.
- Favour incremental refactors over broad rewrites, and follow the module system,
  path aliases, and lint rules already in the repository.
- If the repository compiles TypeScript into checked-in JavaScript, edit the
  sources, rebuild, and never hand-edit the generated output.

## Runtime validation

- **Use a schema library when the repository allows the dependency**, for example
  zod. Follow whichever library the repository already uses. The schema is the
  source of truth, and the static types are inferred from it
  (`type Booking = z.infer<typeof BookingSchema>`), so the key lists cannot drift.
- **A hand-written validator needs a stated reason:** no new runtime dependencies
  allowed, a bundle-size budget, or a hot path. Write the reason in the module doc
  comment. Keep one source of truth: derive the key list from one constant, and
  check it against the type at compile time. Do not write the keys once in an
  `interface` and again in the validator.
- **Use strict objects at every level.** Reject unknown keys instead of silently
  dropping them. In zod, use `z.strictObject` (plain `z.object` strips unknown
  keys). Strictness does not carry into nested objects, so make each nested schema
  strict.
- **Error messages name fields, never values.** Report the path and the expected
  shape. Never echo the received value, because input can hold secrets or
  personal data. Avoid options that attach the input to issues, and custom
  messages that interpolate it. List unknown keys first, because they usually
  explain the other errors (a misspelled key also produces a "missing field" error).
- **Validate once, at the boundary.** Parse untrusted input into typed values at
  the edge, and pass the typed value inward. Do not re-validate in the domain.
- **Ship the runtime dependency with every consumer.** A validation library moves
  from a type-only concern to runtime code. Put it in `dependencies`, not
  `devDependencies`. Check each consumer that ships compiled output without
  bundling, such as a Dockerfile that copies `dist/` and runs a production
  install, a function layer, or a workspace package whose `package.json` must
  declare the dependency itself rather than rely on hoisting. Each must install
  the dependency. Prove it by running the built artefact, not only the tests.

See [references/runtime-validation.md](references/runtime-validation.md) for a
tested zod example with an error formatter.

Run the repository's type-check and test commands after changes.

For layout, readable statement structure, and doc comments, use the
`typescript-style` skill.
