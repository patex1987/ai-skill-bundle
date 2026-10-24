import { WELCOME_PERCENT, type Coupon } from './coupon';

const coupons: Coupon[] = [
  { code: 'WELCOME', kind: 'percent', percent: WELCOME_PERCENT, expiresAt: new Date('2030-01-01') },
  { code: 'FIVEOFF', kind: 'fixed', amountCents: 500, expiresAt: new Date('2030-01-01') },
];

export function findCoupon(code: string): Coupon | undefined {
  return coupons.find((c) => c.code === code);
}
