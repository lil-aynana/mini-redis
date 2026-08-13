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

CLIENTS = 20
OPERATIONS_PER_CLIENT = 50

router = Router(NODES)

results = []
lock = threading.Lock()


def worker(client_id):

    success = 0
    errors = 0

    for i in range(OPERATIONS_PER_CLIENT):

        key = f"router-load:{client_id}:{i}"
        value = f"value-{client_id}-{i}"

        try:

            # SET through Router
            response = router.send_command(
                f"SET {key} {value}"
            )

            if response != "+OK":
                errors += 1
                continue

            # GET through Router
            response = router.send_command(
                f"GET {key}"
            )

            if response == f"+{value}":
                success += 1
            else:
                errors += 1

        except Exception as e:

            errors += 1

            print(
                f"Client {client_id} error: {e}"
            )

    with lock:
        results.append(
            (client_id, success, errors)
        )


# --------------------------------------------------
# Start benchmark
# --------------------------------------------------

print("Starting Router load test...")
print(f"Clients: {CLIENTS}")
print(
    f"Operations/client: "
    f"{OPERATIONS_PER_CLIENT}"
)

start = time.perf_counter()

threads = []

for client_id in range(CLIENTS):

    thread = threading.Thread(
        target=worker,
        args=(client_id,)
    )

    threads.append(thread)
    thread.start()


for thread in threads:
    thread.join()


# --------------------------------------------------
# Results
# --------------------------------------------------

elapsed = time.perf_counter() - start

total_success = sum(
    result[1]
    for result in results
)

total_errors = sum(
    result[2]
    for result in results
)

total_operations = (
    CLIENTS *
    OPERATIONS_PER_CLIENT *
    2
)

success_rate = (
    total_success /
    (CLIENTS * OPERATIONS_PER_CLIENT)
) * 100


print()
print("========== ROUTER RESULTS ==========")

print(
    f"Total operations: "
    f"{total_operations}"
)

print(
    f"Successful SET+GET pairs: "
    f"{total_success}"
)

print(
    f"Errors: "
    f"{total_errors}"
)

print(
    f"Time: "
    f"{elapsed:.4f} seconds"
)

print(
    f"Throughput: "
    f"{total_operations / elapsed:.2f} ops/sec"
)

print(
    f"Success rate: "
    f"{success_rate:.2f}%"
)