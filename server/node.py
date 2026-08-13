"""
node.py — the TCP server for a single mini-redis node.

WIRE PROTOCOL (Day 1 version — simple, human-readable, testable with `nc`):

  Client sends one command per line:
      SET <key> <value...>      (value is everything after the key — spaces allowed)
      GET <key>
      DEL <key>
      EXISTS <key>
      PING

  Server replies with one line:
      +OK                 -> SET succeeded
      +PONG               -> PING reply
      +<value>            -> GET found the key
      $-1                 -> GET / value not found (nil, borrowed from Redis' RESP)
      :1 / :0             -> DEL / EXISTS: 1 = true, 0 = false
      -ERR <message>      -> something went wrong (bad command, wrong arg count)

  Why this format: prefixing replies with +, $, :, - is lifted directly from
  Redis' real RESP protocol (simplified — no length-prefixing on bulk strings
  yet). It's a deliberate design choice so this is easy to explain in an
  interview: "I used a simplified version of RESP."

Concurrency model: one thread per connection. Fine for this project's scale;
in a real production node you'd want an event loop (asyncio / epoll) to avoid
thread-per-connection overhead at high connection counts — worth mentioning
as a known tradeoff if asked.
"""

import argparse
import socket
import threading

from store import Store
from pathlib import Path


class Node:
    def __init__(self, host: str = "0.0.0.0", port: int = 6380, node_id: str = "node1"):
        self.host = host
        self.port = port
        self.node_id=node_id
        project_root = Path(__file__).resolve().parent.parent
        wal_file = project_root / "data" / node_id / "data.wal"
        self.store = Store(wal_file=wal_file)
        self._server_socket: socket.socket | None = None

    def start(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen()
        print(f"[{self.node_id}] listening on {self.host}:{self.port}")

        try:
            while True:
                conn, addr = self._server_socket.accept()
                thread = threading.Thread(
                    target=self._handle_client, args=(conn, addr), daemon=True
                )
                thread.start()
        except KeyboardInterrupt:
            print(f"\n[{self.node_id}] shutting down")
        finally:
            self._server_socket.close()

    def _handle_client(self, conn: socket.socket, addr) -> None:
        # makefile() gives us line-buffered read/write over the socket,
        # so we can treat this like reading lines from a file instead of
        # hand-rolling buffer accumulation.
        f = conn.makefile("rw", encoding="utf-8", newline="\n")
        try:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                response = self._dispatch(line)
                f.write(response + "\n")
                f.flush()
        except ConnectionError:
            pass
        finally:
            conn.close()

    def _dispatch(self, line: str) -> str:
        parts = line.split(" ", 2)  # command, key, rest-of-line-as-value
        cmd = parts[0].upper()

        

        try:
            if cmd == "PING":
                return "+PONG"

            if cmd == "INFO":
                return (
                    f"node_id={self.node_id} "
                    f"host={self.host} "
                    f"port={self.port} "
                    f"keys={self.store.size()}"
                )

            elif cmd == "SET":
                if len(parts) < 3:
                    return "-ERR usage: SET <key> <value>"
                _, key, value = parts
                self.store.set(key, value)
                return "+OK"

            elif cmd == "GET":
                if len(parts) < 2:
                    return "-ERR usage: GET <key>"
                key = parts[1]
                value = self.store.get(key)
                return f"+{value}" if value is not None else "$-1"

            elif cmd == "DEL":
                if len(parts) < 2:
                    return "-ERR usage: DEL <key>"
                key = parts[1]
                deleted = self.store.delete(key)
                return ":1" if deleted else ":0"

            elif cmd == "EXISTS":
                if len(parts) < 2:
                    return "-ERR usage: EXISTS <key>"
                key = parts[1]
                return ":1" if self.store.exists(key) else ":0"

            elif cmd == "EXPIRE":
                if len(parts) != 3:
                    return "-ERR usage: EXPIRE <key> <seconds>"

                key = parts[1]

                try:
                    seconds = int(parts[2])
                except ValueError:
                    return "-ERR invalid seconds"

                return ":1" if self.store.expire(key, seconds) else ":0"

            else:
                return f"-ERR unknown command '{cmd}'"

        except Exception as e:  # noqa: BLE001 — last-resort guard so one bad
            # request can't kill the client's connection thread.
            return f"-ERR internal error: {e}"


def main():
    parser = argparse.ArgumentParser(description="mini-redis single node server")
    parser.add_argument("--port", type=int, default=6380)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--node-id", default="node1")
    args = parser.parse_args()

    node = Node(host=args.host, port=args.port, node_id=args.node_id)
    node.start()


if __name__ == "__main__":
    main()
