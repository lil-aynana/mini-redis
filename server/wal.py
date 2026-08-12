import os


class WAL:

    def __init__(self, filename="data.wal"):
        self.filename = filename

    def append(self, command):
        with open(self.filename, "a") as file:
            file.write(command + "\n")

    def read_all(self):
        if not os.path.exists(self.filename):
            return []

        with open(self.filename, "r") as file:
            return [line.strip() for line in file]

    def clear(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)