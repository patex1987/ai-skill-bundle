# Lint Recipe

An opt-in rustfmt and Clippy configuration for the parts of `rust-style` that a
tool can check. Propose it only with agreement, and add it in its own commit.
Most of the skill (naming, structure, doc comment content, blank lines between
steps) has no lint. Clippy passing does not mean the code reads well.

Tested on 2026-11-07 with Rust 1.96.1 (rustfmt 1.9.0, Clippy 0.1.96, stable).
Every entry below was run against a dense sample module. The `[lints]` table
needs Rust 1.74 or later. `#[expect]` and `reason = "..."` need Rust 1.81.

## `rustfmt.toml`

```toml
style_edition = "2024"
```

`style_edition` follows the crate's Rust edition when it is not set. Set it
explicitly only when the repository wants the 2024 style on an older edition.
The 2024 style edition sorts versions naturally (`x8` before `x16`) and puts
uppercase before lowercase.

Do not add `imports_granularity` or `group_imports` on stable. rustfmt prints
"unstable features are only available in nightly channel" and ignores them.
Keep import groups and one-module-per-`use` by hand, as `SKILL.md` describes.

## `Cargo.toml`: every crate

```toml
[lints.rust]
unsafe_code = "forbid"
unused_qualifications = "warn"

[lints.clippy]
allow_attributes_without_reason = "warn"
dbg_macro = "warn"
todo = "warn"
unwrap_used = "warn"
redundant_else = "warn"
manual_let_else = "warn"
semicolon_if_nothing_returned = "warn"
needless_pass_by_value = "warn"
inconsistent_struct_constructor = "warn"
```

In a Cargo workspace, put these under `[workspace.lints.*]` and add
`[lints] workspace = true` to each member.

CI turns warnings into errors with `cargo clippy --all-targets -- -D warnings`.
Keep the levels at `warn` in `Cargo.toml` so local builds still run.

## `clippy.toml`

```toml
allow-unwrap-in-tests = true
```

Without this setting, `unwrap_used` reports every `unwrap` in `#[cfg(test)]`
modules. On an existing 4,000-line Axum service, all of its roughly 100
`unwrap_used` warnings came from test modules.

## Libraries: public API docs

For a crate that other crates depend on, add:

```toml
[lints.rust]
missing_docs = "warn"

[lints.clippy]
missing_errors_doc = "warn"
missing_panics_doc = "warn"
```

These check exported items only. In a binary crate, or for `pub(crate)` items,
they report nothing.

Do not set `check-private-items = true` in `clippy.toml` to reach private items.
`missing_panics_doc` then also flags every `#[test]` function that calls
`unwrap`.

## Binary crates: docs on internal items, gradually

`clippy::missing_docs_in_private_items` covers `pub(crate)` and private items.
It does not flag items inside `#[cfg(test)]` modules. It is noisy on existing
code: the same 4,000-line service reported about 300 warnings, mostly struct
fields. Adopt it one module at a time instead of crate-wide:

```rust
//! Seat holds: placing, looking up, and expiring temporary seat reservations.
#![warn(clippy::missing_docs_in_private_items)]
```

Turn it on crate-wide only after the backlog is cleared, in its own issue.

## What the recipe catches

On a format-clean, Clippy-clean sample module (the `evals/files` fixture), the
baseline recipe reported six `unwrap` calls on runtime paths and one
`#[allow]` without a reason. It did not report any of these:

- type-word names (`data`, `value`, `string`)
- a `bool` parameter
- `Result<T, String>`
- a happy path nested in `if`/`else`
- a one-word doc comment
- missing blank lines
- an index that panics on empty input

Those need the skill or a reviewer.
