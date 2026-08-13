import socket


class RecoveryManager:

    def __init__(self, nodes):
        self.nodes = nodes

    # --------------------------------------------------
    # Send command to a node
    # --------------------------------------------------

    def _send(self, node_name, command):

        host, port = self.nodes[node_name]

        with socket.create_connection(
            (host, port),
            timeout=2
        ) as sock:

            sock.sendall((command + "\n").encode())

            response = b""

            while not response.endswith(b"\n"):

                chunk = sock.recv(4096)

                if not chunk:
                    break

                response += chunk

        return response.decode().strip()

    # --------------------------------------------------
    # Get keys from source node
    # --------------------------------------------------

    def get_keys(self, node_name):

        response = self._send(
            node_name,
            "KEYS"
        )

        if response.startswith("+"):

            data = response[1:]

            if not data:
                return []

            return data.split(",")

        raise RuntimeError(
            f"Failed to get keys from {node_name}: {response}"
        )

    # --------------------------------------------------
    # Get version of a key
    # --------------------------------------------------

    def get_version(self, node_name, key):

        response = self._send(
            node_name,
            f"VERSION {key}"
        )

        if response.startswith(":"):

            return int(response[1:])

        raise RuntimeError(
            f"Failed to get version for {key}: {response}"
        )

    # --------------------------------------------------
    # Synchronize target node
    # --------------------------------------------------

    def sync_node(self, source_node, target_node):

        print(
            f"Starting recovery: "
            f"{source_node} -> {target_node}"
        )

        keys = self.get_keys(source_node)

        synced = 0
        ignored = 0

        for key in keys:

            # Get value
            value_response = self._send(
                source_node,
                f"GET {key}"
            )

            if not value_response.startswith("+"):
                continue

            value = value_response[1:]

            # Get authoritative version
            version = self.get_version(
                source_node,
                key
            )

            # Send versioned replication
            sync_response = self._send(
                target_node,
                f"REPLSET {key} {value} {version}"
            )

            if sync_response == "+OK":

                synced += 1

            elif sync_response == "+IGNORED":

                ignored += 1

        print(
            f"Recovery complete: "
            f"{synced} updated, "
            f"{ignored} already up-to-date, "
            f"{len(keys)} total"
        )

        return synced