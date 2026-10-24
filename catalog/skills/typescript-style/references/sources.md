# Sources

The text of this skill is original. The ideas below come from published skills and
style guides, which were read on 2026-10-24. Nothing was copied verbatim.

| Source | Licence | Ideas adapted |
|---|---|---|
| [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html) | CC-BY 3.0 | JSDoc for users and `//` for implementation; no types in `@param`; do not restate names; blank lines between sections and members, none at the start or end of a body; braces; named exports; `import type` |
| [TSDoc](https://tsdoc.org/) | specification | `@param name - description` syntax and the standard tag set |
| [perdolique/workflow `typescript-conventions`](https://github.com/perdolique/workflow/tree/main/skills/typescript-conventions) | Unlicense | Name non-trivial intermediate results; order statements by data flow; keep declarative builders chained; no pass-through wrappers; comment non-obvious decisions only |
| [thenordicone/claude-skills `typescript`](https://github.com/thenordicone/claude-skills/tree/main/skills/typescript) | MIT | Guard clauses, no `else` after `return`; `function` declarations for named functions; `as const` over `enum`; no floating promises |
| [pproenca/dot-skills `ts-google`](https://github.com/pproenca/dot-skills/tree/main/skills/.experimental/ts-google) | MIT | A rule list derived from the Google guide; checked against the guide itself |
| [claude-dev-suite `jsdoc-tsdoc`](https://github.com/claude-dev-suite/claude-dev-suite/blob/main/skills/documentation/jsdoc-tsdoc/SKILL.md) | MIT | TSDoc versus JSDoc; describe behaviour, not types; name the replacement in `@deprecated` |

This skill differs from these sources in four ways:

- It puts the formatter and linter first and treats layout as something tools
  enforce, because instructions alone do not stop dense generated code.
- It makes blank lines an explicit rule, because Prettier never adds them.
- It ships a lint recipe that was tested on the date above.
- It requires doc comments only on exports, and only with content the types cannot
  carry. It does not require `@example` and `@throws` everywhere.
