---
name: fastapi-service
description: Write or modify Python FastAPI service code, including routers, Pydantic v2 request/response models, dependency injection with Depends or a DI container, lifespan start-up and shutdown, middleware, error translation, async I/O, and API performance concerns.
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# FastAPI Service

Keep API code aligned with the repository's conventions rather than generic
internet defaults. Use `clean-architecture` for layer placement,
`rest-api-design` for HTTP contracts, and `pytest-testing` for tests.

## Boundaries

- HTTP concerns live in the API layer: routers, request/response models,
  mappers, middleware, status codes, and request-context extraction.
- Keep handlers thin: validate and extract, call one service, map the result to
  a response model.
- Declare `response_model`, summaries, and response metadata on public endpoints.
- Use Pydantic models (or typed dataclasses) for stable interfaces, not raw dicts.
  Never return ORM or persistence objects directly.
- Translate domain exceptions to HTTP errors once, at the boundary.
- Use the `lifespan` handler for start-up and shutdown; do not add new
  `@app.on_event` handlers.

## Dependencies

- Use `Depends` for request-local extraction and route-local assembly.
- If the project has a DI container or registrar pattern (for example `svcs`),
  shared application and infrastructure dependencies belong there. Read the
  project's DI notes before changing wiring, keep registrars mechanical, and do
  not add a second dependency system.
- Avoid hidden global singletons for anything that needs a lifecycle or test override.

## Python style

- Use `async def` for I/O-bound work and `def` for pure synchronous logic.
- Type all public signatures, dependencies, mappers, and test helpers.
- Use guard clauses near the top of functions instead of deep nesting.
- Prefer typed request/result objects for non-trivial calls.

## Errors and logging

- Use domain-specific exceptions for business failures. Keep client-facing
  messages stable and free of internals.
- Log unexpected failures with context, but never tokens, secrets, or sensitive bodies.
- Do not hide actionable failures behind broad exception handlers.

## Async and performance

- No blocking I/O in async handlers or services. Use async database and HTTP
  clients, or offload blocking work explicitly.
- Bound fan-out and background work, and give every background task a lifecycle owner.
- Paginate or project large responses. Preserve latency, throughput, queue-depth,
  and failure observability on hot paths.

## Testing

Test routes for validation, status codes, auth behaviour, and mapping. Test
services with fakes, and cover cancellation, timeouts, retries, and duplicate
processing for async work.
