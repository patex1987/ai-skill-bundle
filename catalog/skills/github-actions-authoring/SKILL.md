---
name: github-actions-authoring
description: Write, test, or review repository-authored GitHub Actions (composite and JavaScript/TypeScript actions) and reusable workflows, including input validation, generated dist/lib output, Node test-runner coverage with fake git/gh executables, permissions, and SHA-pinned third-party actions.
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# GitHub Actions Authoring

Treat action inputs, the runner environment, and process output as untrusted.
Keep policy pure and testable, and keep YAML as thin glue. For boundaries, see
the automation note in `clean-architecture` if it is installed.

## Authoring

- Keep strict TypeScript and avoid `any`. Model closed value sets as unions or
  readonly maps, and validate environment, JSON, and process output at runtime
  before narrowing.
- Use explicit ESM imports for the Node runtime the action declares.
- When sources compile to checked-in JavaScript (`dist/`, `lib/`, `.mjs`), edit the
  sources, rebuild, and never hand-edit generated output. CI should fail on drift.
- Pass arguments to `git`, `gh`, and other tools as arrays, never as shell strings.
- Composite YAML owns step order and the permissions it expects from callers.
  Pin third-party actions to full commit SHAs, and request the least
  `permissions` each workflow job needs.
- Preserve observable errors, outputs, and exit codes when refactoring an entrypoint.

## Testing

- Run the checked-in JavaScript that caller workflows will execute, using the
  Node built-in test runner or the repository's runner.
- Use temporary workspaces and fake `git`/`gh` executables for process adapters.
  Ordinary tests never call GitHub, registries, scanners, OIDC, or cloud APIs.
- Assert success outputs and retained files, and refusal of unsupported or unsafe
  inputs: paths, symlinks, overwrites, stale revisions, unexpected digests or subjects.
- Verify exact artifact membership and action pins when composite metadata changes.
- Keep inputs small and explicit. Do not hide the environment or filesystem
  state that sets up a security scenario.
- Add a regression test whenever a failure could weaken admission, disclose
  process output, or produce ambiguous evidence.

## Verification

Run focused tests while iterating, then the repository's CI script (install
with lifecycle scripts disabled where the repository does, compile, compare
generated output, run the offline suite) and `git diff --check`.
