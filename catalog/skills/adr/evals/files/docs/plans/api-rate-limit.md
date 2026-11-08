# Implementation Plan: API Rate Limit

Status: done

## 1. Summary

Limit each API key to a fixed number of requests per minute with an in-process
token bucket, and answer over-limit requests with 429 and Retry-After.

Research: [api-rate-limit-codebase.md](../research/api-rate-limit-codebase.md)
Review record: [api-rate-limit-review.md](api-rate-limit-review.md)

## 5. Requirements and Assumptions

### Decisions

- Limit per API key, not per client IP. Decision (user, Q-02)
- In-process token bucket per instance. A shared Redis counter was rejected: the
  service runs as a single instance, and Redis would add an operational
  dependency. Decision (user, Q-03)
- Return 429 with a Retry-After header. Decision (user, Q-04)
- Name the module `rate_limit.py` rather than `throttle.py`. Decision (user, Q-05)

## 12. Implementation Steps

1. [x] Tests for AC-01 to AC-03 (failed: module missing).
2. [x] Token bucket in `src/rate_limit.py`; limit read from `config/limits.json`.
3. [x] README Limits section.

## 13. Testing Strategy

| ID | Setup / action | Observable expected result | Level / file | Command and directory | Pre-change expectation |
|---|---|---|---|---|---|
| AC-01 | 61 requests in one minute with one key | The 61st is rejected with a positive Retry-After | unit, `tests/test_rate_limit.py` | `python3 -m unittest discover -s tests` (root) | Fails: module missing |
| AC-02 | Two keys, limit 1 | Each key has its own limit | unit, same | same | Fails: module missing |
| AC-03 | `config/limits.json` sets 60 | The limiter uses 60 | unit, same | same | Fails: module missing |

Test agreement: agreed (user, Q-06).

## 18. Docs Impact

- Architecture: `docs/architecture/overview.md`, Components (new rate limiter) and
  Known gaps (limits are per instance, so they multiply with instances).
- ADR candidates:
  - In-process token bucket per instance; rejected alternative: a shared Redis
    counter (an extra operational dependency for a single-instance service).
  - Module name `rate_limit.py`; rejected alternative: `throttle.py`.
- Behaviour or contract changes: 429 with Retry-After; tests in `tests/test_rate_limit.py`.
- Other docs: `README.md`, Limits section.

## 19. As-built

- Deviation: the limit is read from `config/limits.json` instead of the
  `RATE_LIMIT_PER_MINUTE` environment variable, so operators can change it without
  a redeploy. Approved by the author during execution.
- Limits are keyed by API key, as decided in Q-02.
- Docs impact: README Limits section done. The overview edit was deferred by the
  author to the next sweep. ADR candidate (token bucket) left for `adr`.
- Validation: [api-rate-limit.md](../validation/api-rate-limit.md), verdict verified.

