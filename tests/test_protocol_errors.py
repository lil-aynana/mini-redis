import socket


HOST = "127.0.0.1"
PORT = 6380


def send_command(sock, command):

    sock.sendall((command + "\n").encode())

    response = b""

    while not response.endswith(b"\n"):

        chunk = sock.recv(4096)

        if not chunk:
            break

        response += chunk

    return response.decode().strip()


with socket.create_connection(
    (HOST, PORT),
    timeout=3
) as sock:

    tests = [
        ("PING", "+PONG"),

        ("GET", "-ERR usage: GET <key>"),

        ("SET", "-ERR usage: SET <key> <value>"),

        ("DEL", "-ERR usage: DEL <key>"),

        ("EXISTS", "-ERR usage: EXISTS <key>"),

        ("EXPIRE", "-ERR usage: EXPIRE <key> <seconds>"),

        ("EXPIRE foo abc", "-ERR invalid seconds"),

        ("VERSION", "-ERR usage: VERSION <key>"),

        (
            "REPLSET foo bar",
            "-ERR usage: REPLSET <key> <value> <version>"
        ),

        (
            "REPLSET foo bar abc",
            "-ERR invalid version"
        ),

        (
            "THIS_COMMAND_DOES_NOT_EXIST",
            "-ERR unknown command 'THIS_COMMAND_DOES_NOT_EXIST'"
        ),
    ]

    passed = 0

    print("========== PROTOCOL TEST ==========")

    for command, expected in tests:

        response = send_command(
            sock,
            command
        )

        print(
            f"{command!r}"
            f" -> "
            f"{response!r}"
        )

        if response == expected:
            passed += 1
        else:
            print(
                f"EXPECTED: {expected!r}"
            )


print()
print(f"Passed: {passed}/{len(tests)}")

assert passed == len(tests)

print("PROTOCOL TEST: PASS")
