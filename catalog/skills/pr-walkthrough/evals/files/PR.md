# Add coupon codes to checkout

Customers can pass `couponCode` to `POST /checkout`. Percentage and fixed-amount
coupons are supported. Unknown or expired coupons return 400.

Tested with `npm test`. No change for requests without a coupon.
