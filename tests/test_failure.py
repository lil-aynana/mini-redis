import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from cluster.router import Router


nodes = {
    "node1": ("127.0.0.1", 6380),
    "node2": ("127.0.0.1", 6381),
    "node3": ("127.0.0.1", 6382),
}

router = Router(nodes)

key = "replication_test"

print("Primary:", router.replication.get_primary(key))
print("Replica:", router.replication.get_replica(key))

print("\nTrying GET through Router...")

try:
    response = router.send_command(f"GET {key}")
    print("Response:", response)

except Exception as e:
    print("FAILED:", e)