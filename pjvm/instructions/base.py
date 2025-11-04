#指令基类，所有指令都继承自这个类

from abc import ABC, abstractmethod

class Instruction(ABC):
    @abstractmethod
    def fetch_operands(self, reader):
        """从字节码里取操作数（无操作数就空实现）"""
        pass

    @abstractmethod
    def execute(self, frame):
        """执行语义"""
        pass