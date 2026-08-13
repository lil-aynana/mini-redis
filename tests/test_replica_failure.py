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

key = "day8_replica_failure"
value = "primary_survives"


primary = router.replication.get_primary(key)
replica = router.replication.get_replica(key)

print("Primary:", primary)
print("Replica:", replica)

print()
print("Stop the REPLICA node:")
print(replica)
print()
print("Then press ENTER.")

input()


print()
print("Sending SET through Router...")

try:

    response = router.send_command(
        f"SET {key} {value}"
    )

    print("SET response:", response)

    assert response == "+OK"

    print()
    print("Checking primary...")

    primary_value = router._send_to_node(
        primary,
        f"GET {key}"
    )

    print("Primary value:", primary_value)

    assert primary_value == f"+{value}"

    print()
    print("REPLICA FAILURE TEST: PASS")

except Exception as e:

    print()
    print("REPLICA FAILURE TEST: FAILED")
    print("Error:", e)

    raise
