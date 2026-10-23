---
name: vitest-testing
description: Create, refactor, review, or explain TypeScript tests with Vitest for backend services and frontends, including fake-first test doubles, factories and fixtures, test.extend, fake timers, framework testing modules, HTTP/e2e tests, and test categorisation. Use for any Vitest test work.
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# Vitest Testing

Keep tests behaviour-focused, readable, and at the lowest boundary that can
prove the contract. Pair with `typescript` for test types and fakes, and with a
framework skill (such as `nestjs`) for framework wiring.

## Core preferences

- Prefer real domain objects and application services over mocks.
- Prefer fakes over mocks when a dependency has meaningful behaviour or state.
- Use `vi.fn()` or `vi.spyOn()` when an outbound interaction is the behaviour
  under test (publishing an event, sending an email, an HTTP call, a retry), or
  when an exceptional path is hard to trigger with a fake.
- Do not assert internal method calls, private state, or internal hook calls
  unless the interaction itself is the contract.
- Give each test fresh mutable state. Prefer explicit setup to hidden magic.
- Tell the story through test names and structure (Arrange, Act, Assert). Add
  comments only for business rules, regressions, races, or non-obvious setup.

## Test doubles

- **Fake:** a small, behaviourally honest implementation of a port (repository,
  queue, clock, external client) that is reused across tests.
- **Stub:** returns fixed data when behaviour does not matter to the test.
- **Mock/spy:** verifies an outbound side effect.

## Reusable support grows from duplication

1. Inline setup in one test.
2. A local helper in the test file.
3. `beforeEach` in one `describe` block.
4. A shared factory or fake under the repository's test-support folder once it
   is reused across files.
5. A `test.extend` fixture only when fixture-style setup is reused and clearer.

Do not create support folders up front. Avoid giant shared fixture files.

## Categories

- **Unit:** domain logic and application services by direct construction, with
  no framework start-up.
- **Thin integration:** parts of one service together, such as a service with an
  in-memory repository, or dependency-injection composition.
- **E2E:** the whole app through HTTP/GraphQL, usually with fake infrastructure.
- **System/smoke:** deployed environments. These run separately from the default suite.

Keep categories separable by directory or script when the repository does.

## Backend services

- Construct use cases directly for unit tests.
- Use the framework's testing module (for example NestJS `TestingModule` with
  `overrideProvider`) only when framework wiring or behaviour matters.
- Use HTTP-level tests (for example `supertest`) for request/response mapping,
  serialisation, and schema coverage.
- Read [references/backend-examples.md](references/backend-examples.md) for
  factories, fakes, stubs, `test.extend`, provider overrides, and e2e examples.

## Frontends

- Test domain transformations and workflows as plain TypeScript.
- Test API parsers, response normalisation, and header propagation directly.
- Test hooks and components only when rendering, lifecycle, accessibility, or
  user interaction is the behaviour.
- Use fake timers for polling, retry, timeout, and delayed state. Advance time
  explicitly, and cover stale or overlapping responses when async work can race.
- Restore globals, timers, and mocks in cleanup.

## Boundaries and regressions

- Cover malformed or partial responses, non-success status codes, and safe error mapping.
- Assert propagation of trace, correlation, and request IDs where an adapter owns those headers.
- Add a regression test for each fixed user-visible or contract bug.

## Workflow

1. Inspect the production boundary and the behaviour worth protecting.
2. Choose the smallest test category that gives confidence.
3. Write or adapt the test. For new behaviour, see it fail for the intended reason first.
4. Run focused files while iterating, then the repository's full check command.
