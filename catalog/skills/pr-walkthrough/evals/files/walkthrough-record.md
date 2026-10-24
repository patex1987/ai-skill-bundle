# Walkthrough: Add coupon codes to checkout

- Target: branch `feature/coupons` vs `main`
- Mode: review
- Pinned base: <base-sha>   Head at start: <head-sha>
- Started: 2026-10-24
- Position: Topic 3/4 — Checkout wiring
- Status: in progress

## Topics

| # | Topic | Files | Status |
|---|---|---|---|
| 1 | Coupon contract | src/coupons/coupon.ts, src/checkout/types.ts | done |
| 2 | Total calculation | src/checkout/total.ts, test/total.test.ts | done |
| 3 | Checkout wiring | src/http/routes.ts, src/coupons/repository.ts | current |
| 4 | Docs | README.md | pending |

## Findings

### Open
- [ ] **Fixed coupon can make the total negative** (Topic 2, blocking).
      Evidence: `src/checkout/total.ts:14`. Suggestion: clamp at zero; add a test.

### Follow-up

### Questions

### Dropped

### Done

## Topic changes

## Not verified
