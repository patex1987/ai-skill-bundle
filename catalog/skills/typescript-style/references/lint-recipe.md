# Lint Recipe

Use this recipe to make the layout and doc-comment rules enforceable. Prettier owns
indentation, wrapping, and quotes. ESLint owns the decisions a printer cannot make:
blank lines, braces, and whether a doc comment exists and is well-formed.

Tested on 2026-10-24 with ESLint 9.39, `@stylistic/eslint-plugin` 5.10,
`typescript-eslint` 8.72, `eslint-plugin-jsdoc` 63.3, and `eslint-plugin-tsdoc` 0.5.
Check the current plugin documentation before adopting it, and adapt it to the
repository's existing config rather than replacing that config.

## Blank lines and braces

Add the `@stylistic/eslint-plugin` package and merge these rules into the
TypeScript block of `eslint.config.mjs`:

```js
import stylistic from '@stylistic/eslint-plugin';

const DECLARATIONS = ['export', 'function', 'class', 'interface', 'type', 'multiline-const', 'multiline-let'];

export default [
  {
    files: ['**/*.ts'],
    plugins: { '@stylistic': stylistic },
    rules: {
      curly: ['error', 'all'],
      'one-var': ['error', 'never'],
      '@stylistic/padding-line-between-statements': [
        'error',
        // One blank line after the import block.
        { blankLine: 'always', prev: 'import', next: '*' },
        { blankLine: 'any', prev: 'import', next: 'import' },
        // Blank lines around top-level declarations and multi-line constants.
        { blankLine: 'always', prev: '*', next: DECLARATIONS },
        { blankLine: 'always', prev: DECLARATIONS, next: '*' },
        // Short single-line constants may stay grouped.
        { blankLine: 'any', prev: ['singleline-const', 'singleline-let'], next: ['singleline-const', 'singleline-let'] },
        // After a block, and before return.
        { blankLine: 'always', prev: 'block-like', next: '*' },
        { blankLine: 'always', prev: '*', next: 'return' },
      ],
      '@stylistic/lines-between-class-members': ['error', 'always', { exceptAfterSingleLine: true }],
    },
  },
];
```

Every rule here is auto-fixable. `eslint --fix` inserts the missing blank lines, and
it puts them before a doc comment rather than between the comment and its
declaration. When a later rule in the list matches, it overrides an earlier one.
Put the `any` exceptions after the `always` rules they relax.

The `multiline-const` entries also apply inside function bodies, which separates
multi-line steps from each other. Remove them if that is too much for the codebase.

## Doc comments

Add the `eslint-plugin-jsdoc` and `eslint-plugin-tsdoc` packages:

```js
import jsdoc from 'eslint-plugin-jsdoc';
import tsdoc from 'eslint-plugin-tsdoc';

export default [
  {
    files: ['**/*.ts'],
    plugins: { jsdoc, tsdoc },
    rules: {
      // Well-formed TSDoc: `@param name - text`, no `{type}`.
      'tsdoc/syntax': 'warn',
      // Exported functions, classes, interfaces, and types need a doc comment.
      'jsdoc/require-jsdoc': ['warn', {
        publicOnly: true,
        enableFixer: false,
        require: { FunctionDeclaration: true, ClassDeclaration: true, MethodDefinition: true },
        contexts: ['TSInterfaceDeclaration', 'TSTypeAliasDeclaration', 'ExportNamedDeclaration > VariableDeclaration'],
      }],
      'jsdoc/no-types': 'error',
      'jsdoc/check-param-names': 'error',
      'jsdoc/require-hyphen-before-param-description': 'warn',
    },
  },
];
```

`enableFixer: false` matters. Without it, `--fix` inserts empty `/** */` stubs that
satisfy the rule and document nothing. Missing docs should stay visible until
someone writes them.

These rules check that a comment exists and is well-formed. They cannot tell
whether it is useful, so review the content against
[doc-comments.md](doc-comments.md).

## Naming and size (opt-in)

