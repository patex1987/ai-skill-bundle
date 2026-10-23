---
name: rest-api-design
description: Design, review, document, or change REST/HTTP API endpoints, including resource naming, methods, status codes, request/response shapes, pagination, filtering and sorting, versioning and compatibility, authentication boundaries, OpenAPI documentation, error contracts, and API tests. Examples use FastAPI, but the guidance is framework-neutral.
metadata:
  routing-tier: deep
  routing-effort: medium
---

# REST API Design

Use this skill to design resource-oriented HTTP APIs that are consistent, predictable, and safe for clients. For FastAPI implementation details, also use `fastapi-service`. For layering and ownership questions, also use `clean-architecture`.

## Design Defaults

- Use resource nouns, not action verbs.
- Use plural collection names: `/runs`, `/conversations`, `/events`.
- Keep the existing versioned prefix style: `/api/v1/...`.
- Keep nesting shallow. Prefer one nested level; avoid more than two levels unless the relationship is truly scoped.
- Model operations as resource state changes before adding custom action endpoints.
- Be consistent over clever. Similar resources should use similar paths, query parameters, response shapes, and error formats.

## Resource Naming

Good:

```text
GET    /api/v1/runs
POST   /api/v1/runs
GET    /api/v1/runs/{run_id}
GET    /api/v1/runs/{run_id}/events
POST   /api/v1/conversations/{conversation_id}/turns
```

Avoid:

```text
GET    /api/v1/getRuns
POST   /api/v1/createRun
GET    /api/v1/run/{run_id}
POST   /api/v1/runs/{run_id}/do-cancel
```

Custom action endpoints are acceptable when the operation is not naturally CRUD, but name them deliberately and document the semantics. Existing examples such as cancellation should explain whether they create intent, change state synchronously, or start asynchronous work.

## HTTP Methods

| Method | Use for | Idempotency expectation |
| --- | --- | --- |
| `GET` | Read a resource or collection | Yes |
| `POST` | Create a subordinate resource or submit a command/request | Usually no |
| `PUT` | Replace a resource at a known URI | Yes |
| `PATCH` | Partially update a resource | Not guaranteed |
| `DELETE` | Delete/cancel/remove a resource | Should be idempotent |

Do not use `GET` for state changes. Do not overload `POST` for reads just because the query object is large unless there is a clear documented reason.

## Status Codes

Success:

- `200 OK`: successful read or update with response body.
- `201 Created`: successful creation; include the created resource or a stable reference.
- `202 Accepted`: asynchronous work accepted but not complete.
- `204 No Content`: successful delete/cancel/update with no body.

Client errors:

- `400 Bad Request`: malformed input or unsupported query combination.
- `401 Unauthorized`: authentication is missing or invalid.
- `403 Forbidden`: authenticated caller is not allowed to access the resource.
- `404 Not Found`: resource does not exist or should not be revealed to this caller.
- `409 Conflict`: state conflict, duplicate, version mismatch, or idempotency conflict.
- `422 Unprocessable Entity`: FastAPI/Pydantic request validation failure or semantic validation error when this is the project convention.
- `429 Too Many Requests`: rate limit exceeded.

Server and upstream errors:

- `500 Internal Server Error`: unexpected server failure.
- `502 Bad Gateway`: upstream dependency returned an invalid failure.
- `503 Service Unavailable`: temporary overload, maintenance, or dependency unavailable.
- `504 Gateway Timeout`: upstream dependency timed out.

Never return `200` for errors. Translate domain exceptions at the API boundary.

## Request And Response Shapes

- Define request and response DTOs with Pydantic models.
- Use `response_model` on FastAPI routes.
- Return DTOs, not database rows, provider SDK objects, or raw internal domain objects.
- Use stable field names in `snake_case`.
- Use ISO 8601 timestamps, preferably UTC, for date/time fields.
- Do not expose secrets, tokens, raw credentials, internal stack traces, or sensitive provider payloads.
- Prefer object responses over bare arrays when the response needs pagination metadata, links, or future extension.

