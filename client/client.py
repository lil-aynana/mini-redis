"""
client.py — a thin client for talking to a mini-redis node.

This is your test harness for every day of the project going forward:
Day 2 (TTL/LRU/WAL), Day 3 (hash ring), Day 4 (multi-node routing) will
all use this same client, or a router built on top of it, to verify
behavior. Keep it working.
"""

import socket


class MiniRedisClient:
    def __init__(self, host: str = "localhost", port: int = 6380, timeout: float = 5.0):
        self.host = host
        self.port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(timeout)
        self._sock.connect((host, port))
        self._f = self._sock.makefile("rw", encoding="utf-8", newline="\n")

    def _send(self, line: str) -> str:
        self._f.write(line + "\n")
        self._f.flush()
        reply = self._f.readline().strip()
        return reply

    def ping(self) -> bool:
        return self._send("PING") == "+PONG"

    def set(self, key: str, value: str) -> bool:
        reply = self._send(f"SET {key} {value}")
        return reply == "+OK"

    def get(self, key: str) -> str | None:
        reply = self._send(f"GET {key}")
        if reply == "$-1":
            return None
        if reply.startswith("+"):
            return reply[1:]
        raise RuntimeError(f"unexpected reply: {reply}")

    def delete(self, key: str) -> bool:
        reply = self._send(f"DEL {key}")
        return reply == ":1"

    def exists(self, key: str) -> bool:
        reply = self._send(f"EXISTS {key}")
        return reply == ":1"

    def close(self) -> None:
        self._sock.close()

    # context-manager support: `with MiniRedisClient() as c:`
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Quick manual smoke test — run node.py in one terminal, then this in another.
    with MiniRedisClient() as c:
        print("PING ->", c.ping())
        print("SET foo bar ->", c.set("foo", "bar"))
        print("GET foo ->", c.get("foo"))
        print("GET missing ->", c.get("missing"))
        print("EXISTS foo ->", c.exists("foo"))
        print("DEL foo ->", c.delete("foo"))
        print("GET foo (after delete) ->", c.get("foo"))
