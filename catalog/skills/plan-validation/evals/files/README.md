# Account API

## Limits

Each API key may send `requests_per_minute` requests (see `config/limits.json`).
Requests over the limit get `429 Too many requests` with a `Retry-After` header.
