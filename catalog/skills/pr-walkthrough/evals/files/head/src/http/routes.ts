import { calculateTotal } from '../checkout/total';
import type { CheckoutRequest } from '../checkout/types';
import { isValid } from '../coupons/coupon';
import { findCoupon } from '../coupons/repository';

export function registerRoutes(app: { post: Function }) {
  app.post('/checkout', (req: { body: CheckoutRequest }, res: any) => {
    const coupon = req.body.couponCode ? findCoupon(req.body.couponCode) : undefined;
    if (req.body.couponCode && (!coupon || !isValid(coupon, new Date()))) {
      return res.status(400).json({ error: 'invalid coupon' });
    }
    const totalCents = calculateTotal(req.body.items, coupon);
    res.status(201).json({ totalCents });
  });
}
