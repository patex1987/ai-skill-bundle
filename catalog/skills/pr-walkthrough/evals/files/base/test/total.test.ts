import { describe, expect, it } from 'vitest';
import { calculateTotal } from '../src/checkout/total';

describe('calculateTotal', () => {
  it('sums price times quantity', () => {
    expect(calculateTotal([{ sku: 'a', priceCents: 250, quantity: 2 }])).toBe(500);
  });
});
