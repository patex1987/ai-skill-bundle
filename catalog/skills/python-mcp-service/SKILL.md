---
name: python-mcp-service
description: Implement, refactor, review, or explain Python MCP servers (FastMCP or the MCP Python SDK) that wrap a downstream API, including tool names and input/result contracts, httpx client adapters, timeouts and error classification, safe error envelopes, health routes, lifecycle, and trace/correlation propagation.
metadata:
  routing-tier: balanced
  routing-effort: medium
---

# Python MCP Service

An MCP server is an adapter between agents and a downstream API. Its tool
surface is a consumer-facing contract.

## Tool contracts

- Treat tool names, descriptions, and input/result shapes as a public API.
  Prefer additive evolution, and coordinate renames or new required fields with
  the agents that call the tools.
- Keep decorated tool functions thin and fully typed. Validate identifiers,
  non-empty collections, ranges, and string bounds before any downstream I/O.
- Return a consistent success/error envelope that helps the agent recover but
  does not expose internal exceptions or raw provider payloads.
- Write tool descriptions for the model that selects them: say what the tool
  does, when to use it, and its important limits.
- Keep test or demo controls (such as fault injection) separate from ordinary
  business inputs.

## Downstream client boundary

- Keep endpoints, timeouts, auth and configuration, HTTP lifecycle, request
  construction, response parsing, and error classification in one client adapter.
- Use one managed `httpx.AsyncClient` per service lifecycle where practical,
  and close owned clients on shutdown.
- Set finite timeouts. Classify timeout, connection, protocol, non-success, and
  malformed-payload failures.
- Do not retry mutating operations unless idempotency is explicit.
- Validate configured URLs, and never forward arbitrary caller-controlled headers.

## Observability

- Propagate only the agreed context: W3C trace context and the platform's
  correlation and request IDs.
- Keep IDs out of metric labels. Log operation names, outcomes, durations, and
  correlation fields, never tokens or full sensitive payloads.

## Transport and health

- Keep MCP decorators, transport setup, and HTTP routes at the outer edge.
- Keep `/health` and readiness bounded and deterministic, and separate liveness
  from downstream dependency health when deployment needs both.
- Avoid hidden network calls at start-up unless readiness owns that check.

## Workflow

1. Inspect the existing tool and downstream API contracts.
2. Identify compatibility and failure semantics before editing.
3. Change the smallest tool or client boundary.
4. Add contract tests for success, invalid input, downstream failure, timeout,
   malformed response, and metadata propagation (see `pytest-testing`).
5. Run the repository's full Python check.
