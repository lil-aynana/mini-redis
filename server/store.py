import threading

from wal import WAL
from ttl import TTLManager
from lru import LRUCache


class Store:

    def __init__(self, max_keys=None, wal_file="data.wal"):

        self._data: dict[str, str] = {}

        # Version number for each key
        self._versions: dict[str, int] = {}

        self._lock = threading.Lock()

        self._wal = WAL(wal_file)
        self._ttl = TTLManager()

        self._max_keys = max_keys
        self._lru = (
            LRUCache(max_keys)
            if max_keys is not None
            else None
        )

        self._recover()

    # --------------------------------------------------
    # WAL RECOVERY
    # --------------------------------------------------

    def _recover(self):

        for command in self._wal.read_all():

            # New format:
            # SET key value version
            #
            # Old format:
            # SET key value
            #
            # maxsplit=3 allows values to contain spaces.

            parts = command.split(" ", 3)

            if not parts:
                continue

            cmd = parts[0]

            # ------------------------------------------
            # SET
            # ------------------------------------------

            if cmd == "SET":

                # New versioned WAL entry
                if len(parts) == 4:

                    key = parts[1]
                    value = parts[2]
                    version = int(parts[3])

                    self._data[key] = value
                    self._versions[key] = version

                # Old WAL entry
                elif len(parts) == 3:

                    key = parts[1]
                    value = parts[2]

                    self._data[key] = value

                    # Old entries have no stored version.
                    # Give them a version based on recovery order.
                    current_version = self._versions.get(
                        key,
                        0
                    )

                    self._versions[key] = (
                        current_version + 1
                    )

                if self._lru:
                    self._lru.put(
                        key,
                        value
                    )

            # ------------------------------------------
            # DEL
            # ------------------------------------------

            elif cmd == "DEL" and len(parts) == 2:

                key = parts[1]

                self._data.pop(
                    key,
                    None
                )

                if self._lru:
                    self._lru.delete(key)

                # We intentionally keep the version.
                #
                # Example:
                # key existed at v5
                # key gets deleted
                #
                # If recreated later:
                # v6
                #
                # instead of going back to v1.

            # ------------------------------------------
            # EXPIRE
            # ------------------------------------------

            elif cmd == "EXPIRE" and len(parts) == 3:

                key = parts[1]
                seconds = int(parts[2])

                if key in self._data:

                    self._ttl.set_expiry(
                        key,
                        seconds
                    )

    # --------------------------------------------------
    # NORMAL SET
    # --------------------------------------------------

    def set(self, key: str, value: str) -> None:

        with self._lock:

            # Increment version
            new_version = (
                self._versions.get(key, 0) + 1
            )

            # Persist version in WAL
            self._wal.append(
                f"SET {key} {value} {new_version}"
            )

            self._data[key] = value

            self._versions[key] = new_version

            # SET removes previous TTL
            self._ttl.remove(key)

            if self._lru:

                evicted_key = self._lru.put(
                    key,
                    value
                )

                # Keep Store and LRU consistent
                if evicted_key is not None:

                    self._data.pop(
                        evicted_key,
                        None
                    )

                    self._ttl.remove(
                        evicted_key
                    )

    # --------------------------------------------------
    # REPLICA SET
    # --------------------------------------------------

    def set_replica(
        self,
        key: str,
        value: str,
        version: int
    ) -> bool:

        with self._lock:

            current_version = self._versions.get(
                key,
                0
            )

            # Ignore stale replication
            if version <= current_version:
                return False

            # Store versioned WAL entry
            self._wal.append(
                f"SET {key} {value} {version}"
            )

            self._data[key] = value

            self._versions[key] = version

            # Replica receives the current value,
            # so remove any previous TTL.
            self._ttl.remove(key)

            if self._lru:

                evicted_key = self._lru.put(
                    key,
                    value
                )

                if evicted_key is not None:

                    self._data.pop(
                        evicted_key,
                        None
                    )

                    self._ttl.remove(
                        evicted_key
                    )

            return True

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, key: str) -> str | None:

        with self._lock:

            if self._ttl.is_expired(key):

                self._data.pop(
                    key,
                    None
                )

                self._ttl.remove(key)

                self._wal.append(
                    f"DEL {key}"
                )

                if self._lru:
                    self._lru.delete(key)

                return None

            value = self._data.get(key)

            if value is not None and self._lru:

                self._lru.get(key)

            return value

    # --------------------------------------------------
    # GET VERSION
    # --------------------------------------------------

    def get_version(self, key: str) -> int:

        with self._lock:

            return self._versions.get(
                key,
                0
            )

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------

    def delete(self, key: str) -> bool:

        with self._lock:

            if key not in self._data:
                return False

            self._wal.append(
                f"DEL {key}"
            )

            del self._data[key]

            self._ttl.remove(key)

            if self._lru:
                self._lru.delete(key)

            return True

    # --------------------------------------------------
    # EXISTS
    # --------------------------------------------------

    def exists(self, key: str) -> bool:

        with self._lock:

            if self._ttl.is_expired(key):

                self._data.pop(
                    key,
                    None
                )

                self._ttl.remove(key)

                self._wal.append(
                    f"DEL {key}"
                )

                if self._lru:
                    self._lru.delete(key)

                return False

            if self._lru:
                self._lru.get(key)

            return key in self._data

    # --------------------------------------------------
    # EXPIRE
    # --------------------------------------------------

    def expire(
        self,
        key: str,
        seconds: int
    ) -> bool:

        with self._lock:

            if key not in self._data:
                return False

            self._ttl.set_expiry(
                key,
                seconds
            )

            self._wal.append(
                f"EXPIRE {key} {seconds}"
            )

            return True

    # --------------------------------------------------
    # KEYS
    # --------------------------------------------------

    def keys(self) -> list[str]:

        with self._lock:

            return list(
                self._data.keys()
            )

    # --------------------------------------------------
    # SIZE
    # --------------------------------------------------

    def size(self) -> int:

        with self._lock:

            return len(
                self._data
            )