import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))

from wal import WAL


class TestWAL(unittest.TestCase):

    def setUp(self):
        self.filename = "test.wal"
        self.wal = WAL(self.filename)
        self.wal.clear()

    def tearDown(self):
        self.wal.clear()

    def test_append_and_read(self):
        self.wal.append("SET foo bar")
        self.wal.append("SET name Ananya")

        commands = self.wal.read_all()

        self.assertEqual(commands, [
            "SET foo bar",
            "SET name Ananya"
        ])

    def test_clear(self):
        self.wal.append("SET foo bar")

        self.wal.clear()

        self.assertEqual(self.wal.read_all(), [])


if __name__ == "__main__":
    unittest.main()