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

    store = Store(
        max_keys=3,
        wal_file=wal_file
    )

    print("Capacity: 3 keys")

    # Add three keys
    store.set("a", "1")
    store.set("b", "2")
    store.set("c", "3")

    print("After a, b, c:")
    print(store.keys())

    assert store.size() == 3

    # Access a so it becomes recently used
    store.get("a")

    # Add d
    store.set("d", "4")

    print("\nAfter accessing a and adding d:")
    print(store.keys())

    # b should be the LRU key and therefore evicted
    assert store.get("b") is None

    # These should still exist
    assert store.get("a") == "1"
    assert store.get("c") == "3"
    assert store.get("d") == "4"

    print("\nLRU eviction: PASS")

finally:

    if os.path.exists(wal_file):
        os.remove(wal_file)
