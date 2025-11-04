"""
多个路径组合
"""
from .entry import Entry, path_list_separator

class CompositeEntry(Entry):
    def __init__(self, path_list: str):
        from .entry import new_entry
        self.entries = [new_entry(path) for path in path_list.split(path_list_separator)]

    def read_class(self, class_name: str) -> tuple[bytes, Entry, Exception | None]:
        for entry in self.entries:
            data, from_entry, err = entry.read_class(class_name)
            if err is None:
                return data, from_entry, None
        return b'', self, FileNotFoundError(f"class not found: {class_name}")

    def __str__(self):
        return path_list_separator.join(str(e) for e in self.entries)