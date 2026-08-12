import time


class TTLManager:

    def __init__(self):
        self._expiry = {}

    def set_expiry(self, key: str, seconds: int) -> None:
        self._expiry[key] = time.time() + seconds

    def is_expired(self, key: str) -> bool:
        if key not in self._expiry:
            return False

        return time.time() >= self._expiry[key]

    def remove(self, key: str) -> None:
        self._expiry.pop(key, None)