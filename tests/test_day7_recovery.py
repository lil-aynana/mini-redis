import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from cluster.recovery import RecoveryManager


NODES = {
    "node1": ("127.0.0.1", 6380),
    "node2": ("127.0.0.1", 6381),
    "node3": ("127.0.0.1", 6382),
}


source = "node3"
target = "node2"

recovery = RecoveryManager(NODES)

print("Recovery source:", source)
print("Recovery target:", target)

print()
print("Starting recovery...")

synced = recovery.sync_node(
    source,
    target
)

print()
print("Keys updated:", synced)

# Verify the important key from the failure test
value = recovery._send(
    target,
    "GET day7_failure_test"
)

print(
    "Recovered key value:",
    value
)

assert value == "+survives_failure"

print()
print("NODE RECOVERY: PASS")
