# Plan: TypeScript naming, module cohesion, and schema-first validation

Status: implemented (authorized in the request: "Plan first, then implement"). Acceptance checks AC1–AC6 pass; see `docs/REVIEW-LOG.md`.
Planning depth: standard (several catalog entities, no runtime code, no contracts).

## 1. Goal

Generated TypeScript should get naming, module cohesion, and runtime validation
right on the first draft, because format, lint, type-check, and tests do not
catch these problems. Evidence: an agent wrote a 600-line pure "contract" module
that passed every check, and a reviewer rejected it for five reasons:

| # | Defect | Catalog gap today |
|---|---|---|
| D1 | Helpers named after types and globals: `object()`, `text()`, `date()`, `bool()`, `number()` | `typescript-style` has no naming section |
| D2 | One large interface with nested inline object types | No rule on when to name a nested type |
| D3 | One file mixing field primitives, record types, JSON parsing, and policy | `clean-architecture` says "do not impose layers", which reads as permission for low cohesion |
| D4 | A hand-written validator that repeats every key list from the interface | `typescript` says "validate at runtime" but not how; nothing prefers schema-derived types |
| D5 | Exported interfaces without doc comments | `typescript-style` requires docs on exports, but its checklist and review guidance do not mention interfaces or type aliases |

Unchanged: the skills' scope, the routing tiers, the packs, render output formats.
Non-goals: installing into any consuming repository; making a schema library a
hard requirement; running the evals against a model.

## 2. Evidence checked

- `catalog/skills/typescript-style/SKILL.md`: layout, structure, idioms, and doc
  comments, but no naming or size guidance.
- `catalog/skills/typescript/SKILL.md`: "Validate them at runtime before
  narrowing. A type assertion is not validation." No library preference, no
  strictness, no error-message or packaging guidance.
- `catalog/skills/clean-architecture/SKILL.md:13`: "Do not impose a four-layer
  layout..."; `references/automation-and-ci.md` ends "Do not force service layers
  onto straightforward construct or stack code." Both are about layers, and
  neither mentions cohesion.
- `catalog/agents/readability-maintainability.md`: covers names against behaviour
  and responsibilities, but not type-word names, file size, or mixed concerns.
- Rule behaviour was tested on 2026-10-24 (ESLint 9.39, typescript-eslint 8.72,
  zod 4.6):
  - `id-denylist` also flags interface fields, type properties, and object
    literal keys (`{ text: string }`, `{ number: 1 }`). That produces false
    positives for legitimate data fields, so the recipe uses
    `no-restricted-syntax` selectors for function, variable, and import names
    instead. Tested: exactly those three were reported.
  - `max-lines` defaults to 300 lines, and `max-lines-per-function` to 50. The
    function count includes nested functions (tested).
  - `@typescript-eslint/naming-convention` with `types: ['boolean']` needs typed
    linting, so it is opt-in only.
  - zod 4: `z.strictObject` rejects unknown keys with `unrecognized_keys`. Plain
    `z.object` silently strips them. Strictness does not propagate to nested
    objects. Default messages name the expected type, not the input value. Unknown-key
    issues come after field issues in `error.issues`, so a formatter must sort
    them first.

## 3. Alternatives

| Option | Verdict |
|---|---|
| A. A new `typescript-modules` skill | Rejected: splits one writing pass across three skills, and triggering overlaps with `typescript-style` |
| B. Extend `typescript-style` (naming, size), `typescript` (validation), and `clean-architecture` (cohesion), each in its own domain | **Chosen**: each rule lives with the skill that already owns the decision |
| C. Lint-only enforcement | Rejected as the only measure: lint cannot judge cohesion or schema derivation. Kept as opt-in support |

## 4. Changes

1. `typescript-style/SKILL.md`: add a **Naming** section, with verb-phrase
   functions, a type-word denylist, predicate booleans, and a bad and good example.
   Add a **Module and type size** section: one reason to change per module, a split
   signal, named documented nested types (reused, or more than about 5 fields), and
   soft limits of about 300 lines per file and about 50 per function. Extend the
   checklist and the reviewing guidance.
2. `typescript/SKILL.md`: add a **Runtime validation** section: schema library
   first when the dependency is allowed, types inferred from the schema, a stated
   reason for hand-written validators, strict objects at every level, and error
   messages that name fields, never values, with unknown keys first. Packaging:
   unbundled consumers must ship the runtime dependency. Add a short reference with
   a tested zod example and error formatter.
3. `clean-architecture/SKILL.md` and `references/automation-and-ci.md`: state that
   "do not impose layers" is about dependency direction, not permission for low
   cohesion. Split pure modules by reason to change.
4. `typescript-style/references/lint-recipe.md`: add opt-in **Naming and size**
   rules (`no-restricted-syntax` type-word selectors, `max-lines`,
   `max-lines-per-function`, and `require-jsdoc` contexts for exported types),
   with the tested caveats, including why not `id-denylist` and when to use typed
   `naming-convention`.
5. `typescript-style/evals`: add an anonymised fixture (a single-file shipment
   booking contract of about 250 lines, with `object()`/`text()` helpers, a large
   nested interface, mixed concerns, a duplicated key list, and undocumented
   exports) and two eval cases: rewrite and review. Add one case to `typescript`
   evals (new file) for schema-first validation.
6. `catalog/agents/readability-maintainability.md`: add explicit naming and
   cohesion checks to the method, and the report bar.
7. Record the change in `docs/REVIEW-LOG.md`.

## 5. Acceptance checks (agreed in the request)

| ID | Check |
|---|---|
| AC1 | `python3 scripts/aibundle.py validate` passes, including the portability lint and evals |
| AC2 | `python3 -m unittest discover -s tests` passes |
| AC3 | Every lint rule in the recipe was run in a scratch project and behaves as documented |
| AC4 | The zod example and error formatter in the `typescript` reference run as documented |
| AC5 | The new fixture reproduces all five defects D1–D5, and the eval expectations require verb names, named documented sub-types, and split modules |
| AC6 | No project names, host paths, or model IDs in catalog content |

## 6. Steps

| Step | Files | Tier |
|---|---|---|
| 1 | `typescript-style/SKILL.md` | balanced |
| 2 | `typescript/SKILL.md`, `typescript/references/runtime-validation.md` | balanced |
| 3 | `clean-architecture/SKILL.md`, `references/automation-and-ci.md` | balanced |
| 4 | `typescript-style/references/lint-recipe.md` (after scratch tests) | balanced |
| 5 | fixtures and `evals.json` for `typescript-style` and `typescript` | balanced |
| 6 | `agents/readability-maintainability.md` | balanced |
| 7 | `docs/REVIEW-LOG.md`; run AC1–AC6 | fast |

## 7. Risks

| Risk | Mitigation |
|---|---|
| Size limits read as hard rules, so agents split files mechanically | Call them soft signals. The rule is reason to change, and the numbers only prompt a look |
| Schema preference pulls a dependency into repositories that avoid one | "When the repository allows it". A hand-written validator stays valid with a stated reason and one source of key lists |
| The type-word denylist hits legitimate imports such as `import { string } from 'zod'` | Document the case: use the namespace import (`import * as z`) or rename locally |
| Body-length limits on `SKILL.md` | `typescript-style` stays well under 500 lines. The zod detail goes to a reference |