Collection response pattern:

```json
{
  "items": [],
  "limit": 50,
  "next_cursor": null
}
```

Error response pattern:

```json
{
  "error": "run_not_found",
  "message": "Run not found",
  "details": {}
}
```

Use the project's existing error format when one is already established.

## Pagination, Filtering, And Sorting

- Paginate collection endpoints from the start.
- Prefer bounded `limit` parameters with a clear default and maximum.
- Use cursor pagination for event streams, logs, and high-churn collections.
- Use offset pagination only for small, stable collections where the tradeoff is acceptable.
- Keep filters explicit: `status=running`, `created_after=...`, `created_before=...`.
- Keep sorting predictable: document the default order and allowed sort fields.

Example:

```text
GET /api/v1/runs?status=running&limit=50
GET /api/v1/runs/{run_id}/events?after=42
```

## Authentication And Authorization

- Reuse the repository's authentication middleware and execution/request context instead of adding ad-hoc auth inside routes.
- Keep authentication separate from authorization: identity proves who the caller is; authorization decides what the caller can access.
- Return `401` for missing/invalid credentials and `403` for authenticated-but-not-allowed callers.
- Do not put bearer tokens, API keys, or session identifiers in query parameters.
- Do not hardcode static API keys or secrets in examples or code.
- If API keys are introduced, store only hashes, compare safely, support rotation, and document ownership.
- Ensure resource ownership checks happen before returning resource details.

## Versioning And Compatibility

- Keep public routes under `/api/v1`.
- Prefer additive changes: new optional fields, new endpoints, new enum values only when clients can tolerate them.
- Treat field removals, type changes, required-field additions, and behavior changes as breaking changes.
- For breaking changes, plan a new API version or an explicit migration period.
- Document deprecations and avoid silent contract drift.

## OpenAPI Documentation

- Use `summary`, useful `description`, `response_model`, and `responses` metadata for public routes.
- Include examples for important success and error responses.
- Document asynchronous semantics clearly: accepted, queued, running, terminal states, polling, cancellation, retry, and idempotency behavior.
- Keep generated OpenAPI accurate; stale docs are worse than sparse docs.

## FastAPI Implementation Shape

If endpoint work changes dependency injection, route dependencies, or service
assembly, use the `fastapi-service` skill too.

Keep route handlers thin:

```python
@router.get(
    "/runs/{run_id}",
    response_model=RunDto,
    responses={404: {"description": "Run not found"}},
)
async def get_run(
    run_id: UUID,
    run_service: RunService = fastapi.Depends(get_run_service),
) -> RunDto:
    try:
        run_status = await run_service.get_run(run_id)
    except RunNotFoundError as exc:
        raise fastapi.HTTPException(status_code=404, detail=str(exc)) from exc

    return RunMapper.to_dto(run_status)
```

Route responsibilities:

- parse and validate HTTP inputs
- call a service/use case
- map domain/application results to DTOs
- translate expected domain failures to HTTP responses

Service responsibilities:

- enforce business rules
- coordinate stores, queues, event logs, and external dependencies
- return typed application/domain results

## Testing

- For fake-first pytest conventions, fixture placement, and FastAPI app test wiring, use the `pytest-testing` skill.
- Test route status codes, response bodies, validation failures, and auth behavior.
- Test pagination/filtering/sorting edge cases.
- Test not-found, forbidden, conflict, and validation responses.
- Test OpenAPI-sensitive behavior when endpoint contracts are part of the deliverable.
- Use focused service tests for business rules; use route tests for HTTP mapping.

## Avoid

- Verbs in resource names when standard HTTP methods express the operation.
- Deeply nested paths that force clients to know the whole data graph.
- Inconsistent singular/plural naming.
- Returning `200 OK` with an error payload.
- Leaking internal IDs, traces, provider payloads, secrets, or implementation details.
- Adding authentication shortcuts in example code.
- Copying examples from other frameworks or languages into this codebase without adapting them to its framework.
