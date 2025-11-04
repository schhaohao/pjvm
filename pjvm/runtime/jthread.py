#线程
#线程 = 栈的列表
from .frame import Frame

class Thread:
    def __init__(self):
        self.stack = []          # 栈的栈

    def push_frame(self, frame: Frame):
        self.stack.append(frame)

    def pop_frame(self) -> Frame:
        return self.stack.pop()

    def current_frame(self) -> Frame:
        return self.stack[-1]