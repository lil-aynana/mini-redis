import hashlib
import bisect


class HashRing:

    def __init__(self, nodes=None, replicas=100):

        self.replicas = replicas

        self.ring = {}
        self.sorted_keys = []

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):

        digest = hashlib.sha1(
            key.encode()
        ).hexdigest()

        return int(digest, 16)

    def add_node(self, node):

        for i in range(self.replicas):

            virtual_node = f"{node}#{i}"

            position = self._hash(virtual_node)

            self.ring[position] = node

            bisect.insort(
                self.sorted_keys,
                position
            )

    def remove_node(self, node):

        for i in range(self.replicas):

            virtual_node = f"{node}#{i}"

            position = self._hash(virtual_node)

            if position in self.ring:

                del self.ring[position]

                self.sorted_keys.remove(position)

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

    def get_node(self, key):

        if not self.ring:
            return None

        position = self._hash(key)

        index = bisect.bisect_left(
            self.sorted_keys,
            position
        )

        if index == len(self.sorted_keys):
            index = 0

        node_position = self.sorted_keys[index]

        return self.ring[node_position]