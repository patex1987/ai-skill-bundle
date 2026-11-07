# Sources

The text of this skill is original. The ideas below come from the style guides
and tool documentation listed here, which were read on 2026-11-07. Nothing was
copied verbatim.

| Source | Licence | Ideas adapted |
|---|---|---|
| [The Rust Style Guide](https://doc.rust-lang.org/nightly/style-guide/) | MIT or Apache-2.0 | The default style that rustfmt follows; zero or one blank lines between items; `use` and `mod` before other items; tools never merge or reorder import groups; casing table; `r#crate` or `crate_`, never `krate`; avoid `#[path]`; prefer expressions; `//` over `/* */`, `///` over `/** */`, `//!` only for modules and crates; comments as sentences within 80 columns; doc comments before attributes; one `derive`; style editions |
| [Google Rust Style Guide](https://google.github.io/styleguide/rustguide.html) | CC-BY 3.0 | Apply API rules in context (application code favours directness); no glob imports, with exceptions; one module per `use`; types unqualified, functions qualified by module; locally scoped trait imports; file named after its main type; parent modules hold declarations and re-exports; borrowed parameter types; borrow before clone; enum over `bool` parameters; `Option`, `Result`, `panic!` split; newtypes; named fields over tuples; implement standard traits; traits only for generics, `dyn`, or extension; `Ext` suffix; getter, setter, and constructor names; descriptive lifetimes; no letter-deleting abbreviations; doc comments say what the code cannot; `# Panics`; `SAFETY:` comments; `#[must_use]`; explicit types on `.parse()`, `.into()`, and long chains; match over check-then-unwrap; `expect` over `unwrap`; assertion messages that explain; short iterator chains and no `for_each`; `format!` over `+`; never reach into a poisoned mutex; macro preference order; `#[rustfmt::skip]` only for alignment |
| [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/naming.html) | MIT or Apache-2.0 | `as_`, `to_`, `into_` conversions; no `get_` prefix on getters |
| [rustdoc book](https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html) | MIT or Apache-2.0 | Summary line, then `# Errors`, `# Panics`, `# Safety`, `# Examples` |
| [Clippy lint list](https://rust-lang.github.io/rust-clippy/master/index.html) and [configuration](https://doc.rust-lang.org/clippy/lint_configuration.html) | MIT or Apache-2.0 | Lint names and `clippy.toml` keys in the recipe, checked by running them on 2026-11-07 |
| [rustfmt configuration](https://rust-lang.github.io/rustfmt/) | MIT or Apache-2.0 | `style_edition`; `imports_granularity` and `group_imports` are nightly-only, confirmed on stable 1.96.1 |

## Google rules left out

These depend on Google's environment and do not fit standalone Cargo
applications:

- **Chromium:** small crates and a flat, single-directory layout (deliberately
  unlike Cargo); `chromium::import!`; `git cl format`; no `async`/`.await`; no
  `std` threads; `rust_gtest_interop` tests.
- **Fuchsia and Android:** `fuchsia_sync::Mutex`, `#[fuchsia::test]`, and their
  unstable-feature exceptions.
- **Build and interop:** `genrule` code generation; C++ namespace globs and
  `cxx` bridge exceptions.
- **Monorepo policy:** `#[non_exhaustive]` on every shared enum and struct (kept
  only for published libraries); extension traits owned by the type's team;
  reasoning based on large-scale changes; per-codebase test frameworks.
- **`panic=abort` context:** the `catch_unwind` ban is still sensible, but the
  reason differs. Tokio already isolates a panicking task.

## Where this skill differs

- **`Arc` for shared state.** Google says to avoid `Rc` and `Arc` unless the
  alternative is unreasonably complex. Axum and Tokio need `Arc` for
  application state and spawned tasks, so this skill accepts it there and
  objects only where single ownership would work.
- **Doc requirements by crate type.** Google asks for docs on public APIs. A
  service is usually a binary crate where nearly everything is `pub(crate)`.
  This skill therefore requires `//!` on every module and `///` on items used
  across modules, and the recipe phases in `missing_docs_in_private_items`.
- **Blank lines and import groups as rules.** Both guides leave them to the
  author. This skill makes them explicit, because rustfmt never adds blank
  lines, and stable rustfmt cannot group imports.
- **Errors.** Neither guide discusses `anyhow` or `thiserror`. This skill
  confines catch-all error types to the binary's edges, which matches common
  Axum and CLI practice.
