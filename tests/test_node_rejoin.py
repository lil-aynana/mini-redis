import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from cluster.router import Router
from cluster.recovery import RecoveryManager


NODES = {
    "node1": ("127.0.0.1", 6380),
    "node2": ("127.0.0.1", 6381),
    "node3": ("127.0.0.1", 6382),
}


router = Router(NODES)
recovery = RecoveryManager(NODES)

key = "day8_rejoin_test"
value = "rejoined_successfully"

# --------------------------------------------------
# Find primary and replica
# --------------------------------------------------

primary = router.replication.get_primary(key)
replica = router.replication.get_replica(key)

print("Primary:", primary)
print("Replica:", replica)

# --------------------------------------------------
# Write initial value
# --------------------------------------------------

print()
print("Initial SET...")

response = router.send_command(
    f"SET {key} initial"
)

print("SET:", response)

assert response == "+OK"


# --------------------------------------------------
# Verify replication
# --------------------------------------------------

replica_value = router._send_to_node(
    replica,
    f"GET {key}"
)

print(
    "Replica initial value:",
    replica_value
)

assert replica_value == "+initial"


# --------------------------------------------------
# Simulate node failure
# --------------------------------------------------

print()
print("Stop the PRIMARY node:")
print(primary)

print()
print("After stopping it, press ENTER.")

input()


# --------------------------------------------------
# Write/read through surviving replica
# --------------------------------------------------

print()
print("Trying GET after failure...")

response = router.send_command(
    f"GET {key}"
)

print("GET:", response)

assert response == "+initial"

print()
print(
    f"{replica} is serving the key."
)


# --------------------------------------------------
# New write after failover
# --------------------------------------------------

print()
print("Writing new value after failover...")

response = router.send_command(
    f"SET {key} {value}"
)

print("SET:", response)

assert response == "+OK"


# --------------------------------------------------
# Restart failed node
# --------------------------------------------------

print()
print(
    f"Restart {primary} now."
)

print(
    "Then press ENTER after the node is listening."
)

input()


# --------------------------------------------------
# Recover failed node
# --------------------------------------------------

print()
print(
    f"Starting recovery: "
    f"{replica} -> {primary}"
)

synced = recovery.sync_node(
    replica,
    primary
)

print()
print(
    "Keys updated:",
    synced
)


# --------------------------------------------------
# Verify recovered data
# --------------------------------------------------

recovered_value = recovery._send(
    primary,
    f"GET {key}"
)

print(
    "Recovered value:",
    recovered_value
)

assert recovered_value == f"+{value}"


# --------------------------------------------------
# Verify version
# --------------------------------------------------

source_version = recovery.get_version(
    replica,
    key
)

target_version = recovery.get_version(
    primary,
    key
)

print(
    "Source version:",
    source_version
)

print(
    "Recovered node version:",
    target_version
)

assert target_version == source_version


print()
print("NODE RESTART + REJOIN: PASS")
