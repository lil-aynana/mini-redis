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
value = "hello_replica"

# Find primary and replica
primary = router.replication.get_primary(key)
replica = router.replication.get_replica(key)

print(f"Key: {key}")
print(f"Primary: {primary}")
print(f"Replica: {replica}")

# Write through router
response = router.send_command(
    f"SET {key} {value}"
)

print(f"SET response: {response}")

# Read directly from primary
primary_response = router._send_to_node(
    primary,
    f"GET {key}"
)

print(f"Primary GET: {primary_response}")

# Read directly from replica
replica_response = router._send_to_node(
    replica,
    f"GET {key}"
)

print(f"Replica GET: {replica_response}")