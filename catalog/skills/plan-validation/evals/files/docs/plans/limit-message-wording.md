# Implementation Plan: Limit Message Wording

Status: in-progress
Planning depth: light plan.

## 1. Summary

Change the over-limit message to "Too many requests".

## 12. Implementation Steps

1. [x] Update `MESSAGE` in `src/rate_limit.py` and its test.

## 13. Testing Strategy

| ID | Setup / action | Observable expected result | Level / file | Command and directory | Pre-change expectation |
|---|---|---|---|---|---|
| AC-01 | Read `MESSAGE` | Equals "Too many requests" | unit, `tests/test_rate_limit.py` | `python3 -m unittest discover -s tests` (root) | Fails: old wording |

Test agreement: agreed (user, in chat).

## 18. Docs Impact

None.

## 19. As-built

Not started.
