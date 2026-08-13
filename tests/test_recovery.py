import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from cluster.recovery import RecoveryManager


nodes = {
    "node1": ("127.0.0.1", 6380),
    "node2": ("127.0.0.1", 6381),
    "node3": ("127.0.0.1", 6382),
}


recovery = RecoveryManager(nodes)


source = "node1"
target = "node2"

print(f"Source: {source}")
print(f"Target: {target}")

synced = recovery.sync_node(
    source,
    target
)

print(f"Synced keys: {synced}")
