import { calculateTotal } from '../checkout/total';
import type { CheckoutRequest } from '../checkout/types';

export function registerRoutes(app: { post: Function }) {
  app.post('/checkout', (req: { body: CheckoutRequest }, res: any) => {
    const totalCents = calculateTotal(req.body.items);
    res.status(201).json({ totalCents });
  });
}
