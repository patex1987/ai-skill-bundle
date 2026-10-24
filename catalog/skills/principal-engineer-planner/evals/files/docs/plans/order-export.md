# Implementation Plan: Order Export

## 1. Summary

Add an asynchronous CSV export of a customer's orders. The API accepts an export
request, a background worker writes the file to object storage, and the customer
downloads it through a short-lived link.

## 2. Goals

- Customers can export their orders as CSV.
- Large exports do not block API requests.

## 3. Non-goals

- Exports for other entity types.

## 4. Current State

See [research](../research/order-export-codebase.md). Orders are read through
`OrderRepository.findByCustomer`. A job queue exists for e-mail delivery.

## 5. Requirements and Assumptions

### Confirmed Requirements

- CSV format.

### Assumptions

- The worker can retry a failed export from the start.
- Exports include all historical orders.
- Download links expire after 24 hours.

### Open Questions

- Maximum number of rows per export?

## 6. Proposed Design

`POST /exports` enqueues a job on the existing queue and returns `202` with an
export ID. The worker pages through `findByCustomer`, streams rows to object
storage, and sets the export status to `ready`. `GET /exports/{id}` returns the
status and, when ready, a signed URL.

## 7. Alternatives Considered

### Alternative A: synchronous streaming response

- Pros: no queue or storage.
- Cons: long requests; timeouts on large customers.
- Decision: rejected (recommendation).

## 10. Security, Privacy, and Abuse Considerations

- Only the owning customer may read an export.

## 11. Performance, Scalability, and Reliability Considerations

- Paging keeps memory bounded.

## 12. Implementation Steps

1. Export model and `POST /exports` — Suggested tier: balanced
2. Worker and storage upload — Suggested tier: deep
3. `GET /exports/{id}` with signed URL — Suggested tier: balanced

## 13. Testing Strategy

| ID | Setup / action | Observable expected result | Level / file | Command and directory | Pre-change expectation |
|---|---|---|---|---|---|
| AC-01 | Customer requests an export | `202` with export ID | integration | `npm test` in repo root | fails: route missing |
| AC-02 | Export completes | status `ready`, URL downloads CSV with all orders | integration | `npm test` | fails |
| AC-03 | Another customer requests the export ID | `404` | integration | `npm test` | fails |

Test agreement: proposed

## 14. Rollout / Migration Plan

Release behind a feature flag.
