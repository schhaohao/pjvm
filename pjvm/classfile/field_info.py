# classfile/field_info.py
from typing import List

class FieldInfo:
    def __init__(self, access_flags: int, name_index: int, descriptor_index: int, attributes: List[dict]):
        self.access_flags = access_flags
        self.name_index = name_index
        self.descriptor_index = descriptor_index
        self.attributes = attributes

    def __repr__(self):
        return f"<Field name_index={self.name_index} desc_index={self.descriptor_index} flags=0x{self.access_flags:04x}>"
