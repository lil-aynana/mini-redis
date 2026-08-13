import socket
import threading
import time


NODES = {
    "node1": ("127.0.0.1", 6380),
    "node2": ("127.0.0.1", 6381),
    "node3": ("127.0.0.1", 6382),
}

HOST = "127.0.0.1"
PORT = 6380

CLIENTS = 20
OPERATIONS_PER_CLIENT = 50


results = []
lock = threading.Lock()


def send_command(sock, command):

    sock.sendall((command + "\n").encode())

    response = b""

    while not response.endswith(b"\n"):

        chunk = sock.recv(4096)

        if not chunk:
            break

        response += chunk

    return response.decode().strip()


def worker(client_id):

    success = 0
    errors = 0

    try:

        with socket.create_connection(
            (HOST, PORT),
            timeout=5
        ) as sock:

            for i in range(OPERATIONS_PER_CLIENT):

                key = f"load:{client_id}:{i}"
                value = f"value-{i}"

                # SET
                response = send_command(
                    sock,
                    f"SET {key} {value}"
                )

                if response != "+OK":
                    errors += 1
                    continue

                # GET
                response = send_command(
                    sock,
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

print("Starting load test...")
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


elapsed = time.perf_counter() - start


# --------------------------------------------------
# Results
# --------------------------------------------------

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

print()
print("========== RESULTS ==========")

print(
    f"Total operations: {total_operations}"
)

print(
    f"Successful operations: "
    f"{total_success * 1}"
)

print(
    f"Errors: {total_errors}"
)

print(
    f"Time: {elapsed:.4f} seconds"
)

print(
    f"Throughput: "
    f"{total_operations / elapsed:.2f} ops/sec"
)

print(
    f"Success rate: "
    f"{(total_success / (CLIENTS * OPERATIONS_PER_CLIENT)) * 100:.2f}%"
)
