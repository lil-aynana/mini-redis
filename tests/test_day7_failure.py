import sys
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

key = "day7_failure_test"
value = "survives_failure"


primary = router.replication.get_primary(key)
replica = router.replication.get_replica(key)

print("Primary:", primary)
print("Replica:", replica)

print()
print("SET through Router...")

response = router.send_command(
    f"SET {key} {value}"
)

print("SET response:", response)

assert response == "+OK"


print()
print("Checking replica...")

replica_value = router._send_to_node(
    replica,
    f"GET {key}"
)

print("Replica value:", replica_value)

assert replica_value == f"+{value}"

print()
print("Replication confirmed.")
print()
print("Now stop the PRIMARY node:")
print(primary)
print()
print("Then press ENTER here.")

input()


print()
print("Trying GET through Router...")

try:

    response = router.send_command(
        f"GET {key}"
    )

    print("GET response:", response)

    assert response == f"+{value}"

    print()
    print("FAILOVER SUCCESS")
    print(
        f"{replica} successfully served "
        f"the request after {primary} failed."
    )

except Exception as e:

    print()
    print("FAILOVER FAILED")
    print("Error:", e)
