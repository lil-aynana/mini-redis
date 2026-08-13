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

    # First write
    store.set("user:1", "Ananya")

    print("After first SET:")
    print("value:", store.get("user:1"))
    print("version:", store.get_version("user:1"))

    assert store.get("user:1") == "Ananya"
    assert store.get_version("user:1") == 1

    # Second write
    store.set("user:1", "Bob")

    print("\nAfter second SET:")
    print("value:", store.get("user:1"))
    print("version:", store.get_version("user:1"))

    assert store.get("user:1") == "Bob"
    assert store.get_version("user:1") == 2

    # Third write
    store.set("user:1", "Charlie")

    print("\nAfter third SET:")
    print("value:", store.get("user:1"))
    print("version:", store.get_version("user:1"))

    assert store.get("user:1") == "Charlie"
    assert store.get_version("user:1") == 3

    print("\nNormal versioning: PASS")

finally:

    if os.path.exists(wal_file):
        os.remove(wal_file)