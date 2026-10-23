---
name: frontend-clean-architecture
description: Use when designing, refactoring, or reviewing frontend architecture with React or other UI frameworks, especially when separating domain logic, use cases, hooks/controllers, presenters, API clients, runtime validation, and UI components.
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# Frontend Clean Architecture Skill

Use this skill for frontend work where UI code risks absorbing business logic, data-fetching details, validation, cache invalidation, or external-service coupling.

The goal is not to force a backend-shaped architecture onto the browser. The goal is to keep domain rules testable, keep external services at boundaries, and let components render state instead of owning business decisions.

## Core Rule

Dependencies point inward:

```text
domain <- application/use cases <- adapters/controllers/presentation <- framework/runtime
```

Frontend mapping:

- **Domain**: entities, value objects, domain types, pure transformations, domain errors.
- **Application**: use cases, commands, ports, DTOs, application services.
- **Adapters**: React hooks, controllers, presenters, API clients, storage adapters, notification adapters, payment adapters, query/cache wrappers.
- **UI**: components that render data and emit events.
- **Platform**: app-wide browser/runtime integrations such as generic HTTP clients, observability propagation, environment config, storage primitives, router/query providers, and SDK setup.
- **Composition root**: app bootstrap, providers, dependency context, router setup, query client setup.

React, browser APIs, HTTP clients, query caches, local storage, timers, analytics, and SDKs are outer details.

## Pragmatic Default

For durable frontend features:

1. Extract reusable domain rules into framework-free code.
2. Preserve dependency direction so external services adapt to the application.
3. Add use cases, ports, controllers, presenters, API clients, runtime schemas, or dependency injection only when workflow complexity justifies the cost.

Do not start every screen with a full architecture scaffold. A prototype can begin as one component, but once the feature becomes durable, edit it toward smaller responsibilities.

## Domain Guidance

Keep domain code boring and portable:

- no React imports
- no browser APIs
- no HTTP/query client imports
- no `localStorage`
- no analytics or notifications
- no `Date.now()`, `new Date()`, random IDs, or global mutable state inside pure transformations
- no display-only formatting unless it is a real domain rule

Prefer pure transformations:

```ts
export function createOrder(
  user: User,
  cart: Cart,
  createdAt: DateTimeString
): Order {
  return {
    userId: user.id,
    products: cart.products,
    createdAt,
    status: 'new',
    total: totalPrice(cart.products),
  };
}
```

Create time, IDs, and external data in a use case or adapter, then pass the completed values into the domain.

## Application and Ports

Use cases coordinate side effects around domain transformations:

```text
side effect -> pure domain transformation -> side effect
```

Put feature-specific dependency contracts under the application feature that owns the use case. Outer adapters implement those contracts.

Use application ports for persistence, network calls, clocks, ID generation, query/cache invalidation, workers, notifications, payments, and browser storage.

Only put an interface in the domain when the domain model itself needs that contract to express a domain rule.

## React Hooks

React hooks are good adapters/controllers. Prefer this shape for non-trivial workflows:

```text
component -> controller hook -> use case -> domain
                         \-> adapters through ports
```

Avoid making a hook the only implementation of a business use case if the workflow needs isolated tests or reuse outside React.

Use case:

```ts
type CheckoutDeps = {
  payment: PaymentPort;
  orders: OrderRepository;
  cart: CartRepository;
  notifier: NotificationPort;
  clock: Clock;
};

export async function checkout(command: CheckoutCommand, deps: CheckoutDeps) {
  const order = createOrder(command.user, command.cart, deps.clock.now());

  const paid = await deps.payment.tryPay(order.total);
  if (!paid) {
    deps.notifier.notify('Payment failed');
    return;
  }

  await deps.orders.save(order);
  await deps.cart.clear();
}
```

Hook adapter:

```ts
export function useCheckout() {
  const deps = useCheckoutDependencies();

  return {
    checkout: (command: CheckoutCommand) => checkout(command, deps),
  };
}
```

For React Query or similar libraries:

- API client fetches and validates.
- Controller hook owns query/mutation setup, loading/error exposure, and cache invalidation.
- Component renders state and calls callbacks.
- Domain and use cases do not import the query client.

