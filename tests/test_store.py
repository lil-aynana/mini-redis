"""
test_store.py — Day 1 automated tests for the in-memory store.

Run with:  python3 -m pytest tests/test_store.py -v
(or, with zero dependencies:  python3 tests/test_store.py)
"""

import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))

from store import Store  # noqa: E402


class TestStore(unittest.TestCase):
    def setUp(self):
        self.wal_file = tempfile.mktemp()
        self.store = Store(wal_file=self.wal_file)

    def test_set_then_get(self):
        self.store.set("foo", "bar")
        self.assertEqual(self.store.get("foo"), "bar")

    def test_get_missing_key_returns_none(self):
        self.assertIsNone(self.store.get("does-not-exist"))

    def test_overwrite_existing_key(self):
        self.store.set("foo", "bar")
        self.store.set("foo", "baz")
        self.assertEqual(self.store.get("foo"), "baz")

    def test_delete_existing_key_returns_true(self):
        self.store.set("foo", "bar")
        self.assertTrue(self.store.delete("foo"))
        self.assertIsNone(self.store.get("foo"))

    def test_delete_missing_key_returns_false(self):
        self.assertFalse(self.store.delete("does-not-exist"))

    def test_exists(self):
        self.assertFalse(self.store.exists("foo"))
        self.store.set("foo", "bar")
        self.assertTrue(self.store.exists("foo"))

    def test_size(self):
        self.assertEqual(self.store.size(), 0)
        self.store.set("a", "1")
        self.store.set("b", "2")
        self.assertEqual(self.store.size(), 2)
        self.store.delete("a")
        self.assertEqual(self.store.size(), 1)

    def test_concurrent_writes_do_not_corrupt_state(self):
        """
        Spin up many threads all writing different keys at once.
        This is the test that actually justifies the Lock in store.py —
        without it, this test is where you'd see corruption or lost writes
        under load.
        """
        import threading

        def writer(n):
            for i in range(100):
                self.store.set(f"key-{n}-{i}", str(i))

        threads = [threading.Thread(target=writer, args=(n,)) for n in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(self.store.size(), 10 * 100)


if __name__ == "__main__":
    unittest.main()
