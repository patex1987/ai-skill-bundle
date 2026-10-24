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

## Rolling it out

1. Start with the workspaces you are actively changing. Use a `files` list, and
   widen it as each area is cleaned up.
2. Land the formatting in one commit with no behaviour changes, and add its hash to
   `.git-blame-ignore-revs`, so that `git blame` skips it.
3. Introduce `require-jsdoc` as `warn`, document code as you touch it, and switch it
   to `error` once the warnings are gone.
4. Add the format check and lint commands to the repository's CI command, so that
   generated code is held to the same rules as hand-written code.
