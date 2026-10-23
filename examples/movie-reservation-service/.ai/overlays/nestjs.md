# movie-reservation-service: NestJS overlay

- GraphQL is code-first. Resolvers live in `src/presentation/graphql/`, for
  example `movie-reservations.resolver.ts`, with `models/` (such as `movie.gql.ts`)
  and `inputs/` (such as `request-reservation.input.ts`).
- `/health` and `/ready` are REST controllers in `src/presentation/http/`. Never
  use GraphQL as the ALB, ECS, Docker Compose, or Kubernetes health-check path.
- Persistence is chosen by composition profile (in-memory or PostgreSQL). Resolvers never depend on either.
- Validation: Zod parses environment and configuration. Reservation identifiers,
  ownership, and business invariants use explicit application/domain validation.
  Do not add `class-validator`/`class-transformer`.
- Tests use Vitest, not Jest. Name test variables clearly, for example
  `inputReservationId`, `actualResponse`, `expectedBody`.
- Preserve the established composition, GraphQL, health/readiness,
  authentication, persistence, and worker boundaries unless an issue explicitly changes them.
