---
name: rust-style
description: Write and review Rust application code (services, CLIs, agents) that is easy to read and change, covering rustfmt- and Clippy-enforced layout, import and module organisation, naming, readable statement structure, error and panic policy, borrowing and trait idioms, and doc comments that explain behaviour rather than repeat signatures. Use whenever writing or editing Rust, when generated Rust comes out dense, badly named, or undocumented, when adding or reviewing doc comments, or when setting up rustfmt and Clippy lint rules. For Axum and Tokio service design, use rust-axum-service; for tests, use rust-testing.
license: MIT-0
metadata:
  routing-tier: balanced
  routing-effort: medium
  tags: [rust, style, documentation, formatting, clippy]
---

# Rust Style

Code is read far more often than it is written. Write Rust that the next
engineer can scan quickly: each file's shape is visible at a glance, each
function reads top to bottom, and doc comments say what the signature cannot.

This skill is for **application code**: HTTP services, CLIs, workers, and agents
built with Cargo. It follows the official Rust Style Guide, and it adapts the
parts of Google's Rust guide that are not specific to Chromium, Android,
Fuchsia, or Google's build systems. Library-grade API rules (accept
`impl IntoIterator`, mark public enums `#[non_exhaustive]`) apply only to crates
that other teams depend on. Application code favours simplicity and directness
over broad reuse.

`rustfmt` and Clippy can pass on code that is still hard to read. rustfmt keeps
the blank lines you write but never adds them. Dense, undocumented code is the
most common failure.

## Order of authority

1. The repository's `rustfmt.toml`, Clippy configuration, `[lints]` table, and
   documented conventions.
2. The style of the surrounding code.
3. This skill.

Follow the repository even where this skill would choose differently, and say so
when the difference matters.

## Layout: let the tools own it

- Find the format, lint, and test commands in the repository guidance and the CI
  workflow. Typical commands are `cargo fmt --all -- --check` and
  `cargo clippy --all-targets --all-features -- -D warnings`. Before handing
  back, run `cargo fmt` and then the checks.
- Do not reformat files you did not otherwise change. Propose a separate,
  formatting-only commit instead.
- Do not use `#[rustfmt::skip]` for personal taste. Use it only for deliberate
  alignment, such as a matrix or lookup table, and add a comment saying why.
- Write the blank lines yourself. rustfmt allows zero or one between items and
  statements, and it decides neither:
  - one after the `use` block, and one after the `mod` declarations
  - one between top-level items: structs, enums, `impl` blocks, functions, and
    multi-line constants
  - one between methods in an `impl` block
  - inside a function body, one between logical steps (parse the input, compute,
    perform the effect, return), and none at the start or end of the body
- When the repository has no lint configuration, recommend the recipe in
  [references/lint-recipe.md](references/lint-recipe.md). Do not add tooling
  or dependencies without agreement.

## Files, modules, and imports

- **File order:** `//!` module docs, `use` statements, `mod` declarations,
  constants, types and their `impl` blocks, free functions, then
  `#[cfg(test)] mod tests` last.
- **Import groups,** separated by a blank line: `std`/`core`/`alloc`, then
  external crates, then `crate::`, `super::`, and `self::`. rustfmt sorts
  within a group and never merges or reorders groups. The `group_imports`
  option needs nightly rustfmt, so set the groups by hand.
- **One module per `use` line:** write `use std::sync::{Arc, Mutex};`, not
  `use std::{sync::{Arc, Mutex}, time::Duration};`. Prefer several short `use`
  lines to one nested, multi-line import.
- **No glob imports,** except `use super::*;` in a test module and
  `pub use child::*;` re-exports in a parent module. A glob hides where a name
  comes from.
- **Types unqualified, functions qualified by module:** `Duration`, `HashMap`,
  but `mem::take(&mut x)` and `fs::read_to_string(path)`. When two types share a
  name (`io::Error` and a crate `Error`), qualify one or rename with `as`.
- **Import a trait where it is used** when only one function needs it, for
  example `use std::str::FromStr;` inside that function.
- **Name a file after its main type:** `hold_store.rs` holds `HoldStore`.
  Keep parent modules (`mod.rs` or `foo.rs` beside `foo/`) to declarations,
  re-exports, and a little glue. Do not use `#[path]`.
- **Use the smallest visibility that works.** In a binary crate, prefer
  `pub(crate)` or private to `pub`. Do not make a field `pub` only so a test
  can read it.

## Naming

A name tells the reader what to expect without opening the definition.

