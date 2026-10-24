import type { Coupon } from '../coupons/coupon';
import type { LineItem } from './types';

export function calculateTotal(items: LineItem[], coupon?: Coupon): number {
  const subtotal = items.reduce((sum, item) => sum + item.priceCents * item.quantity, 0);
  if (!coupon) {
    return subtotal;
  }
  return applyCoupon(subtotal, coupon);
}

function applyCoupon(subtotal: number, coupon: Coupon): number {
  if (coupon.kind === 'fixed') {
    return subtotal - coupon.amountCents;
  }
  return Math.round(subtotal * (1 - coupon.percent / 100));
}
