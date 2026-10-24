import { describe, expect, it } from 'vitest';
import { calculateTotal } from '../src/checkout/total';
import { WELCOME_PERCENT } from '../src/coupons/coupon';

const items = [{ sku: 'a', priceCents: 250, quantity: 2 }];
const later = new Date('2030-01-01');

describe('calculateTotal', () => {
  it('sums price times quantity', () => {
    expect(calculateTotal(items)).toBe(500);
  });

  it('applies a percentage coupon', () => {
    const coupon = { code: 'WELCOME', kind: 'percent' as const, percent: WELCOME_PERCENT, expiresAt: later };
    expect(calculateTotal(items, coupon)).toBe(500 * (1 - WELCOME_PERCENT / 100));
  });

  it('applies a fixed coupon', () => {
    const coupon = { code: 'FIVEOFF', kind: 'fixed' as const, amountCents: 100, expiresAt: later };
    expect(calculateTotal(items, coupon)).toBe(400);
  });
});
