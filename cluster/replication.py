import bisect

from cluster.hash_ring import HashRing


class ReplicaManager:

    def __init__(self, nodes, replicas=100):
        self.nodes = nodes

        self.ring = HashRing(
            list(nodes.keys()),
            replicas=replicas
        )

    def get_primary(self, key):
        return self.ring.get_node(key)

    def get_replica(self, key):

        if not self.ring.ring:
            return None

        # Find the hash position of this specific key
        key_position = self.ring._hash(key)

        # Find where the key lands on the ring
        index = bisect.bisect_left(
            self.ring.sorted_keys,
            key_position
        )

        if index == len(self.ring.sorted_keys):
            index = 0

        # Primary is the node at this position
        primary = self.ring.ring[
            self.ring.sorted_keys[index]
        ]

        # Walk clockwise until we find a different physical node
        for offset in range(1, len(self.ring.sorted_keys)):

            next_index = (
                index + offset
            ) % len(self.ring.sorted_keys)

            next_node = self.ring.ring[
                self.ring.sorted_keys[next_index]
            ]

            if next_node != primary:
                return next_node

        return None

    def get_primary_and_replica(self, key):

        primary = self.get_primary(key)
        replica = self.get_replica(key)

        return primary, replica