| Item | Case |
|---|---|
| Types, traits, enum variants | `UpperCamelCase` |
| Functions, methods, variables, fields, modules, macros | `snake_case` |
| `const` and immutable `static` | `SCREAMING_SNAKE_CASE` |
| Generic type parameters | one capital letter, or a short name tied to the bound |
| Lifetimes | `'a` for one or two simple relationships, otherwise descriptive (`'conn`) |

- **Functions say what they do:** `parse_hold`, `release_expired`,
  `seat_count`. Follow the standard library's prefixes:
  - `as_x` is a free borrowed view, `to_x` is a conversion that does work, and
    `into_x` consumes `self`
  - `is_x`, `has_x`, `can_x` return `bool`
  - getters have no `get_` prefix: `seats()`, `seats_mut()`, `set_seats()`,
    `take_seats()`
  - constructors are `new`, `try_new` (returns `Result`), `with_x` (one variant
    of several), `from_x` (beside a `From` impl), and a type with `new()` and no
    arguments also implements `Default`
- **Never name a value after its type or shape:** `data`, `value`, `string`,
  `obj`, `map`, `vec`, `list`, `res`. Name the role: `requested_seats`,
  `holds_by_id`. Single letters are fine only in short closures and
  conventional indices.
- **Do not abbreviate by deleting letters** (`cnt`, `mgr`, `rsvn`). Write the word
  unless the abbreviation is common (`id`, `url`, `http`).
- **Units belong in the type,** such as `Duration` or `SystemTime`. When a raw
  number is unavoidable, put the unit in the name: `ttl_secs`, `size_bytes`.
- **Reserved words:** use `r#type` or `type_`. Do not misspell (`typ`, `krate`).
- **Extension traits** that only add methods to a foreign type end in `Ext`.

## Readable structure

- **Name intermediate results** instead of nesting calls in arguments and
  conditions. A name is a free comment.

  ```rust
  // Hard to read
  store.insert(parse_seats(&req.seats)?.into_iter().filter(|s| !held.contains(s)).collect(), ttl_for(tier(&user)));

  // Easier
  let requested = parse_seats(&req.seats)?;
  let available: Vec<Seat> = requested.into_iter().filter(|seat| !held.contains(seat)).collect();
  let ttl = ttl_for(user.tier());

  store.insert(available, ttl);
  ```
- **Guard clauses first.** Return early for invalid input, with `let ... else`
  for patterns that must match. Keep the happy path at the left margin, not
  inside a trailing `else`.
- **Use expressions:** `let ttl = if is_vip { VIP_TTL } else { STANDARD_TTL };`,
  not a mutable variable assigned in branches.
- **Match, do not check-then-unwrap:** `if let Some(hold) = holds.get(id)`, not
  `if holds.get(id).is_some() { holds.get(id).unwrap() }`.
- **Keep iterator chains short.** A chain of three or four adapters is fine.
  Use a `for` loop when the body mutates outside state, has several steps, or
  needs `?`. Avoid `for_each`, and do not put a long chain in a `for` header.
- **Write the type where inference hides it:** on `.collect()`, `.parse()`,
  `.into()`, and long chains, as `let ids: Vec<HoldId> = ...`. Use a turbofish
  only where a binding cannot carry the type.
- **Replace a non-obvious `bool` parameter with an enum:** `place(seats,
  Tier::Vip)`, not `place(seats, true)`. If a `bool` stays, add a
  `/* is_vip */` comment at the call site.
- **Use named fields for anything but a newtype.** Use `.0`/`.1` only on
  single-field newtypes and very local tuples.
- **Name magic numbers** as constants with a unit or a `Duration`:
  `const STANDARD_HOLD: Duration = Duration::from_secs(300);`.
- **Build strings with `format!`**, not `+` chains or `str::replace` templates.

## Errors and panics

- `Option` for plain absence. `Result` for failures the caller may handle or
  needs to tell apart. `panic!` only for bugs, meaning broken invariants the code
  itself should prevent.
- Model library and domain errors as an enum that implements `Display` and
  `std::error::Error`, by hand or with `thiserror` if the repository uses it.
  Do not use `Result<T, String>`. Use `anyhow` (or a similar crate) only at the
  edges: `main`, configuration, and startup wiring. Add context there with
  `.context("reading config")`.
- `unwrap()` is acceptable in tests and in proven local invariants. Elsewhere,
  use `?` or handle the case. When a panic is right, use `expect` with the
  invariant it relies on: `.expect("UNIX_EPOCH is before now")`. Never
  `unwrap` on request input, I/O, or configuration.
- Never reach into a poisoned `Mutex`. Propagate an error, or panic with a
  message.
- Give `assert!` and `debug_assert!` a message that says why the condition must
  hold, or shows the value. Do not restate the condition.
- Add `#[must_use]` to functions where ignoring the result is a mistake, unless
  the return type already has it (`Result` does).

