#运行时类对象（先只存常量池）

class JClass:
    def __init__(self, class_file):
        self.constant_pool = class_file.constant_pool
        self.name = class_file.get_class_name()
        self.methods = class_file.methods   # MethodInfo 列表