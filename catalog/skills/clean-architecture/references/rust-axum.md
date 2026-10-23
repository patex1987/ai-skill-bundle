# Clean Architecture in Rust/Axum

- Keep domain rules as ordinary, synchronous Rust functions and types, without
  Axum, Tokio timers, environment access, or telemetry SDKs.
- Handlers parse and validate transport input with extractors, invoke one
  operation, and map the result. `IntoResponse` and status codes stay at the HTTP boundary.
- Prefer plain functions and concrete structs first. Introduce a small trait,
  a function parameter, or an enum only for a real boundary or useful substitution.
  Avoid universal repository traits and service base abstractions.
- Choose generics or trait objects from real ownership and dispatch needs.
  Add `Arc`, `Send`, `Sync`, and async bounds where sharing and execution require
  them, not by habit in pure domain values.
- Do not expose a full SDK client, the router state, or a database pool through a
  domain API. The consumer owns the port and an outer adapter implements it.
- Use typed errors to clarify invariants. Preserve the distinction between
  infrastructure failures and domain failures, and return safe public errors.
- Keep I/O asynchronous and bounded at the adapter/application boundary. Do not
  introduce async traits speculatively.
- The composition root (`main.rs` or a `startup` module) wires adapters into
  router state and owns graceful shutdown and telemetry flushing.
- Do not split a small service into several crates or a four-layer tree. A module
  with pure functions and a thin handler can already have sound boundaries.
