export const WELCOME_PERCENT = 10;

export type Coupon =
  | { code: string; kind: 'percent'; percent: number; expiresAt: Date }
  | { code: string; kind: 'fixed'; amountCents: number; expiresAt: Date };

export function isValid(coupon: Coupon, now: Date): boolean {
  return coupon.expiresAt.getTime() > now.getTime();
}
