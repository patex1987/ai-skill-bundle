---
name: typescript
description: Design or refactor TypeScript types, function signatures, modules, and runtime validation boundaries, and explain compile-time versus runtime guarantees. Use for TypeScript type design, replacing any, module and export structure, or strictness questions in any TypeScript codebase.
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

Run the repository's type-check and test commands after changes.

For layout, readable statement structure, and doc comments, use the
`typescript-style` skill.
