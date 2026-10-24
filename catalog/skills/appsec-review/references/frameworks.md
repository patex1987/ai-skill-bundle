# Framework Enforcement Points

Find where each framework actually enforces identity, authorization,
validation, and output filtering. Check global configuration before calling a
handler unprotected, and look for alternate routes that skip the protection.
Check the framework version in the lockfile. Defaults change between major
versions.

Trace each sensitive entry point along this path:

```text
caller-controlled input -> verified identity -> authorization + validation
                        -> data access or external effect -> serialized output
```

## Next.js and React

- Server actions and route handlers are public endpoints. Each must check
  identity and object access itself, because a layout or middleware check
  does not protect a directly called action.
- Middleware matchers can miss paths (locale prefixes, `_next` routes, trailing
  slashes). Never rely on middleware alone for authorization.
- `NEXT_PUBLIC_*` values are shipped to browsers. Server-only modules should
  import `server-only`.
- Data passed from server to client components is serialized to the browser.
  Look for whole records with private fields.
- Caching and revalidation: a response cached for one user and served to
  another. Behaviour depends on the version and on per-route config.
- XSS: React escapes by default. Investigate `dangerouslySetInnerHTML`,
  Markdown renderers that allow raw HTML, and user-supplied `href` values.

## NestJS

- Global guards (`APP_GUARD`) vs. per-controller and per-method guards.
  Public-route metadata (`@Public()` style decorators) and how the guard reads
  it.
- GraphQL resolvers and field resolvers need guards too. Check the context
  extraction for GraphQL vs. HTTP.
- `ValidationPipe` with `whitelist` and `forbidNonWhitelisted`, DTO
  `transform`, and mass assignment through spread or `Object.assign` into
  entities.
- Tenant and owner predicates in services and repositories. The guard
  authenticates, the query must authorize.
- Webhook handlers: raw-body signature verification before parsing, timestamp
  and replay checks, and idempotency.
- Exception filters that leak stack traces or internal messages, and
  interceptors that log request bodies with secrets.

## FastAPI

- `Depends`/`Security` on the router or the route. Find sensitive routes that
  are missing them, especially routes added to a different router.
- `app.dependency_overrides` in tests can hide missing production
  dependencies. Check that tests exercise the real dependency for at least the
  denial case.
- Pydantic validates shape, not ownership. Check `response_model` filtering,
  and partial updates via `model_dump(exclude_unset=True)` applied to ORM
  objects.
- Raw SQL with f-strings and `text()` built from input. Also `subprocess` with
  `shell=True`, `yaml.load`, and `pickle`.
- `httpx` and `requests` with user URLs (SSRF), and blocking calls inside
  `async` handlers on hot paths (availability, if in scope).
- CORS with `allow_credentials=True` and broad origins.

## Axum and Rust

- Router nesting and layer order: a `route_layer` or `layer` applied before or
  after `nest` and `merge` changes which routes are protected. Check fallback
  handlers.
- Identity must come from a verified extractor or middleware. Request headers
  such as `X-User-Id` are not identity unless a trusted proxy sets them and
  strips client values.
- Tenant predicates in `sqlx` and Diesel queries, and `format!` used to build
  SQL.
- `unwrap`/`expect`/indexing on attacker-controlled input in a shared
  service, body-size limits, and `unsafe` or FFI blocks.
- Secrets printed through `Debug` derives, tracing spans, and error bodies.
  Use secrecy wrappers.
- `reqwest` redirect policy and URL validation for outbound requests.

## AWS CDK, ECS, Lambda, EventBridge

- Review the synthesized template (`cdk.out/*.template.json`) as well as the
  construct code. Grants (`grantReadWrite`, `addToPolicy`) often widen access
  more than the code suggests.
- `cdk synth` runs application code and may perform lookups. Run it in a
  sandbox without credentials, or review a synthesized template from CI.
- Task and execution roles: least privilege, no shared admin roles, and secrets
  through Secrets Manager or SSM references rather than plain environment
  values.
- Load balancer listeners and security groups: what is internet-facing, and
  whether ECS tasks are in private subnets.
- EventBridge and SQS resource policies, cross-account principals, and
  consumers that treat event fields as authenticated identity.
- `RemovalPolicy` and deletion protection on stateful resources, and
  replacements that destroy data.

## GitHub Actions

- Triggers: `pull_request_target`, `workflow_run`, `issue_comment`, and who can
  fire them. Forks get no secrets on `pull_request`, but the privileged
  triggers run with base-branch secrets.
- `permissions:` at workflow and job level. The default token scope depends on
  repository settings, so state the assumption.
- `${{ }}` expressions inside `run:`, `actions/github-script`, and composite
  actions.
- Third-party actions pinned by SHA, reusable workflows, and self-hosted
  runners exposed to fork PRs.
- OIDC to cloud: trust-policy `sub` conditions bound to a repository, branch,
  or environment, and environment protection rules.

## Containers

- Base image provenance and pinning, running as a non-root user, and a
  read-only root filesystem where possible.
- Secrets in `ARG`/`ENV` or copied files (they persist in layers).
  `.dockerignore` coverage of `.env`, `.git`, and credentials.
- Exposed ports and debug endpoints in production images.

## Other stacks

For a framework not listed, find the equivalents before reviewing:
- where routes are registered
- how authentication middleware attaches identity
- the authorization hook
- the validation layer
- the ORM's raw-query escape hatches
- the template engine's escaping rules
- the outbound HTTP client
