---
name: pytest-testing
description: Create, organise, refactor, review, or explain Python tests with pytest, including fake-first test doubles, fixtures and conftest placement, async tests with pytest-asyncio, FastAPI/httpx API tests, httpx.MockTransport adapter tests, CLI tests, and required failure-path coverage. Use for any pytest work.
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# pytest Testing

Keep tests behaviour-focused, fake-first, offline by default, and organised
around the boundary that can fail. Pair with `python-tooling` for commands and
dependencies, and with `fastapi-service` or `python-mcp-service` for framework details.

## Core preferences

- Prefer real domain objects and services over mocks. Prefer fakes when a
  dependency has state or meaningful behaviour: persistence, queues, event logs,
  clocks, workers, external clients, or auth providers.
- Use `Mock`/`AsyncMock` or a small spy when the outbound interaction is the
  contract, or when a failure is hard to trigger with a fake.
- Test observable behaviour: return values, persisted state, emitted events,
  HTTP responses, exit codes, and lifecycle effects. Avoid tests that only prove
  mocks were passed around.
- Prefer plain test functions and fixtures over test classes, unless the
  repository already uses classes or `unittest.TestCase` (pytest runs both).

## Layers

| Layer | Scope | Notes |
|---|---|---|
| Unit | Domain logic and services by direct construction | No app, database, or DI container |
| Thin integration | Several in-process parts together | Service plus in-memory store, consumer plus queue |
| API / contract | FastAPI `TestClient` or `httpx.AsyncClient` over ASGI, or decorated tool functions with fake clients | Validation, status codes, DTOs, auth, error mapping |
| Adapter | One concrete adapter at its I/O boundary | `httpx.MockTransport`, temporary directories, controlled subprocess results |
| Infrastructure / smoke | Real resources or running services | Marked and run separately, never in public CI against live cloud accounts |

## Required failure coverage at boundaries

- Invalid or blank identifiers, empty collections, and out-of-range values.
- Connection failures, timeouts, and non-success status codes.
- Non-JSON, wrong-shape, and missing-field responses.
- Allowed propagation headers present, and blank or disallowed values omitted.
- Stable, safe error envelopes that do not leak raw exceptions or downstream bodies.
- For validators: a negative test for every tightened rule, and a regression
  test for every fixed bug.

## Fixtures and conftest

- Default to function-scoped fixtures for mutable state. Use `yield` fixtures
  for resources that need cleanup.
- Avoid `autouse=True` unless the effect is truly cross-cutting and obvious, and
  avoid fixture chains that hide the scenario.
- Grow support from duplication: inline setup, then a local helper or fake, then
  a folder-level `conftest.py`, then a shared fakes package, then a higher
  `conftest.py`. Never start with a large root `conftest.py`.
- Name fixtures after the role they play in the test.
- Use `pytest.mark.parametrize` only when every row protects the same behaviour.

## Async

- Mark async tests (`pytest.mark.asyncio`, or the repository's configured mode).
- Make concurrency deterministic with `asyncio.Event`, controlled fakes, and
  `asyncio.wait_for`. Avoid arbitrary sleeps.
- Cancel and await background tasks in `finally`, and close async clients
  explicitly, so work does not leak between tests.

## Workflow

1. Inspect the production boundary and the observable behaviour worth protecting.
2. Choose the smallest layer that gives confidence.
3. Construct the real subject, adding fakes only where state matters.
4. For new behaviour, see the test fail for the intended reason first.
5. Run focused tests, then the repository's full check.

Read [references/examples.md](references/examples.md) for fakes, spies, narrow
mocks, dependency overrides, folder-level conftest, and async event-driven tests.
