# classfile/method_info.py
from typing import List, Optional

class CodeAttribute:
    def __init__(self, max_stack: int, max_locals: int, code: bytes, exception_table: list, attributes: list):
        self.max_stack = max_stack
        self.max_locals = max_locals
        self.code = code
        self.exception_table = exception_table
        self.attributes = attributes

    def __repr__(self):
        return f"<Code max_stack={self.max_stack} max_locals={self.max_locals} code_len={len(self.code)}>"

class MethodInfo:
    def __init__(self, access_flags: int, name_index: int, descriptor_index: int, attributes: List[dict], cp=None):
        self.access_flags = access_flags
        self.name_index = name_index
        self.descriptor_index = descriptor_index
        self.attributes = attributes  # raw attribute dicts
        self.code: Optional[CodeAttribute] = None
        self._cp = cp  # constant pool for resolving names if needed
        # If there's a Code attribute, populate self.code
        for attr in attributes:
            if attr.get('name') == 'Code':
                self.code = attr.get('info')  # should be CodeAttribute instance

    def get_name(self) -> str:
        if self._cp:
            return self._cp.get_utf8(self.name_index)
        return f"#{self.name_index}"

    def get_descriptor(self) -> str:
        if self._cp:
            return self._cp.get_utf8(self.descriptor_index)
        return f"#{self.descriptor_index}"

    def __repr__(self):
        return f"<Method {self.get_name()} {self.get_descriptor()} flags=0x{self.access_flags:04x} code={self.code}>"
