#栈帧
#栈帧 = 局部变量表 + 操作数栈 + 线程引用

from .local_vars import LocalVars
from .operand_stack import OperandStack

class Frame:
    def __init__(self, thread, max_locals: int, max_stack: int):
        self.thread = thread
        self.local_vars = LocalVars(max_locals)
        self.operand_stack = OperandStack(max_stack)
        self.next_pc = 0          # 下一条指令地址