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

TOTAL_KEYS = 100

success = 0
errors = 0


for i in range(TOTAL_KEYS):

    key = f"replication-load:{i}"
    value = f"value-{i}"

    try:

        primary = router.replication.get_primary(key)
        replica = router.replication.get_replica(key)

        # Write through Router
        response = router.send_command(
            f"SET {key} {value}"
        )

        if response != "+OK":
            errors += 1
            continue

        # Read directly from primary
        primary_value = router._send_to_node(
            primary,
            f"GET {key}"
        )

        # Read directly from replica
        replica_value = router._send_to_node(
            replica,
            f"GET {key}"
        )

        if (
            primary_value == f"+{value}"
            and replica_value == f"+{value}"
        ):
            success += 1

        else:
            errors += 1

            print(
                f"Mismatch for {key}: "
                f"primary={primary_value}, "
                f"replica={replica_value}"
            )

    except Exception as e:

        errors += 1

        print(
            f"Error for {key}: {e}"
        )


print()
print("========== REPLICATION LOAD ==========")

print(
    f"Total keys: {TOTAL_KEYS}"
)

print(
    f"Successfully replicated: {success}"
)

print(
    f"Errors: {errors}"
)

print(
    f"Replication success rate: "
    f"{(success / TOTAL_KEYS) * 100:.2f}%"
)
