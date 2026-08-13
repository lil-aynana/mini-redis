import socket
import threading
import random


HOST = "127.0.0.1"
PORT = 6380

CLIENTS = 20
OPERATIONS_PER_CLIENT = 100

KEYS = [
    f"mixed:{i}"
    for i in range(20)
]

results = []
lock = threading.Lock()


def send_command(sock, command):

    sock.sendall(
        (command + "\n").encode()
    )

    response = b""

    while not response.endswith(b"\n"):

        chunk = sock.recv(4096)

        if not chunk:
            break

        response += chunk

    return response.decode().strip()


def worker(client_id):

    operations = 0
    errors = 0

    try:

        with socket.create_connection(
            (HOST, PORT),
            timeout=10
        ) as sock:

            for i in range(
                OPERATIONS_PER_CLIENT
            ):

                key = random.choice(KEYS)

                operation = random.choice([
                    "SET",
                    "GET",
                    "EXISTS",
                    "DEL"
                ])

                try:

                    if operation == "SET":

                        value = (
                            f"value-"
                            f"{client_id}-"
                            f"{i}"
                        )

                        command = (
                            f"SET {key} {value}"
                        )

                        response = send_command(
                            sock,
                            command
                        )

                        if response != "+OK":

                            errors += 1

                            print(
                                f"[ERROR] "
                                f"client={client_id} "
                                f"command={command!r} "
                                f"response={response!r}"
                            )

                    elif operation == "GET":

                        command = f"GET {key}"

                        response = send_command(
                            sock,
                            command
                        )

                        if not (
                            response.startswith("+")
                            or response == "$-1"
                        ):

                            errors += 1

                            print(
                                f"[ERROR] "
                                f"client={client_id} "
                                f"command={command!r} "
                                f"response={response!r}"
                            )

                    elif operation == "EXISTS":

                        command = f"EXISTS {key}"

                        response = send_command(
                            sock,
                            command
                        )

                        if response not in (
                            ":0",
                            ":1"
                        ):

                            errors += 1

                            print(
                                f"[ERROR] "
                                f"client={client_id} "
                                f"command={command!r} "
                                f"response={response!r}"
                            )

                    elif operation == "DEL":

                        command = f"DEL {key}"

                        response = send_command(
                            sock,
                            command
                        )

                        if response not in (
                            ":0",
                            ":1"
                        ):

                            errors += 1

                            print(
                                f"[ERROR] "
                                f"client={client_id} "
                                f"command={command!r} "
                                f"response={response!r}"
                            )

                    operations += 1

                except Exception as e:

                    errors += 1

                    print(
                        f"[EXCEPTION] "
                        f"client={client_id} "
                        f"operation={operation} "
                        f"key={key} "
                        f"error={repr(e)}"
                    )

    except Exception as e:

        errors += 1

        print(
            f"[CONNECTION ERROR] "
            f"client={client_id}: "
            f"{repr(e)}"
        )

    with lock:

        results.append(
            (
                client_id,
                operations,
                errors
            )
        )


print(
    "========== CONCURRENT MIXED TEST =========="
)

print(
    f"Clients: {CLIENTS}"
)

print(
    f"Operations/client: "
    f"{OPERATIONS_PER_CLIENT}"
)

print(
    f"Shared keys: {len(KEYS)}"
)


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


total_operations = sum(
    result[1]
    for result in results
)

total_errors = sum(
    result[2]
    for result in results
)


print()
print(
    f"Total operations: "
    f"{total_operations}"
)

print(
    f"Errors: "
    f"{total_errors}"
)

print(
    f"Successful operations: "
    f"{total_operations - total_errors}"
)


assert len(results) == CLIENTS

assert total_operations == (
    CLIENTS *
    OPERATIONS_PER_CLIENT
)

assert total_errors == 0

print()
print(
    "CONCURRENT MIXED OPERATIONS: PASS"
)
