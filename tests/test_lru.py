import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))

from lru import LRUCache


class TestLRU(unittest.TestCase):

    def test_basic_get_put(self):

        cache = LRUCache(2)

        cache.put("a", "1")
        cache.put("b", "2")

        self.assertEqual(cache.get("a"), "1")
        self.assertEqual(cache.get("b"), "2")

    def test_evicts_least_recently_used(self):

        cache = LRUCache(2)

        cache.put("a", "1")
        cache.put("b", "2")

        # A becomes recently used
        cache.get("a")

        # B should be evicted
        cache.put("c", "3")

        self.assertEqual(cache.get("a"), "1")
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("c"), "3")

    def test_update_makes_key_recently_used(self):

        cache = LRUCache(2)

        cache.put("a", "1")
        cache.put("b", "2")

        # A becomes recently used
        cache.put("a", "100")

        cache.put("c", "3")

        self.assertEqual(cache.get("a"), "100")
        self.assertIsNone(cache.get("b"))

    def test_size(self):

        cache = LRUCache(2)

        cache.put("a", "1")
        cache.put("b", "2")

        self.assertEqual(cache.size(), 2)

        cache.put("c", "3")

        self.assertEqual(cache.size(), 2)


if __name__ == "__main__":
    unittest.main()