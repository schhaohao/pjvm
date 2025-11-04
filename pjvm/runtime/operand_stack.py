#操作数栈

class OperandStack:
    """操作数栈，用 list 模拟"""
    def __init__(self, max_stack: int):
        self.slots = []
        self.max_stack = max_stack

    def push_int(self, val: int):
        self.slots.append(val)

    def pop_int(self) -> int:
        return self.slots.pop()

    def push_ref(self, ref):
        self.slots.append(ref)

    def pop_ref(self):
        return self.slots.pop()

    def push_swap(self):  # swap 两个字
        a, b = self.slots.pop(), self.slots.pop()
        self.slots.extend([a, b])