"""In-process token bucket rate limit, one bucket per API key."""
import json
import time
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / "config" / "limits.json"
MESSAGE = "Too many requests"


def load_limit(path=CONFIG):
    return json.loads(path.read_text())["requests_per_minute"]


class RateLimiter:
    def __init__(self, per_minute, clock=time.monotonic):
        self.per_minute = per_minute
        self.clock = clock
        self.buckets = {}

    def check(self, api_key):
        """Return (allowed, retry_after_seconds) for one request."""
        now = self.clock()
        tokens, last = self.buckets.get(api_key, (self.per_minute, now))
        tokens = min(self.per_minute, tokens + (now - last) * self.per_minute / 60)
        if tokens < 1:
            self.buckets[api_key] = (tokens, now)
            return False, int((1 - tokens) * 60 / self.per_minute) + 1
        self.buckets[api_key] = (tokens - 1, now)
        return True, 0
