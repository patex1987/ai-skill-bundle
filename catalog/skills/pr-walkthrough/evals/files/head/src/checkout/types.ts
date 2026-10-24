export interface LineItem {
  sku: string;
  priceCents: number;
  quantity: number;
}

export interface CheckoutRequest {
  customerId: string;
  items: LineItem[];
  couponCode?: string;
}
