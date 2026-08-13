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

distribution = {
    "node1": 0,
    "node2": 0,
    "node3": 0,
}

TOTAL_KEYS = 10000

for i in range(TOTAL_KEYS):

    key = f"distribution:{i}"

    primary = router.replication.get_primary(key)

    distribution[primary] += 1


print("Key distribution:")
print()

for node, count in distribution.items():

    percentage = (
        count / TOTAL_KEYS
    ) * 100

    print(
        f"{node}: "
        f"{count} keys "
        f"({percentage:.2f}%)"
    )


print()
print(f"Total keys: {TOTAL_KEYS}")
