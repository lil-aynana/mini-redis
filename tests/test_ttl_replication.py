import sys
import time
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from cluster.router import Router


NODES = {
    "node1": ("127.0.0.1", 6380),
    "node2": ("127.0.0.1", 6381),
    "node3": ("127.0.0.1", 6382),
}

router = Router(NODES)

key = "day8_ttl_replication"

primary = router.replication.get_primary(key)
replica = router.replication.get_replica(key)

print("Primary:", primary)
print("Replica:", replica)

# --------------------------------------------------
# SET
# --------------------------------------------------

print()
print("SET key...")

response = router.send_command(
    f"SET {key} temporary"
)

print("SET:", response)

assert response == "+OK"


# --------------------------------------------------
# Verify replica received it
# --------------------------------------------------

replica_value = router._send_to_node(
    replica,
    f"GET {key}"
)

print(
    "Replica immediately:",
    replica_value
)

assert replica_value == "+temporary"


# --------------------------------------------------
# EXPIRE
# --------------------------------------------------

print()
print("Setting TTL = 2 seconds...")

response = router.send_command(
    f"EXPIRE {key} 2"
)

print("EXPIRE:", response)

assert response == ":1"


# --------------------------------------------------
# Verify it still exists
# --------------------------------------------------

response = router.send_command(
    f"GET {key}"
)

print(
    "Primary immediately:",
    response
)

assert response == "+temporary"


# --------------------------------------------------
# Wait for expiration
# --------------------------------------------------

print()
print("Waiting 3 seconds...")

time.sleep(3)


# --------------------------------------------------
# Trigger expiration on primary
# --------------------------------------------------

primary_value = router._send_to_node(
    primary,
    f"GET {key}"
)

print(
    "Primary after expiration:",
    primary_value
)

assert primary_value == "$-1"


# --------------------------------------------------
# Trigger expiration on replica
# --------------------------------------------------

replica_value = router._send_to_node(
    replica,
    f"GET {key}"
)

print(
    "Replica after expiration:",
    replica_value
)

assert replica_value == "$-1"


print()
print("TTL + REPLICATION TEST: PASS")
