import socket

from cluster.replication import ReplicaManager


class Router:

    def __init__(self, nodes):
        self.nodes = nodes

        # Nodes that are currently considered unavailable
        self.failed_nodes = set()

        # Handles primary + replica placement
        self.replication = ReplicaManager(nodes)

        # Use the same hash ring
        self.ring = self.replication.ring

    # --------------------------------------------------
    # Hash-ring lookup
    # --------------------------------------------------

    def get_node(self, key):
        return self.ring.get_node(key)

    # --------------------------------------------------
    # Send a command to a specific node
    # --------------------------------------------------

    def _send_to_node(self, node_name, command):

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
    # Mark a node as failed
    # --------------------------------------------------

    def mark_node_failed(self, node):

        if node in self.failed_nodes:
            return

        self.failed_nodes.add(node)

        # Remove failed node from hash ring
        self.ring.remove_node(node)

        print(
            f"NODE DOWN: {node} removed from hash ring"
        )


    def _get_version(self, node_name, key):

        response = self._send_to_node(
            node_name,
            f"VERSION {key}"
        )

        if response.startswith(":"):

            return int(response[1:])

        raise RuntimeError(
            f"Invalid VERSION response: {response}"
        )

    # --------------------------------------------------
    # Main command routing
    # --------------------------------------------------

    def send_command(self, command):

        parts = command.split(" ", 2)

        if len(parts) < 2:
            return "-ERR command requires a key"

        cmd = parts[0].upper()
        key = parts[1]

        # Find current primary and replica
        primary = self.replication.get_primary(key)
        replica = self.replication.get_replica(key)

        # --------------------------------------------------
        # READ PATH
        # --------------------------------------------------

        if cmd in ("GET", "EXISTS"):

            # Try primary first
            try:

                return self._send_to_node(
                    primary,
                    command
                )

            except (
                ConnectionRefusedError,
                TimeoutError,
                OSError
            ):

                print(
                    f"WARNING: primary {primary} unavailable, "
                    f"reading {key} from replica {replica}"
                )

                # Mark primary as failed
                self.mark_node_failed(primary)

                # Try replica
                try:

                    response = self._send_to_node(
                        replica,
                        command
                    )

                    print(
                        f"PROMOTED: {replica} is now primary "
                        f"for {key}"
                    )

                    return response

                except (
                    ConnectionRefusedError,
                    TimeoutError,
                    OSError
                ):

                    return (
                        "-ERR primary and replica unavailable"
                    )

        # --------------------------------------------------
        # WRITE PATH
        # --------------------------------------------------

        try:

            response = self._send_to_node(
                primary,
                command
            )

        except (
            ConnectionRefusedError,
            TimeoutError,
            OSError
        ):

            return (
                f"-ERR primary {primary} unavailable"
            )

        # If primary rejected the command
        if response.startswith("-ERR"):
            return response

        # --------------------------------------------------
        # SET replication
        # --------------------------------------------------

        if cmd == "SET":

            if len(parts) < 3:
                return "-ERR usage: SET <key> <value>"

            value = parts[2]

            version=self._get_version(primary,key)

            replica_command = (
                f"REPLSET {key} {value} {version}"
            )

            try:

                replica_response = self._send_to_node(
                    replica,
                    replica_command
                )

                if replica_response not in ("+OK", "+IGNORED"):

                    print(
                        f"WARNING: replication failed "
                        f"for key={key}, "
                        f"replica={replica}"
                    )

            except (
                ConnectionRefusedError,
                TimeoutError,
                OSError
            ):

                print(
                    f"WARNING: replica {replica} unavailable "
                    f"for key={key}"
                )

        return response