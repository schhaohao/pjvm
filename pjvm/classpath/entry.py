"""
Entry 接口（Python 抽象基类)
"""

import os
import abc

path_list_separator = os.pathsep  # ";" on Windows, ":" on Unix

class Entry(abc.ABC):
    @abc.abstractmethod
    def read_class(self, class_name: str) -> tuple[bytes, 'Entry', Exception | None]:
        """读取 class 文件内容，返回 (字节数据, 当前Entry, 错误)"""
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        """返回路径字符串表示"""
        pass


def new_entry(path: str) -> Entry:
    from .composite_entry import CompositeEntry
    from .wildcard_entry import new_wildcard_entry
    from .zip_entry import ZipEntry
    from .dir_entry import DirEntry

    if path_list_separator in path:
        return CompositeEntry(path)
    if path.endswith("*"):
        return new_wildcard_entry(path)
    if path.lower().endswith((".jar", ".zip")):
        return ZipEntry(path)
    return DirEntry(path)