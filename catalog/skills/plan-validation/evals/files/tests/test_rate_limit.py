import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rate_limit import MESSAGE, RateLimiter, load_limit  # noqa: E402


class FrozenClock:
    now = 0.0

    def __call__(self):
        return self.now


class RateLimitTest(unittest.TestCase):
    def test_ac01_request_over_the_limit_is_rejected_with_retry_after(self):
        limiter = RateLimiter(60, clock=FrozenClock())
        for _ in range(60):
            self.assertEqual(limiter.check("key-a"), (True, 0))
        allowed, retry_after = limiter.check("key-a")
        self.assertFalse(allowed)
        self.assertGreater(retry_after, 0)

    def test_ac02_keys_have_independent_limits(self):
        limiter = RateLimiter(1, clock=FrozenClock())
        self.assertTrue(limiter.check("key-a")[0])
        self.assertTrue(limiter.check("key-b")[0])
        self.assertFalse(limiter.check("key-a")[0])

    def test_ac03_limit_comes_from_config(self):
        self.assertEqual(load_limit(), 60)

    def test_message(self):
        self.assertEqual(MESSAGE, "Too many requests")


if __name__ == "__main__":
    unittest.main()
