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

    # --------------------------------------------------
    # Simulate the original server
    # --------------------------------------------------

    print("Creating original store...")

    store1 = Store(
        wal_file=wal_file
    )

    store1.set("wal:test:1", "Ananya")
    store1.set("wal:test:2", "MiniRedis")
    store1.set("wal:test:3", "Distributed")

    print("Original data:")
    print(
        store1.get("wal:test:1")
    )
    print(
        store1.get("wal:test:2")
    )
    print(
        store1.get("wal:test:3")
    )

    assert store1.get("wal:test:1") == "Ananya"
    assert store1.get("wal:test:2") == "MiniRedis"
    assert store1.get("wal:test:3") == "Distributed"

    # --------------------------------------------------
    # Simulate server crash/restart
    # --------------------------------------------------

    print()
    print("Simulating server restart...")

    store2 = Store(
        wal_file=wal_file
    )

    print("Recovered data:")

    print(
        store2.get("wal:test:1")
    )

    print(
        store2.get("wal:test:2")
    )

    print(
        store2.get("wal:test:3")
    )

    # --------------------------------------------------
    # Verify recovery
    # --------------------------------------------------

    assert store2.get("wal:test:1") == "Ananya"
    assert store2.get("wal:test:2") == "MiniRedis"
    assert store2.get("wal:test:3") == "Distributed"

    # Versions should also survive recovery
    assert store2.get_version("wal:test:1") == 1
    assert store2.get_version("wal:test:2") == 1
    assert store2.get_version("wal:test:3") == 1

    print()
    print("WAL CRASH RECOVERY: PASS")

finally:

    if os.path.exists(wal_file):
        os.remove(wal_file)
