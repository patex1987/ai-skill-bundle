# Checkout sample

`POST /checkout` returns the order total in cents. Pass an optional
`couponCode` to apply a discount; an unknown or expired code returns `400`.
