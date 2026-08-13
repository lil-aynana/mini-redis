import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from cluster.hash_ring import HashRing


nodes = ["node1", "node2", "node3"]

keys = [f"key:{i}" for i in range(10000)]

ring = HashRing(nodes)

# Record original ownership
before = {}

for key in keys:
    before[key] = ring.get_node(key)


# Remove node2
ring.remove_node("node2")

moved = 0

for key in keys:
    after = ring.get_node(key)

    if before[key] != after:
        moved += 1


print("Total keys:", len(keys))
print("Keys moved:", moved)
print("Percentage moved:", moved / len(keys) * 100)