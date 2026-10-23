# Readable Python and Command-Line Boundaries

## Human-Facing CLI Boundaries

- Write the parser description for an engineer discovering the command through
  `--help`: explain what operation it performs, what it trusts, and what it
  produces.
- Give every non-obvious argument useful help text. Describe the expected value
  and its role; do not merely expand the flag name.
- Keep parsing and presentation in the CLI. Domain policy and application
  workflows must not call `print()` or know about terminal formatting.
- Define output channels deliberately. Use stdout for a documented
  machine-consumable result when the command has one, and stderr for human
  diagnostics. Do not mix commentary into a JSON or path output contract.
- `print()` is acceptable in a small presentation adapter. Use logging when the
  command needs structured operational events, levels, or multiple sinks—not as
  a reflexive replacement for every print.
- Do not introduce `structlog` piecemeal. First define the event names, context,
  redaction rules, renderer, and stdout/stderr contract; then adopt it
  consistently at the outer boundary if the benefit justifies the dependency.

## Documentation And Readability

- Use native reStructuredText docstrings for supported public Python APIs and
  for boundary functions whose trust assumptions, side effects, or failure
  behavior are not obvious.
- Start with a human explanation of the operation and why callers use it. Add
  `:param name:`, `:returns:`, and `:raises Error:` fields when they communicate
  information that type hints cannot.
- Document accepted trust level, important invariants, external side effects,
  emitted artifacts, and failure semantics where relevant.
- Do not write a docstring that only rephrases the function name or signature.
  Obvious private helpers do not need ceremonial documentation.
- Keep docstrings accurate when behavior changes. A detailed stale docstring is
  worse than a short truthful one.

## Python Control Flow And Readability

Apply these principles when writing new Python code and reviewing or
refactoring existing code. Favor boring, predictable code: optimize for low
cognitive complexity, not minimum indentation or line count. Do not refactor
unrelated code merely because it differs from a stylistic preference.

- Prefer shallow control flow, usually one or two nesting levels, using guard
  clauses for invalid inputs and exceptional or terminal cases. Treat nesting
  depth as a preference, never a limit. Keep necessary context managers and
  `try/finally` resource cleanup together; do not split them just to flatten code.
- Use early returns when a branch has reached its natural conclusion. Omit
  redundant `else` branches after `return`, `raise`, `break`, or `continue`.
  Keep `if/elif/else` when mutually exclusive branches converge on shared work;
  independent `if` statements must not change which branches execute.
- Extract helpers for meaningful responsibilities or domain rules, such as
  `_validate_statement` or `_matches_workload_grant`. Judge the extraction by
  whether the caller becomes easier to understand. Avoid trivial wrappers,
  excessive navigation, and abstractions created only to reduce indentation.
- Prefer explicit logic over dense conditions, nested ternaries, or clever
  one-liners. Use named predicates for complex concepts, but keep simple boolean
  expressions inline when a helper would add no meaning.
- Validate inputs and invariants before the main operation where practical.
  Preserve required checks throughout workflows, including checks immediately
  before side effects; moving all validation to the beginning can miss changes.
- Prefer direct results over unnecessary mutable flags. Use `any`, `all`, or
  comprehensions only when their evaluation behavior fits the contract. Keep an
  explicit loop when it improves diagnostics or preserves validation and
  side-effect ordering.
- Never let an early return or short-circuit expression skip required validation.
  For example, finding a matching audit `Allow` must not skip a later `Deny` or
  malformed statement. Validate all required statements before accepting, either
  in a separate pass or by recording the match and finishing the validation loop.
- Preserve observable behavior during readability refactors: validation order
  and completeness, exception types and messages, side-effect order, cleanup,
  edge cases, and public contracts. Explain meaningful tradeoffs; do not silently
  introduce behavior changes under the label of stylistic cleanup.

During review, look for unnecessary nesting, redundant terminal branches,
unclear predicates, helpers without a useful responsibility, and mutable state
that obscures intent. Suggest changes only when the readability benefit is
concrete, and check that simplifying the happy path preserves failure behavior.
