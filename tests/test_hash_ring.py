import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "cluster")
)

from hash_ring import HashRing


class TestHashRing(unittest.TestCase):

    def test_empty_ring(self):

        ring = HashRing()

        self.assertIsNone(
            ring.get_node("hello")
        )

    def test_add_node(self):

        ring = HashRing()

        ring.add_node("node1")

        self.assertEqual(
            ring.get_node("hello"),
            "node1"
        )

    def test_multiple_nodes(self):

        ring = HashRing([
            "node1",
            "node2",
            "node3"
        ])

        for key in ["a", "b", "c", "d", "e"]:

            node = ring.get_node(key)

            self.assertIn(
                node,
                ["node1", "node2", "node3"]
            )

    def test_same_key_same_node(self):

        ring = HashRing([
            "node1",
            "node2",
            "node3"
        ])

        first = ring.get_node("user123")

        second = ring.get_node("user123")

        self.assertEqual(first, second)


    def test_keys_are_distributed(self):
    
            ring = HashRing(
                ["node1", "node2", "node3"],
                replicas=100
            )
    
            counts = {
                "node1": 0,
                "node2": 0,
                "node3": 0
            }
    
            for i in range(1000):
    
                node = ring.get_node(
                    f"key-{i}"
                )
    
                counts[node] += 1
    
            for node in counts:
    
                self.assertGreater(
                    counts[node],
                    100
                )

    def test_adding_node_only_moves_some_keys(self):

        ring = HashRing(
            ["node1", "node2", "node3"],
            replicas=100
        )

        keys = [f"key-{i}" for i in range(1000)]

        before = {}

        for key in keys:
            before[key] = ring.get_node(key)

     # Add a new node
        ring.add_node("node4")

        moved = 0

        for key in keys:

            after = ring.get_node(key)

            if before[key] != after:
                moved += 1

        print(f"Keys moved: {moved}/{len(keys)}")

    # We expect substantially fewer than all keys to move
        self.assertLess(moved, 500)

    def test_removing_node_only_moves_some_keys(self):

        ring = HashRing(
            ["node1", "node2", "node3"],
            replicas=100
        )

        keys = [f"key-{i}" for i in range(1000)]

        before = {}

        for key in keys:
            before[key] = ring.get_node(key)

        ring.remove_node("node2")

        moved = 0

        for key in keys:

            after = ring.get_node(key)

            if before[key] != after:
                moved += 1

        print(f"Keys moved after removal: {moved}/{len(keys)}")

        self.assertLess(moved, 700)

    def test_remove_node(self):

        ring = HashRing([
            "node1",
            "node2",
            "node3"
        ])

        ring.remove_node("node2")

        for key in ["a", "b", "c", "d"]:

            node = ring.get_node(key)

            self.assertIn(
                node,
                ["node1", "node3"]
            )


if __name__ == "__main__":
    unittest.main()