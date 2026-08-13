import sys
from pathlib import Path
from collections import Counter

sys.path.append(str(Path(__file__).resolve().parent.parent))

from cluster.replication import ReplicaManager


nodes = {
    "node1": ("127.0.0.1", 6380),
    "node2": ("127.0.0.1", 6381),
    "node3": ("127.0.0.1", 6382),
}

manager = ReplicaManager(nodes)

keys = [f"key:{i}" for i in range(10000)]

primary_counts = Counter()
replica_counts = Counter()

for key in keys:

    primary, replica = manager.get_primary_and_replica(key)

    assert primary in nodes
    assert replica in nodes
    assert primary != replica

    primary_counts[primary] += 1
    replica_counts[replica] += 1


print("Primary distribution:")

for node in nodes:
    print(f"{node}: {primary_counts[node]}")


print("\nReplica distribution:")

for node in nodes:
    print(f"{node}: {replica_counts[node]}")