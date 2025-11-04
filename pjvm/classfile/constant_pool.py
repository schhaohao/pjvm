# classfile/constant_pool.py
from typing import List, Optional

# Constant pool tags (subset)
# java虚拟机规范一共定义了14种常量，如下：
CONSTANT_Class = 7
CONSTANT_Fieldref = 9
CONSTANT_Methodref = 10
CONSTANT_InterfaceMethodref = 11
CONSTANT_String = 8
CONSTANT_Integer = 3
CONSTANT_Float = 4
CONSTANT_Long = 5
CONSTANT_Double = 6
CONSTANT_NameAndType = 12
CONSTANT_Utf8 = 1
CONSTANT_MethodHandle = 15
CONSTANT_MethodType = 16
CONSTANT_InvokeDynamic = 18

# 常量池，其实常量池就是一个数据库，索引从1开始，因为0是保留的是空
class ConstantPool:
    def __init__(self, entries: List[Optional[dict]]):
        # entries: index => dict with 'tag' and fields, index 0 unused.
        # entries 是一个 Python 列表，
        # 下标就是常量池索引。下标 0 故意留空，符合 JVM 规范（常量池从 1 开始）。
        # 每个元素是一个 dict，最少有 'tag': 7/10/1...，再根据类型存不同字段
        # 比如 'tag': 7, 'value': 'java/lang/Object' 表示一个 Class 常量
        # 'tag': 10, 'class_index': 1, 'name_and_type_index': 2 表示一个 Fieldref 常量
        # 'tag': 15, 'ref_kind': 1, 'ref_index': 2 表示一个 MethodHandle 常量
        # 'tag': 16, 'descriptor_index': 2 表示一个 MethodType 常量
        # 'tag': 18, 'bootstrap_method_attr_index': 1, 'name_and_type_index': 2 表示一个 InvokeDynamic 常量
        self.entries = entries

    def get(self, index: int) -> dict:
        if index <= 0 or index >= len(self.entries):
            raise IndexError(f"Invalid constant pool index: {index}")
        return self.entries[index]

    def get_utf8(self, index: int) -> str:
        entry = self.get(index)
        if entry['tag'] != CONSTANT_Utf8:
            raise TypeError(f"Expected Utf8 at index {index}, found {entry['tag']}")
        return entry['value']

    def get_class_name(self, index: int) -> str:
        entry = self.get(index)
        if entry['tag'] != CONSTANT_Class:
            raise TypeError(f"Expected Class at index {index}, found {entry['tag']}")
        name_index = entry['name_index']
        return self.get_utf8(name_index).replace('/', '.')

    def get_name_and_type(self, index: int) -> tuple:
        entry = self.get(index)
        if entry['tag'] != CONSTANT_NameAndType:
            raise TypeError(f"Expected NameAndType at index {index}, found {entry['tag']}")
        name = self.get_utf8(entry['name_index'])
        descriptor = self.get_utf8(entry['descriptor_index'])
        return name, descriptor

    def get_methodref(self, index: int) -> tuple:
        entry = self.get(index)
        if entry['tag'] not in (CONSTANT_Methodref, CONSTANT_InterfaceMethodref):
            raise TypeError(f"Expected Methodref at index {index}, found {entry['tag']}")
        class_index = entry['class_index']
        name_and_type_index = entry['name_and_type_index']
        class_name = self.get_class_name(class_index)
        name, desc = self.get_name_and_type(name_and_type_index)
        return class_name, name, desc

    def __len__(self):
        return len(self.entries)