These rules support the Naming and Module and type size sections. They are opt-in:
the size limits are signals, and a cohesive file may legitimately pass them.
Start them as `warn`. Lint cannot judge cohesion or schema derivation, so a
reviewer still checks those.

```js
const TYPE_WORDS = '/^(object|text|string|number|bool|boolean|date|data)$/';

export default [
  {
    files: ['**/*.ts'],
    rules: {
      // Functions, variables, and local import names must not be type or global words.
      'no-restricted-syntax': [
        'error',
        {
          selector: `FunctionDeclaration > Identifier.id[name=${TYPE_WORDS}]`,
          message: 'Name functions for what they do (parseX, requireX, isX, toX), not after a type or global.',
        },
        {
          selector: `VariableDeclarator > Identifier.id[name=${TYPE_WORDS}]`,
          message: 'Name values for their role, not after a type or global.',
        },
        {
          selector: `ImportSpecifier > Identifier.local[name=${TYPE_WORDS}]`,
          message: 'Rename the import for what it does, or use a namespace import.',
        },
      ],
      // Soft size signals.
      'max-lines': ['warn', { max: 300, skipBlankLines: true, skipComments: true }],
      'max-lines-per-function': ['warn', { max: 50, skipBlankLines: true, skipComments: true }],
    },
  },
];
```

For exported interfaces and type aliases without doc comments, use the
`jsdoc/require-jsdoc` rule from [Doc comments](#doc-comments). Its `contexts`
already cover `TSInterfaceDeclaration` and `TSTypeAliasDeclaration`.

If `no-restricted-syntax` is already configured, merge these selector entries into
the existing list. A second config block for the same rule replaces the first; it
does not merge.

Behaviour verified on 2026-10-24 (ESLint 9.39, typescript-eslint 8.72,
`eslint-plugin-jsdoc` 63.3):

- **Why not `id-denylist`.** That core rule also reports interface fields, type
  properties, object literal keys, class fields, parameters, and every *reference*
  to a denied local name. A data field such as `{ date: string }` or `{ text: string }`
  would be an error. The `no-restricted-syntax` selectors above report only
  function declarations, variable declarations, and local import names. Calls to
  functions you do not own, such as `z.string()`, are never reported.
- **Imports.** `import { string } from 'zod'` is reported. Use
  `import * as z from 'zod'`, or rename the import locally (`import { text as label }`
  is not reported).
- **`max-lines`** defaults to 300 and does not count the final newline. Without the
  skip options, blank and comment-only lines count.
- **`max-lines-per-function`** defaults to 50, and **counts nested functions inside
  the outer function**. A factory that returns a 40-line closure plus 15 lines of
  setup is reported. Extract the closure, or accept the warning when the factory
  reads clearly.
- **`require-jsdoc` with `publicOnly`** reports exported interfaces, exported type
  aliases, and exported constants. It skips non-exported interfaces and aliases,
  and anything that already has a `/** */` comment. It checks only that a comment
  exists, not that it is useful.

### Boolean names (typed linting)

`@typescript-eslint/naming-convention` can require predicate prefixes on booleans,
but its `types` option needs type information. That makes linting slower and
requires `parserOptions.projectService`. Add it only if the repository already
lints with types:

```js
'@typescript-eslint/naming-convention': ['warn', {
  selector: ['variable', 'parameter'],
  types: ['boolean'],
  // The prefix is trimmed before the format check, so PascalCase allows isEnabled.
  format: ['PascalCase'],
  prefix: ['is', 'has', 'can', 'should', 'did', 'will'],
}],
```

This was verified to report `const active = …` and a `flag: boolean` parameter,
and to accept `isActive` and `hasItems`.

## Rolling it out

1. Start with the workspaces you are actively changing. Use a `files` list, and
   widen it as each area is cleaned up.
2. Land the formatting in one commit with no behaviour changes, and add its hash to
   `.git-blame-ignore-revs`, so that `git blame` skips it.
3. Introduce `require-jsdoc` as `warn`, document code as you touch it, and switch it
   to `error` once the warnings are gone.
4. Add the format check and lint commands to the repository's CI command, so that
   generated code is held to the same rules as hand-written code.
