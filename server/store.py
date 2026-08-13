import threading

from wal import WAL
from ttl import TTLManager
from lru import LRUCache


class Store:

    def __init__(self, max_keys=None,wal_file="data.wal"):
        self._data: dict[str, str] = {}
        self._lock = threading.Lock()

        self._wal = WAL(wal_file)
        self._ttl = TTLManager()

        self._max_keys = max_keys
        self._lru = LRUCache(max_keys) if max_keys is not None else None

        self._recover()
        

    def _recover(self):
        for command in self._wal.read_all():

            parts = command.split(" ", 2)

            if not parts:
                continue

            cmd = parts[0]

            if cmd == "SET" and len(parts) == 3:
                key = parts[1]
                value = parts[2]

                self._data[key] = value

                if self._lru:
                    self._lru.put(key, value)

            elif cmd == "DEL" and len(parts) == 2:
                key = parts[1]

                self._data.pop(key, None)

                if self._lru:
                    self._lru.delete(key)

            elif cmd == "EXPIRE" and len(parts) == 3:
                key = parts[1]
                seconds = int(parts[2])

                if key in self._data:
                    self._ttl.set_expiry(key, seconds)

    def set(self, key: str, value: str) -> None:

        with self._lock:

            self._wal.append(f"SET {key} {value}")

            self._data[key] = value

            self._ttl.remove(key)

            if self._lru:
                self._lru.put(key, value)

                # If LRU evicted something
                while self._lru.size() > self._max_keys:
                    pass

    def get(self, key: str) -> str | None:

        with self._lock:

            if self._ttl.is_expired(key):

                self._data.pop(key, None)
                self._ttl.remove(key)

                self._wal.append(f"DEL {key}")

                if self._lru:
                    self._lru.delete(key)

                return None

            value = self._data.get(key)

            if value is not None and self._lru:
                self._lru.get(key)

            return value

    def delete(self, key: str) -> bool:

        with self._lock:

            if key not in self._data:
                return False

            self._wal.append(f"DEL {key}")

            del self._data[key]

            self._ttl.remove(key)

            if self._lru:
                self._lru.delete(key)

            return True

    def exists(self, key: str) -> bool:

        with self._lock:

            if self._ttl.is_expired(key):

                self._data.pop(key, None)
                self._ttl.remove(key)

                self._wal.append(f"DEL {key}")

                if self._lru:
                    self._lru.delete(key)

                return False

            if self._lru:
                self._lru.get(key)

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