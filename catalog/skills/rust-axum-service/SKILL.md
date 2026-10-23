---
name: rust-axum-service
description: Implement, refactor, review, or explain Rust HTTP services built on Axum and Tokio, including typed Serde request/response contracts, extractors, router state, error enums and IntoResponse mapping, timeouts and cancellation, bounded inputs, OpenTelemetry tracing and metrics, and graceful shutdown.
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# Rust Axum Service

Write idiomatic Rust, and keep the service small enough that its behaviour stays
obvious. Use `clean-architecture` for boundary decisions and `rust-testing` for tests.

## Rust design

- Model bounded states and failure types with enums, not free-form strings.
- Use typed request/response structs with Serde at the HTTP boundary.
- Use `Result`, `Option`, and `?` for expected absence and failure. Map errors to
  a stable, safe HTTP contract at the edge.
- Avoid `unwrap()`/`expect()` on runtime input and external operations.
- Borrow when practical. Clone only when ownership or async lifetimes justify
  it, and do not optimise allocation without evidence.
- Introduce traits for real swappable boundaries, not for every function.

## Axum boundary

- Keep extractors, headers, query parsing, status codes, and response mapping in
  handlers or HTTP adapters. Keep business decisions in plain modules that do not
  depend on Axum.
- Expose a router-building function that tests can call in-process.
- Bound query limits and user-controlled strings before doing work or allocating.
- Keep health and readiness cheap and deterministic.

## Tokio and lifecycle

- Do not block the runtime with synchronous network or filesystem work. Use
  `spawn_blocking` deliberately when there is no async alternative.
- Put timeouts around external I/O. Use bounded channels when background work
  needs backpressure.
- Prefer structured task ownership, explicit cancellation, and graceful shutdown.
- Flush telemetry on shutdown, but do not let an exporter failure block termination indefinitely.

## Errors and security

- Separate safe client-facing errors from internal diagnostic context.
- Do not log secrets, full provider payloads, or unbounded request content.
- Validate configured endpoints and propagated headers.
- Never let request metadata select internal behaviour such as fault injection,
  data snapshots, or feature switches unless that is an explicit, authenticated contract.

## Observability

- Extract W3C trace context at the inbound boundary, and keep correlation fields in spans and logs.
- Use low-cardinality metric attributes (route, outcome, status class). Keep
  request, trace, and user IDs out of metric labels.
- Record enough duration and outcome evidence to explain slow and failed paths.

## Workflow

1. Inspect the current route and response contract.
2. Identify ownership, compatibility, and failure semantics.
3. Change the smallest handler, domain, or telemetry boundary.
4. Add focused tests for normal, invalid, and failure behaviour.
5. Run `cargo fmt --all -- --check`, `cargo clippy --all-targets -- -D warnings`,
   and `cargo test --all-targets`, or the repository's equivalents.
