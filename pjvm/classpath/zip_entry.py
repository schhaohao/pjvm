"""
读取 jar/zip 中的 .class
"""
import zipfile
import os
from .entry import Entry

class ZipEntry(Entry):
    def __init__(self, path: str):
        self.abs_path = os.path.abspath(path)

    def read_class(self, class_name: str) -> tuple[bytes, Entry, Exception | None]:
        try:
            with zipfile.ZipFile(self.abs_path, 'r') as z:
                if class_name in z.namelist():
                    with z.open(class_name) as f:
                        data = f.read()
                        return data, self, None
                else:
                    return b'', self, FileNotFoundError(f"class not found: {class_name}")
        except Exception as e:
            return b'', self, e

    def __str__(self):
        return self.abs_path