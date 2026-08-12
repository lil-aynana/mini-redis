import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))

from store import Store
from wal import WAL


class TestStoreWAL(unittest.TestCase):

    def setUp(self):
        WAL().clear()

    def tearDown(self):
        WAL().clear()

    def test_recovery_after_restart(self):

        # First Store instance
        store1 = Store()

        store1.set("name", "Ananya")
        store1.set("city", "Bangalore")

        self.assertEqual(store1.get("name"), "Ananya")
        self.assertEqual(store1.get("city"), "Bangalore")

        # Simulate restart by creating a NEW Store
        store2 = Store()

        self.assertEqual(store2.get("name"), "Ananya")
        self.assertEqual(store2.get("city"), "Bangalore")

    def test_delete_is_recovered(self):

        store1 = Store()

        store1.set("name", "Ananya")
        store1.delete("name")

        store2 = Store()

        self.assertIsNone(store2.get("name"))


if __name__ == "__main__":
    unittest.main()