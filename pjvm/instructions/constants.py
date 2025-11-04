#ldc系列
#实现第一条指令 ldc（把常量池字符串压栈）
from .base import Instruction

class LDC(Instruction):
    def __init__(self):
        self.index = 0

    def fetch_operands(self, reader):
        self.index = reader.read_u1()  # ldc 取 1 字节索引

    def execute(self, frame):
        # 获取当前方法的常量池
        cp = frame.thread.current_frame().method.clazz.constant_pool
        # 从常量池中获取常量
        entry = cp.get(self.index)
        if entry['tag'] == 8:          # CONSTANT_String
            utf = cp.get_utf8(entry['string_index'])
            # 先直接用 Python str 当“Java 字符串对象”
            frame.operand_stack.push_ref(utf)
        elif entry['tag'] == 3:        # CONSTANT_Integer
            frame.operand_stack.push_int(entry['bytes'])
        else:
            raise ValueError("ldc unsupported tag")


#硬编码 System.out.println.伪指令（后面会挪到 native）
class INVOKE_VIRTUAL(Instruction):
    def fetch_operands(self, reader):
        self.index = reader.read_u2()  # invokevirtual 取 2 字节

    def execute(self, frame):
        cp = frame.thread.current_frame().method.clazz.constant_pool
        cls_name, name, desc = cp.get_methodref(self.index)
        if cls_name == "java.io.PrintStream" and name == "println" and desc == "(Ljava/lang/String;)V":
            ref = frame.operand_stack.pop_ref()  # 字符串
            frame.operand_stack.pop_ref()        # System.out 对象（忽略）
            print(ref)                           # 直接打印
        else:
            raise NotImplementedError("Only System.out.println is stubbed")

#getstatic 指令，获取静态字段
class GET_STATIC(Instruction):
    def fetch_operands(self, reader):
        self.index = reader.read_u2()   # 2 字节常量池索引

    def execute(self, frame):
        cp = frame.method.clazz.constant_pool
        # 解析 CONSTANT_Fieldref
        entry = cp.get(self.index)
        cls_idx = entry['class_index']
        name_and_type_idx = entry['name_and_type_index']

        cls_name = cp.get_class_name(cls_idx)
        name, desc = cp.get_name_and_type(name_and_type_idx)

        # 目前只硬编码 System.out
        if cls_name == "java.lang.System" and name == "out":
            # 先把伪 PrintStream 对象推栈（后面再细化）
            frame.operand_stack.push_ref("FakePrintStream")
            return

        raise NotImplementedError(f"Field {cls_name}.{name} not stubbed")

#0xB1 = return（方法正常结束，无返回值）
class RETURN(Instruction):
    def fetch_operands(self, reader):
        pass  # 无操作数

    def execute(self, frame):
        # 直接弹出当前栈帧，线程回到上一层
        frame.thread.pop_frame()