# Clean Architecture in TypeScript/NestJS

- `domain/`: entities, value objects, branded identifiers, state transitions, and
  domain errors. No imports from `@nestjs/*`, GraphQL, ORMs or query builders,
  database drivers, or telemetry SDKs.
- `application/`: use cases and orchestration. Each feature owns its ports
  (for example `application/<feature>/ports/`) for persistence, clocks, ID
  generation, workers, telemetry, and external services.
- `infrastructure/`: concrete database, authentication, observability,
  configuration, and external-service adapters.
- `presentation/`: HTTP controllers, GraphQL resolvers, DTOs/models, middleware,
  and mapping between transport and application types.
- `di/` (or the module files): NestJS modules, provider tokens, lifecycle hooks,
  and composition profiles, such as choosing in-memory or database adapters.

Notes:

- Bind ports with injection tokens (a `Symbol` or string constant) plus
  `useClass`/`useFactory`. Do not inject concrete adapters into use cases.
- GraphQL object models, database rows, and domain objects are separate types
  when their contracts evolve independently.
- Guards, interceptors, and pipes are delivery concerns. They may authenticate
  and shape requests, but authorization *policy* about domain ownership belongs
  in the application layer, where it can be tested.
- Background workers are delivery adapters too. Claims, heartbeats, retries, and
  terminal states are application contracts, not worker-loop details.
