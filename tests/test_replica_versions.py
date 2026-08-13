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

    # Replica receives version 5
    result = store.set_replica(
        "user:1",
        "Bob",
        5
    )

    print("Apply v5:", result)
    print("Value:", store.get("user:1"))
    print("Version:", store.get_version("user:1"))

    assert result is True
    assert store.get("user:1") == "Bob"
    assert store.get_version("user:1") == 5

    # Older version should be rejected
    result = store.set_replica(
        "user:1",
        "Ananya",
        3
    )

    print("\nApply v3:", result)
    print("Value:", store.get("user:1"))
    print("Version:", store.get_version("user:1"))

    assert result is False
    assert store.get("user:1") == "Bob"
    assert store.get_version("user:1") == 5

    # Newer version should be accepted
    result = store.set_replica(
        "user:1",
        "Charlie",
        6
    )

    print("\nApply v6:", result)
    print("Value:", store.get("user:1"))
    print("Version:", store.get_version("user:1"))

    assert result is True
    assert store.get("user:1") == "Charlie"
    assert store.get_version("user:1") == 6

    print("\nVersion conflict handling: PASS")

finally:

    if os.path.exists(wal_file):
        os.remove(wal_file)
