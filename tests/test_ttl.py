import time
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))

from ttl import TTLManager


class TestTTL(unittest.TestCase):

    def test_key_is_not_expired_initially(self):
        ttl = TTLManager()

        ttl.set_expiry("foo", 10)

        self.assertFalse(ttl.is_expired("foo"))

    def test_key_expires(self):
        ttl = TTLManager()

        ttl.set_expiry("foo", 0.1)

        self.assertFalse(ttl.is_expired("foo"))

        time.sleep(0.2)

        self.assertTrue(ttl.is_expired("foo"))

    def test_key_without_ttl_is_not_expired(self):
        ttl = TTLManager()

        self.assertFalse(ttl.is_expired("foo"))

    def test_remove_ttl(self):
        ttl = TTLManager()

        ttl.set_expiry("foo", 10)
        ttl.remove("foo")

        self.assertFalse(ttl.is_expired("foo"))


if __name__ == "__main__":
    unittest.main()