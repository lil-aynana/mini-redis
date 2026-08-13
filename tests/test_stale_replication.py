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


wal_file = tempfile.mktemp()

try:

    store = Store(wal_file=wal_file)

    print("========== STALE REPLICATION TEST ==========")

    # ------------------------------------------
    # v5 should be accepted
    # ------------------------------------------

    result = store.set_replica(
        "replication:key",
        "value-v5",
        5
    )

    print("v5:", result)

    assert result is True
    assert store.get("replication:key") == "value-v5"
    assert store.get_version("replication:key") == 5

    # ------------------------------------------
    # Duplicate v5 should be ignored
    # ------------------------------------------

    result = store.set_replica(
        "replication:key",
        "duplicate-v5",
        5
    )

    print("duplicate v5:", result)

    assert result is False
    assert store.get("replication:key") == "value-v5"
    assert store.get_version("replication:key") == 5

    # ------------------------------------------
    # Older v4 should be ignored
    # ------------------------------------------

    result = store.set_replica(
        "replication:key",
        "stale-v4",
        4
    )

    print("stale v4:", result)

    assert result is False
    assert store.get("replication:key") == "value-v5"
    assert store.get_version("replication:key") == 5

    # ------------------------------------------
    # Newer v6 should be accepted
    # ------------------------------------------

    result = store.set_replica(
        "replication:key",
        "value-v6",
        6
    )

    print("v6:", result)

    assert result is True
    assert store.get("replication:key") == "value-v6"
    assert store.get_version("replication:key") == 6

    # ------------------------------------------
    # Newer v7 should be accepted
    # ------------------------------------------

    result = store.set_replica(
        "replication:key",
        "value-v7",
        7
    )

    print("v7:", result)

    assert result is True
    assert store.get("replication:key") == "value-v7"
    assert store.get_version("replication:key") == 7

    # ------------------------------------------
    # Old v6 should NOT overwrite v7
    # ------------------------------------------

    result = store.set_replica(
        "replication:key",
        "stale-v6",
        6
    )

    print("stale v6:", result)

    assert result is False
    assert store.get("replication:key") == "value-v7"
    assert store.get_version("replication:key") == 7

    print()
    print("Final value:", store.get("replication:key"))
    print("Final version:", store.get_version("replication:key"))

    print()
    print("STALE REPLICATION PROTECTION: PASS")

finally:

    if os.path.exists(wal_file):
        os.remove(wal_file)
