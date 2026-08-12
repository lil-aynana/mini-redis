import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))

from store import Store
from wal import WAL


class TestStoreLRU(unittest.TestCase):

    def setUp(self):
        WAL().clear()

    def tearDown(self):
        WAL().clear()

    def test_lru_eviction(self):

        store = Store(max_keys=2)

        store.set("a", "1")
        store.set("b", "2")

        # Make A recently used
        self.assertEqual(store.get("a"), "1")

        # B should be evicted
        store.set("c", "3")

        self.assertEqual(store.get("a"), "1")
        self.assertIsNone(store.get("b"))
        self.assertEqual(store.get("c"), "3")

        self.assertEqual(store.size(), 2)


if __name__ == "__main__":
    unittest.main()