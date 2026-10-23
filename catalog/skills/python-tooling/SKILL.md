---
name: python-tooling
description: Set up or change a Python project's toolchain and command-line entry points with uv, pytest, Ruff, and pyproject.toml, including dependency changes, lockfiles, pinned Python versions, frozen CI installs, local-first check commands, and readable CLI and control-flow conventions.
metadata:
  routing-tier: balanced
  routing-effort: low
---

# Python Tooling

Keep one reproducible toolchain that developers and CI run the same way. Follow
the repository's existing tools if they differ from these defaults (for example
Poetry or tox), and do not migrate tools as a side effect.

## Baseline

- `uv` resolves dependencies, syncs environments, and runs commands. Pin the
  `uv` requirement in `pyproject.toml` and the Python patch version in
  `.python-version`, and have CI read those files instead of repeating versions.
- Runtime dependencies go in `project.dependencies`, and test and lint tools in a
  `dev` dependency group. Commit `uv.lock`.
- pytest runs tests (add `pytest-asyncio` for async code), and Ruff handles linting and formatting.
- Prefer the standard library unless a dependency clearly improves correctness
  or maintainability.

A typical full local check:

```bash
uv sync --frozen
uv run --frozen --no-sync pytest
uv run --frozen --no-sync ruff check .
uv run --frozen --no-sync ruff format --check .
git diff --check
```

Use the repository's documented check command when it has one.

## Dependency changes

- Edit `pyproject.toml`, update `uv.lock` (`uv lock`), and verify with a frozen sync.
- Prefer bounded compatible ranges. Keep packaging metadata and console entry
  points aligned with the real package layout (for example `src/`).
- Do not add a library when the standard library or an existing dependency is enough.

## Local-first entry points

- Every executable capability has a documented command that works from a local
  checkout: an importable module plus `python -m package.module` or a declared
  console script.
- CI installs the pinned environment and calls that same command. Do not keep a
  second implementation in workflow YAML or shell.
- Keep library code importable and testable without CI-only environment
  variables, credentials, or live services. Put live integration checks in
  separate, explicit jobs.
- Make failures locally actionable: name the stage, safe input context, and a
  stable issue code where applicable.

## CI boundaries

- Public CI stays credential-free and network-independent after installing dependencies.
- Keep categories separate when they exist: unit and contract tests, automation
  tests, and smoke tests against running services.
- Publication and deployment jobs depend on the relevant quality gates.

## Readability and CLIs

Read [references/readability-and-cli.md](references/readability-and-cli.md)
when writing CLI parsers, choosing between stdout, stderr, and logging, writing
docstrings, or refactoring control flow for readability without changing behaviour.
