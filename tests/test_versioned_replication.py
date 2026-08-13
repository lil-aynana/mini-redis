import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from cluster.router import Router


nodes = {
    "node1": ("127.0.0.1", 6380),
    "node2": ("127.0.0.1", 6381),
    "node3": ("127.0.0.1", 6382),
}


router = Router(nodes)

key = "versioned_replication_test"

primary = router.replication.get_primary(key)
replica = router.replication.get_replica(key)

print("Primary:", primary)
print("Replica:", replica)


# --------------------------------------------------
# First SET
# --------------------------------------------------

response = router.send_command(
    f"SET {key} first"
)

print("\nFirst SET:", response)

primary_version = router._get_version(
    primary,
    key
)

replica_version = router._get_version(
    replica,
    key
)

print("Primary version:", primary_version)
print("Replica version:", replica_version)

assert response == "+OK"
assert primary_version == replica_version


# --------------------------------------------------
# Second SET
# --------------------------------------------------

response = router.send_command(
    f"SET {key} second"
)

print("\nSecond SET:", response)

primary_version = router._get_version(
    primary,
    key
)

replica_version = router._get_version(
    replica,
    key
)

print("Primary version:", primary_version)
print("Replica version:", replica_version)

assert response == "+OK"
assert primary_version == replica_version


# --------------------------------------------------
# Verify values
# --------------------------------------------------

primary_value = router._send_to_node(
    primary,
    f"GET {key}"
)

replica_value = router._send_to_node(
    replica,
    f"GET {key}"
)

print("\nPrimary value:", primary_value)
print("Replica value:", replica_value)

assert primary_value == "+second"
assert replica_value == "+second"


print("\nVersioned replication: PASS")