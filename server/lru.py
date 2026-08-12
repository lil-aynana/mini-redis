class Node:

    def __init__(self, key, value):
        self.key = key
        self.value = value

        self.prev = None
        self.next = None


class LRUCache:

    def __init__(self, capacity):
        self.capacity = capacity

        self.cache = {}

        # Dummy nodes
        self.head = Node(None, None)
        self.tail = Node(None, None)

        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):

        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_end(self, node):

        last = self.tail.prev

        last.next = node
        node.prev = last

        node.next = self.tail
        self.tail.prev = node

    def get(self, key):

        if key not in self.cache:
            return None

        node = self.cache[key]

        # Recently used → move to end
        self._remove(node)
        self._add_to_end(node)

        return node.value

    def delete(self, key):

        if key not in self.cache:
            return False

        node = self.cache[key]

        self._remove(node)
        del self.cache[key]

        return True

    def put(self, key, value):

        # Key already exists
        if key in self.cache:

            node = self.cache[key]

            node.value = value

            self._remove(node)
            self._add_to_end(node)

            return None

        # New key
        node = Node(key, value)

        self.cache[key] = node

        self._add_to_end(node)

        # Capacity exceeded
        if len(self.cache) > self.capacity:

            lru = self.head.next
            evicted_key=lru.key

            self._remove(lru)

            del self.cache[evicted_key]
            return evicted_key

    def size(self):
        return len(self.cache)