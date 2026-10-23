---
name: clean-architecture
description: Design, review, or refactor dependency direction and ownership boundaries (domain, application/use cases, ports and adapters, presentation, composition root) in services, frontends, CLIs, or automation. Use when deciding where code belongs or whether an abstraction earns its cost; skip mechanical edits with no architectural choice.
license: MIT-0
metadata:
  routing-tier: deep
  routing-effort: high
---

# Clean Architecture

Dependencies point inward, toward plain domain and application behaviour.
Enforce responsibilities before directories. Do not impose a four-layer layout
or new packages on code that a pure function and one adapter already keep clean.

## Responsibility ownership

| Responsibility | Owns | Must not depend on |
|---|---|---|
| Domain | Entities, value objects, identifiers, invariants, state transitions, domain errors | Frameworks, transport, persistence, telemetry SDKs |
| Application | Use cases and orchestration, plus the narrow ports they need (persistence, clock, IDs, queues, external services) | Concrete adapters, transport DTOs |
| Adapters / infrastructure | Databases, HTTP clients, filesystems, message brokers, auth providers, telemetry exporters | Business policy |
| Presentation / delivery | Routes, controllers, resolvers, CLI parsing, request/response DTOs, status codes, error mapping | Business decisions |
| Composition root | Wiring concrete adapters to ports, lifecycle, configuration loading | Runtime business decisions |

## Boundary rules

- Keep handlers thin: validate and map input, call one application operation,
  then map the result or error.
- Let the consumer own the port, and keep it narrow. Avoid universal repository
  interfaces and "god" stores. Split read, command, and work-claiming capabilities
  when their consistency needs differ.
- Keep transport DTOs, persistence rows, and domain objects distinct when they
  change for different reasons. Do not duplicate structs only to show off layers.
- Add an abstraction only for a real boundary, a meaningful substitution, or
  deterministic tests. One implementation and no test seam is a smell.
- Make transaction boundaries, idempotency, retries, ownership/tenant scope, and
  terminal states explicit application contracts.
- Do not turn retryable infrastructure failures into terminal business outcomes,
  and do not leak infrastructure error details to callers.
- Propagate trace and correlation context at the boundaries without coupling
  domain objects to telemetry libraries.
- Keep schema migrations separate from normal application start-up.

## Design pressure checks

- The domain imports a framework, DTO, table, or middleware: the boundary leaks.
- A route or resolver contains policy: move the policy inward.
- An adapter decides business rules: move the rule inward, keep the adapter mechanical.
- A use case needs many unrelated dependencies: split it or narrow its ports.
- Pure business tests need a real database: the dependency boundary is too low.

## Testing

- Test domain rules directly with ordinary values.
- Test use cases with small fakes for meaningful ports.
- Test adapters at the I/O boundary they own, and test delivery mapping in-process.
- Test DI composition only when the wiring itself is the behaviour.

## Refactoring workflow

1. Identify the behaviour and which responsibility owns each decision.
2. Protect the observable behaviour with characterisation tests before moving code.
3. Extract one meaningful boundary at a time, preserving public contracts.
4. Review dependency direction, and whether each new abstraction earns its cost.

Avoid broad rewrites whose main output is a directory diagram.

## Stack notes

Read only the note that matches the code you are changing:

- [references/typescript-nestjs.md](references/typescript-nestjs.md): NestJS layering, provider tokens, GraphQL models.
- [references/python-fastapi.md](references/python-fastapi.md): FastAPI routes, `Depends`, DI containers, ORM tables.
- [references/rust-axum.md](references/rust-axum.md): Axum handlers, traits versus generics, async boundaries.
- [references/automation-and-ci.md](references/automation-and-ci.md): CLIs, CI automation, GitHub Actions, and IaC control-plane code.
