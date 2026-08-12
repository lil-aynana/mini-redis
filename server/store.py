import threading

from wal import WAL
from ttl import TTLManager


class Store:
    
    def __init__(self):
        self._data: dict[str, str] = {}
        self._lock = threading.Lock()
        self._wal = WAL()
        self._ttl = TTLManager()

        self._recover()

    def _recover(self):
        """
        Rebuild in-memory state by replaying the WAL.
        """

        for command in self._wal.read_all():

            parts = command.split(" ", 2)

            if not parts:
                continue

            cmd = parts[0]

            if cmd == "SET" and len(parts) == 3:
                key = parts[1]
                value = parts[2]

                self._data[key] = value

            elif cmd == "DEL" and len(parts) == 2:
                key = parts[1]

                self._data.pop(key, None)

            elif cmd == "EXPIRE" and len(parts) == 3:
                key = parts[1]
                seconds = int(parts[2])

                if key in self._data:
                    self._ttl.set_expiry(key, seconds)

    def set(self, key: str, value: str) -> None:
        with self._lock:
            self._wal.append(f"SET {key} {value}")
            self._data[key] = value

            # A new SET removes any previous TTL
            self._ttl.remove(key)

    def get(self, key: str) -> str | None:
        with self._lock:

            if self._ttl.is_expired(key):
                self._data.pop(key, None)
                self._ttl.remove(key)

                self._wal.append(f"DEL {key}")

                return None
            return self._data.get(key)

    def delete(self, key: str) -> bool:
        with self._lock:

            if key not in self._data:
                return False

            self._wal.append(f"DEL {key}")
            del self._data[key]
            self._ttl.remove(key)

            return True

    def exists(self, key: str) -> bool:
        with self._lock:
            if self._ttl.is_expired(key):
                self._data.pop(key, None)
                self._ttl.remove(key)

                self._wal.append(f"DEL {key}")

                return False
            return key in self._data

    def expire(self, key: str, seconds: int) -> bool:
        with self._lock:

            if key not in self._data:
                return False

            self._ttl.set_expiry(key, seconds)

            self._wal.append(f"EXPIRE {key} {seconds}")

            return True

    def keys(self) -> list[str]:
        with self._lock:
            return list(self._data.keys())

    def size(self) -> int:
        with self._lock:
            return len(self._data)