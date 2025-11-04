#局部变量表,也叫本地变量表，每一个方法在执行的时候，都会创建一个自己局部变量表，用于存储方法的局部变量
# 局部变量表(Local Variable Table)是一组变量值存储空间，用于存放方法参数和方法内定义的局部变量。
# 局部变量表的容量以变量槽(Variable Slot)为最小单位，Java虚拟机规范并没有定义一个槽所应该占用内存空间的大小，
# 但是规定了一个槽应该可以存放一个32位以内的数据类型。一个局部变量可以保存一个类型为boolean、byte、char、short、int、float、reference和returnAddress类型的数据。
# reference类型表示对一个对象实例的引用。returnAddress类型是为jsr、jsr_w和ret指令服务的，目前已经很少使用了。
#最底层数据结构，无脑先用list
class LocalVars:
    """局部变量表，用 list 模拟"""
    def __init__(self, max_locals: int):
        self.slots = [None] * max_locals

    def set_int(self, index: int, val: int):
        self.slots[index] = val

    def get_int(self, index: int) -> int:
        return self.slots[index]

    def set_ref(self, index: int, ref):
        self.slots[index] = ref

    def get_ref(self, index: int):
        return self.slots[index]