# 字节码 → 指令对象（最小 reader）

from symtable import Class
from .constants import LDC, INVOKE_VIRTUAL, GET_STATIC, RETURN
from .base import Instruction
from ..classfile import class_reader

# 操作码 → 类 映射（只放目前要用的）
OP_2_INST = {
    0x12: LDC,      # ldc
    0xB6: INVOKE_VIRTUAL,      # invokevirtual
    0xB2: GET_STATIC,      # getstatic
    0xB1: RETURN,      # return
}

def decode_opcode(code, pc):
    opcode = code[pc]
    cls = OP_2_INST.get(opcode)
    if not cls:
        raise NotImplementedError(f"Opcode 0x{opcode:02X} not implemented")
    inst = cls()
    # # 简易 reader：只给 fetch_operands 用
    # class Reader:
    #     def __init__(self, data, start):
    #         self.data = data
    #         self.pos = start
    #     def read_u1(self):
    #         val = self.data[self.pos]
    #         self.pos += 1
    #         return val

    #     def read_u2(self):
    #         val = int.from_bytes(self.data[self.pos:self.pos+2], byteorder='big')
    #         self.pos += 2
    #         return val

    
    reader = class_reader.ClassReader(code)
    reader.pos = pc + 1
    # reader = Reader(code, pc + 1)
    inst.fetch_operands(reader)
    return inst, reader.pos - pc   # 返回指令对象 + 长度