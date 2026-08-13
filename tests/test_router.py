import sys
from pathlib import Path
from collections import Counter

sys.path.append(str(Path(__file__).resolve().parent.parent))

from cluster.router import Router


nodes = {
    "node1": ("127.0.0.1", 6380),
    "node2": ("127.0.0.1", 6381),
    "node3": ("127.0.0.1", 6382),
}

router = Router(nodes)

counts = Counter()

for i in range(100):

    key = f"user:{i}"
    value = f"Ananya{i}"

    command = f"SET {key} {value}"

    node = router.get_node(key)

    response = router.send_command(command)

    if response != "+OK":
        print(f"ERROR: {key} -> {response}")

    counts[node] += 1


print("\nKey distribution:")

for node in nodes:
    print(f"{node}: {counts[node]}")