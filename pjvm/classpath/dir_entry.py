import os
from .entry import Entry

class DirEntry(Entry):
    def __init__(self, path: str):
        self.abs_dir = os.path.abspath(path)

    def read_class(self, class_name: str) -> tuple[bytes, Entry, Exception | None]:
        file_path = os.path.join(self.abs_dir, class_name)
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                return data, self, None
        except Exception as e:
            return b'', self, e

    def __str__(self):
        return self.abs_dir