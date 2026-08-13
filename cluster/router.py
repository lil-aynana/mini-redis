import socket

from cluster.hash_ring import HashRing


class Router:

    def __init__(self, nodes):
        self.nodes = nodes

        node_names = list(nodes.keys())

        self.ring = HashRing(node_names)

    def get_node(self, key):
        return self.ring.get_node(key)

    def send_command(self, command):
        parts = command.split(" ", 2)

        if len(parts) < 2:
            return "-ERR command requires a key"

        key = parts[1]

        node_name = self.get_node(key)

        host, port = self.nodes[node_name]

        with socket.create_connection((host, port), timeout=2) as sock:

            sock.sendall((command + "\n").encode())

            response = b""

            while not response.endswith(b"\n"):
                chunk = sock.recv(4096)

                if not chunk:
                    break

                response += chunk

        return response.decode().strip()