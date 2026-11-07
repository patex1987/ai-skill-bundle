# Doc Comments

rustdoc reads `///` (outer) and `//!` (inner) comments as Markdown. Editors
show them on hover, and `cargo doc` renders them. The signature already gives
the types, so a doc comment should explain behaviour.

## What to write

Ask what a caller would get wrong if they had only the signature:

| The signature cannot say | Write |
|---|---|
| Units and ranges | "`ttl` is clamped to between one minute and one hour." |
| Defaults | "Uses a five-minute hold when `ttl` is `None`." |
| Side effects | "Takes the store lock and writes one audit event." |
| Errors the caller should handle | an `# Errors` section, with one line per variant |
| Panics | a `# Panics` section, with the condition |
| Invariants and ordering | "Call `open` first. Calling it twice is safe." |
| Ownership and lifetime | "The returned guard releases the hold when dropped." |
| Why it exists, if not obvious | one or two sentences after the summary |

## Modules

Put one `//!` paragraph at the top of each module file: what the module owns,
and what it deliberately does not do.

```rust
//! Seat holds: placing, looking up, and expiring temporary seat reservations.
//!
//! Holds live in memory only. Persisting a confirmed booking is the job of
//! `booking`.
```

## Functions

```rust
/// Places a hold on the requested seats for the tier's hold duration.
///
/// Seats are trimmed and empty entries are ignored, so `"A1, ,A2"` requests two
/// seats.
///
/// # Errors
///
/// - [`HoldError::SeatCountMismatch`] when the number of parsed seats differs
///   from `expected_count`.
/// - [`HoldError::NoSeats`] when no seat remains after trimming.
pub(crate) fn place(&mut self, seats: &str, expected_count: usize, tier: Tier) -> Result<HoldId, HoldError> {
```

Avoid comments like these:

```rust
/// place
pub fn place(...)

/// Creates a new HoldStore.          // restates `new` on `HoldStore`
pub fn new() -> HoldStore

/// Returns a Result<String, String>. // restates the signature
```

A constructor or getter whose name says everything can go without a comment in
application code. In a library, `missing_docs` requires one, so write a short
summary.

## Types, fields, and variants

Document the type's meaning and invariants. Document a field or variant when its
name and type leave a question open (units, who sets it, when it is `None`).

```rust
/// A temporary claim on seats that expires unless it is confirmed.
pub(crate) struct Hold {
    pub(crate) id: HoldId,
    pub(crate) seats: Vec<SeatId>,
    /// When the hold lapses. Expired holds are ignored by `active` and removed
    /// by `release_expired`.
    pub(crate) expires_at: SystemTime,
}
```

Self-explanatory enum variants need no comment.

## `unsafe`

An `unsafe fn` or `unsafe trait` needs a `# Safety` section that states what
the caller must guarantee. Each `unsafe { }` block needs a `// SAFETY:`
comment above it that explains why those guarantees hold at this point.

## Implementation comments

Use `//` for reasons, constraints, and workarounds:

```rust
// The lock is released before logging so that a slow log sink cannot block
// other requests.
drop(holds);
```

Do not narrate code (`// increment counter`), and do not leave commented-out
code. A `TODO` names an issue: `// TODO(#42): persist holds across restarts.`

You can mix `///` and `//` on one item. The `//` lines do not appear in the
rendered docs:

```rust
/// Releases every hold whose expiry has passed.
// TODO(#42): emit an event per released hold.
pub(crate) fn release_expired(&mut self, now: SystemTime) -> usize {
```
