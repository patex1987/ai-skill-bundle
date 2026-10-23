---
name: nestjs
description: Implement, refactor, or explain NestJS service code, including modules, providers and injection tokens, controllers, GraphQL resolvers, DTOs, validation, guards and interceptors, and NestJS testing. Pair with clean-architecture for layer boundaries.
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# NestJS

Treat NestJS as the delivery and composition framework, not the whole
architecture. Use `clean-architecture` as the source of truth for layers, and
`typescript` for type design.

## Core principles

- Keep decorators and framework classes at the presentation and composition edges.
- Keep controllers and resolvers thin: parse input, call a use case, map output.
- Put business decisions in domain entities or application use cases.
- Put persistence and third-party integrations in infrastructure adapters.
- Bind application ports to implementations with provider tokens.
- Prefer composition over inheritance, explicit parameter and return types, and
  focused types over `any`.
- Follow the repository's naming conventions. NestJS defaults are PascalCase
  classes, camelCase members, and kebab-case files.

## Structure

Place NestJS-specific files at the edges of the layered structure. A typical shape:

```text
src/
  app.module.ts
  main.ts
  presentation/
    http/        controllers, health/readiness endpoints
    graphql/     resolvers, object models, input classes
  di/            modules, provider tokens, composition profiles
```

Create only the folders the current feature needs. Do not put business
behaviour in controllers, resolvers, guards, or interceptors.

## GraphQL

- Preserve the existing approach (code-first or schema-first) and its generated
  schema configuration unless a coordinated contract change alters them.
- Map GraphQL inputs to application input types. Do not pass framework DTOs into the domain.
- Classes and decorators exist for runtime schema metadata. Interfaces disappear
  at runtime, and decorators are not business validation.
- Keep liveness and readiness probes as plain HTTP endpoints, not GraphQL operations.
- Select persistence adapters through composition, never inside resolvers.

## Validation

- Inspect the existing boundary before choosing a mechanism. Do not add
  `class-validator`/`class-transformer`, Zod, or another library just because
  NestJS supports it.
- Keep configuration parsing, transport validation, and domain invariants
  distinct, and do not mix validation styles without a documented reason.

## Shared modules

Add a common/shared module only when duplication or real cross-cutting
behaviour exists: configuration, guards, interceptors, exception filters, or
custom decorators.

## Testing

- Unit test domain objects and use cases without starting Nest.
- Use `Test.createTestingModule` and `overrideProvider` when provider wiring or
  framework behaviour is what you are testing.
- Add HTTP/GraphQL e2e tests once a module has behaviour worth protecting.
- Use the repository's existing test runner. For Vitest specifics, use `vitest-testing`.

## Explaining NestJS

When teaching, explain dependency injection through the concrete providers and
modules involved, explain decorator metadata when you add decorators, and say
whether a construct is compile-time only or exists at runtime.
