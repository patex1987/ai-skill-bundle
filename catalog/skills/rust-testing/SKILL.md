---
name: rust-testing
description: Create, organise, refactor, review, or explain Rust tests for services and libraries, including pure unit tests, table-driven cases, in-process Axum router tests with tower::ServiceExt, tokio::test with paused time, trace and metric contract tests, and process/container smoke tests.
license: MIT-0
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# Rust Testing

Choose the smallest test boundary that proves the behaviour. Before refactoring,
treat the existing router and failure-path tests as the regression suite.

## Layers

- **Unit:** domain rules, bounds and defaults, parsing, and response/error mapping
  as ordinary functions (`#[cfg(test)] mod tests`).
- **Handler:** call an in-process Axum `Router` with `tower::ServiceExt::oneshot`
  and assert status, headers, and JSON without binding a port.
- **Async:** use `#[tokio::test]` only when the behaviour is genuinely async.
- **Integration:** `tests/` crates for public API behaviour across modules.
- **Smoke:** start the built binary or container separately to check health,
  readiness, shutdown, and exporter configuration.

## Determinism

- Use table-driven cases for bounds, defaults, and enumerated outcomes.
- Use paused Tokio time (`start_paused = true`, `tokio::time::advance`) for delays and timeouts.
- Avoid real sleeps, randomness without a fixed seed, and external network calls in ordinary tests.
- Give each test fresh state. Serialise only tests that truly share global
  telemetry or process state.
- Do not make statistical assertions about random behaviour. Inject the source of randomness instead.

## Observability

- Test `traceparent` parsing, including rejection of malformed and all-zero IDs.
- Test metric attribute construction as bounded data rather than relying on a live collector.
- Keep exporter integration as a separate smoke boundary.

## Failure coverage

- Invalid and extreme inputs, plus missing or malformed propagation headers.
- Every enumerated error variant and its public mapping.
- Telemetry disabled, and exporter setup failure.
- Graceful shutdown and health/readiness contracts when they change.

Run focused tests while developing, then `cargo fmt --all -- --check`,
`cargo clippy --all-targets -- -D warnings`, and `cargo test --all-targets`.
