# movie-reservation-service: clean-architecture overlay

## Layer paths

- `src/domain/`: reservation entities, value objects, identifiers, state
  transitions, and domain errors. No NestJS, GraphQL, Knex, database, or telemetry SDK imports.
- `src/application/`: use cases. Ports live under `src/application/<feature>/ports/`
  for persistence, clocks, ID generation, workers, telemetry, and external dependencies.
- `src/infrastructure/`: database, authentication, observability, configuration,
  fixture, and external-service adapters.
- `src/presentation/`: HTTP controllers, GraphQL resolvers, DTOs/models, and middleware.
- `src/di/`: NestJS modules, provider tokens, lifecycle integration, and composition profiles.

## Reservation correctness

- Ownership, tenant scope, idempotency, duplicate seat requests, transaction
  boundaries, claims, heartbeats, retries, and terminal states are explicit
  application contracts.
- Do not create repository god objects. Split read, command, and work-claiming
  capabilities when their responsibilities or consistency needs differ.
- Use integration/e2e tests for GraphQL mapping, Postgres transactions,
  concurrency, authentication, and process boundaries.