## Components, Controllers, Presenters

Components should trend toward humble views:

- receive data
- render markup
- expose events through callbacks
- avoid direct HTTP calls
- avoid business transformations in JSX
- avoid runtime schema validation
- avoid cache invalidation details

Use controller hooks for lifecycle, event handling, use-case calls, query state, and navigation side effects.

Use presenters or view-model mappers when display data needs shaping:

```text
domain/application state -> presenter -> view model -> component
```

UI-only labels, relative-time strings, and display grouping can live in presenters. Business calculations belong in domain or application code.

Use guard clauses and child components to reduce nested conditional JSX.

## API and Trust Boundaries

Treat external runtime data as untrusted until an adapter validates and maps it:

```text
HTTP response -> schema parse -> DTO mapping -> application/domain model -> view model
```

Guidelines:

- Validate API responses, browser storage, URL params, feature flags, SDK payloads, and file inputs at the boundary.
- Do not use TypeScript casts as runtime validation.
- Prefer explicit API fields or discriminated unions over `null` used as an implicit signal.
- Let the backend own authorization and data-eligibility decisions; let the frontend decide how to render returned state.
- Centralize endpoint paths and query keys near the API/query adapter.
- Keep transport retries, headers, and error normalization outside JSX.

API client boundary:

```ts
const endpoints = {
  activePrompt: '/prompts',
  createAnswer: '/prompts',
} as const;

export async function getActivePrompt(): Promise<Prompt> {
  const response = await api.get(endpoints.activePrompt);
  return promptSchema.parse(response.data);
}
```

## Folder Structure

Layer-first is fine for teaching or small apps:

```text
domain/
application/
adapters/
ui/
```

Prefer feature-first for larger frontends:

```text
features/checkout/domain
features/checkout/application
features/checkout/adapters
features/checkout/ui
platform/api
platform/observability
```

The dependency rule matters more than folder names.

Use `platform/` for app-wide frontend runtime code that is reused across features but is not business logic:

- `platform/api/`: generic HTTP, GraphQL, or SDK transport primitives.
- `platform/observability/`: trace, correlation, request-id, logging, and metrics propagation helpers.
- `platform/config/`: runtime environment and feature-flag access.
- `platform/storage/`: low-level browser storage adapters.

Feature-specific adapters still belong inside the feature, for example `features/orders/adapters/orders-api.ts`. Domain and application code must not import from `platform/`; feature adapters, UI composition, and app bootstrap may.

Avoid vague catch-all names such as `utils`, `helpers`, `tools`, or broad `shared` folders without clear segment ownership. If a project already uses `shared`, keep it only when its subfolders have explicit purposes such as `shared/api` or `shared/ui`; prefer renaming to `platform` when the code is mainly app-wide runtime integration.

## Review Checklist

- Domain code imports no React, browser, HTTP, query-cache, or storage details.
- Domain and application code do not import from `platform/`.
- Domain transformations are pure where practical.
- Use cases coordinate workflows and depend on ports, not concrete services.
- Ports live with the application feature unless the domain truly needs them.
- Hooks/controllers adapt React lifecycle and state to use cases.
- Components render data and call callbacks.
- API/storage/SDK adapters validate external data at trust boundaries.
- App-wide runtime code is grouped under purpose-specific `platform/` segments, not generic utility folders.
- Presenters/view models own display shaping; business rules are not hidden in JSX.
- Query keys, endpoints, and cache invalidation are centralized in adapter/controller code.
- Architecture is proportionate to feature complexity and bundle/onboarding cost.

## Anti-Patterns

- Fetching directly in durable components.
- Putting payment, order, permission, pricing, or game rules in JSX.
- Importing React or browser APIs from domain modules.
- Calling SDKs directly from use cases instead of through ports.
- Treating `as SomeType` as validation of server data.
- Using `null` or empty arrays as hidden business flags when an explicit field is needed.
- Creating shallow wrappers that hide almost no complexity.
- Splitting by layers mechanically while features still depend on each other in uncontrolled directions.
