#解释器主循环
from ..instructions import decode_opcode

# 解释器主循环
def interpret(method):
    # 获取方法的 code 属性
    code_attr = method.code
    code = code_attr.code
    thread = method.clazz.thread
    frame = thread.current_frame()
    pc = 0
    while pc < len(code):
        inst, length = decode_opcode(code, pc)
        frame.next_pc = pc + length
        inst.execute(frame)
        pc = frame.next_pc