## Types, ownership, and traits

- Accept borrowed views: `&str` not `&String`, `&[T]` not `&Vec<T>`,
  `Option<&T>` not `&Option<T>`, and `&T` not `&Box<T>`.
- Borrow first. Clone only when ownership or an async boundary needs it, not to
  quiet the borrow checker. Cloning an `Arc` is cheap and expected.
  `Arc<...>` for shared service state is normal. Do not add `Rc` or `Arc` where
  single ownership works.
- Use a newtype for identifiers and units that are easy to mix up:
  `struct HoldId(String)`.
- Implement standard traits instead of inventing methods: `FromStr` not
  `fn parse_str`, `Display` not `fn to_text`, `Default`, and `From`/`TryFrom`.
  Derive what you can. Implement `is_empty` alongside `len`.
- Define a trait only when there are several implementations, or one boundary
  that needs a test double. Do not use a trait only to organise code. Prefer
  generics or `impl Trait` to `dyn Trait` unless you need heterogeneous values
  or smaller code. Use `impl Into<T>` parameters only in library APIs.
- Prefer functions and types to `macro_rules!`, and `macro_rules!` to procedural
  macros.
- Write `unsafe` only when no safe alternative exists. Wrap it in a small safe
  function, and add a `// SAFETY:` comment that explains why each requirement
  holds. Set `unsafe_code = "forbid"` in crates that do not need it.

## Attributes

- Use `#[expect(lint, reason = "...")]` (Rust 1.81 and later) instead of a bare
  `#[allow]`. It warns (`unfulfilled_lint_expectations`) once the lint no longer
  fires, so stale suppressions get removed. When `#[allow]` is right (generated code, a `cfg`-dependent lint),
  add `reason = "..."`.
- Use one `#[derive(...)]` per item. Doc comments go above attributes.

## Doc comments

Use `///` for what a caller needs to know, `//!` at the top of a module or
crate for what the module is for, and `//` for why the implementation looks the
way it does. See [references/doc-comments.md](references/doc-comments.md) for
examples.

- In a library, document every public item. In a binary crate, give every
  module a `//!` line. Document every item used from another module, unless its
  name and signature say everything.
- The first line is a one-sentence summary in the third person
  ("Releases expired holds."). Do not repeat the name ("Release function.").
- Add what the signature cannot say:
  - units, ranges, and defaults
  - side effects (I/O, locking, mutation)
  - ordering and idempotency
- Use the standard rustdoc headings when they apply:
  - `# Errors` lists when each error variant is returned
  - `# Panics` lists the conditions that panic
  - `# Safety` states what the caller must guarantee for an `unsafe fn`
  - `# Examples` only where correct use is not obvious
- Do not explain the language ("Implements Clone so it can be cloned").
- Comments are sentences: capital letter, full stop, under about 80 columns. Put
  them on their own line, not after code.
- Inline comments explain a reason, constraint, or workaround. A `TODO` names an
  issue. Delete comments the change makes wrong, and do not commit
  commented-out code.

## Before handing back

- [ ] `cargo fmt` ran, and the repository's fmt, Clippy, and test commands pass.
- [ ] Imports are in std, external, crate groups, one module per `use`, with no
      globs outside test modules and re-exports.
- [ ] Top-level items, methods, and logical steps are separated by blank lines.
- [ ] No variable or function is named after a type or shape (`data`, `value`,
      `string`, `res`). Functions follow `as_`/`to_`/`into_`/`is_` and have no
      `get_` prefix.
- [ ] Invalid input returns early. The happy path is not nested in an `else`.
- [ ] No `unwrap` outside tests and proven invariants. `expect` messages state
      the invariant. No `Result<T, String>` in library or domain code.
- [ ] Parameters take `&str`, `&[T]`, and `Option<&T>`. Numbers carry a unit
      or are a `Duration`.
- [ ] Each new or changed module has a `//!` line, and each item used from
      another module has a `///` comment that says what the signature cannot,
      with `# Errors` and `# Panics` where they apply.
- [ ] Suppressions use `#[expect(..., reason = "...")]`.

## When reviewing

Report layout and import problems as one `nit` per file, naming the rustfmt or
Clippy setting that would prevent them, instead of commenting on each line.
Raise these to `should`:

- a missing or misleading doc comment on an item another module or crate uses
- names that hide what a function does, or values named after their type
- `unwrap` on runtime input, I/O, or configuration
- stringly typed errors (`Result<T, String>`) in domain or library code
- tuples or `bool` parameters whose meaning the call site cannot show

Report structure that hides a bug, such as an index that can panic or a lock
held across `.await`, as that bug, not as style. Green checks are not evidence
of good naming, documentation, or structure.
