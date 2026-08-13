import sys
import threading
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

KEY = "day8_live_failure"

router = Router(NODES)

primary = router.replication.get_primary(KEY)
replica = router.replication.get_replica(KEY)

print("Primary:", primary)
print("Replica:", replica)

print()
print("Make sure ALL THREE nodes are running.")
print("Then press ENTER to start the workload.")

input()

stop_event = threading.Event()

success = 0
errors = 0
lock = threading.Lock()


def worker():

    global success
    global errors

    i = 0

    while not stop_event.is_set():

        value = f"value-{i}"

        try:

            response = router.send_command(
                f"SET {KEY} {value}"
            )

            if response == "+OK":
                with lock:
                    success += 1
            else:
                with lock:
                    errors += 1

        except Exception:
            with lock:
                errors += 1

        i += 1

        time.sleep(0.05)


thread = threading.Thread(
    target=worker
)

thread.start()

print()
print("WORKLOAD STARTED")
print()
print("Now STOP the PRIMARY node:")
print(primary)
print()
print("Wait about 2 seconds.")
print("Then press ENTER here.")

input()

# Give the Router time to encounter the failed node
time.sleep(2)

stop_event.set()
thread.join()

print()
print("========== RESULTS ==========")
print("Successful operations:", success)
print("Errors:", errors)

print()
print("Checking current value through Router...")

try:

    response = router.send_command(
        f"GET {KEY}"
    )

    print("GET response:", response)

    if response.startswith("+"):

        print()
        print("PRIMARY FAILURE DURING LOAD: PASS")

    else:

        print()
        print("PRIMARY FAILURE DURING LOAD: FAILED")

        raise AssertionError(
            f"Unexpected GET response: {response}"
        )

except Exception as e:

    print()
    print("PRIMARY FAILURE DURING LOAD: FAILED")
    print("Error:", e)

    raise
