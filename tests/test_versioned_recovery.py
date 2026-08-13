import os
import sys
import tempfile

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "server"
    )
)

from store import Store


source_wal = tempfile.mktemp()
target_wal = tempfile.mktemp()

try:

    source = Store(wal_file=source_wal)
    target = Store(wal_file=target_wal)

    # ------------------------------------------
    # Source has newer version
    # ------------------------------------------

    source.set_replica(
        "user:1",
        "NEW",
        5
    )

    # Target has older version
    target.set_replica(
        "user:1",
        "OLD",
        3
    )

    print("Before synchronization:")
    print(
        "Source:",
        source.get("user:1"),
        "v",
        source.get_version("user:1")
    )

    print(
        "Target:",
        target.get("user:1"),
        "v",
        target.get_version("user:1")
    )

    # ------------------------------------------
    # Simulate recovery
    # ------------------------------------------

    result = target.set_replica(
        "user:1",
        source.get("user:1"),
        source.get_version("user:1")
    )

    print("\nApplying source version:")
    print("Result:", result)

    print(
        "Target:",
        target.get("user:1"),
        "v",
        target.get_version("user:1")
    )

    assert result is True
    assert target.get("user:1") == "NEW"
    assert target.get_version("user:1") == 5

    # ------------------------------------------
    # Now try stale data
    # ------------------------------------------

    result = target.set_replica(
        "user:1",
        "STALE",
        4
    )

    print("\nTrying stale version 4:")
    print("Result:", result)

    print(
        "Target:",
        target.get("user:1"),
        "v",
        target.get_version("user:1")
    )

    assert result is False
    assert target.get("user:1") == "NEW"
    assert target.get_version("user:1") == 5

    print("\nVersioned recovery protection: PASS")

finally:

    if os.path.exists(source_wal):
        os.remove(source_wal)

    if os.path.exists(target_wal):
        os.remove(target_wal)
