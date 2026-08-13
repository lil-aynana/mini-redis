import sys
import time
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

key = "day7_ttl_test"

print("Setting key...")

response = router.send_command(
    f"SET {key} temporary"
)

print("SET:", response)

assert response == "+OK"


print("Setting TTL = 2 seconds...")

response = router.send_command(
    f"EXPIRE {key} 2"
)

print("EXPIRE:", response)

assert response == ":1"


print("Immediately checking key...")

response = router.send_command(
    f"GET {key}"
)

print("GET:", response)

assert response == "+temporary"


print("Waiting for expiration...")

time.sleep(3)


response = router.send_command(
    f"GET {key}"
)

print("GET after expiration:", response)

assert response == "$-1"


print()
print("TTL REGRESSION TEST: PASS")
