import type { LineItem } from './types';

export function calculateTotal(items: LineItem[]): number {
  return items.reduce((sum, item) => sum + item.priceCents * item.quantity, 0);
}
