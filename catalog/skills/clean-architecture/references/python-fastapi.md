# Clean Architecture in Python/FastAPI

- Domain modules do not import FastAPI, Pydantic transport DTOs, ORM tables
  (SQLAlchemy, Piccolo, and similar), middleware, or the DI container.
- Routes own HTTP translation: request validation, identity extraction, DTO
  mapping, status codes, and translating domain exceptions to HTTP errors.
- Use cases (often a `services/` package) depend on domain objects and narrow
  ports, expressed as `typing.Protocol` classes or plain callables.
- ORM tables and migrations belong to infrastructure. Repository adapters translate
  rows into domain/application objects.
- `Depends` is appropriate for route-local extraction and request-scoped
  assembly. Shared, swappable dependencies belong in the composition root,
  whether that is a DI container (such as `svcs`), registrars, or plain construction
  at start-up. Registrars register dependencies; they do not make business decisions.
- The lifespan handler owns start-up and shutdown. Do not scatter lifecycle work.
- Prefer typed request objects in and typed result objects out for non-trivial
  use cases. Use plain functions for mappers and pure transformations.
- For workers and event logs, preserve append-only semantics, ordering,
  idempotency, and deterministic replay where those invariants apply.

Do not add a DI framework for ordinary construction. Do not pass powerful
mutable stores deep into execution logic when a narrower port, event sink, or
cancellation signal is enough.
