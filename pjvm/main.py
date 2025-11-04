#!/usr/bin/env python3
"""
@author: sunchenhao
@date: 2025-11-03
@description: Pjvm 主类入口
"""

import sys
from typing import List
from pjvm.classpath.classpath import Classpath
from pjvm.classfile.class_file import ClassFile
from pjvm.runtime.jthread import Thread
from pjvm.runtime.jclass import JClass
from pjvm.runtime.interpreter import interpret
from pjvm.runtime.frame import Frame


class Main:
    def __init__(self, class_path: str, main_class: str, args: List[str] = None):
        self.class_path = class_path
        self.main_class = main_class
        self.args = args or []

    def start(self):
        # 1. 使用你写的 Classpath 加载类
        cp = Classpath(jre_option="", cp_option=self.class_path)

        # 2. 转换类名格式：java.lang.Object -> java/lang/Object
        class_name = self.main_class.replace(".", "/")
        class_data, entry, error = cp.read_class(class_name)

        if error:
            print(f"找不到类 {self.main_class}：{error}")
            return

        # print(f"✅ 找到类：{self.main_class}")
        # print(f"📦 所属路径：{entry}")
        # print(f"🔢 字节码长度：{len(class_data)} 字节")

        # 3. TODO：后续解析字节码并执行
        self.execute_class_file(class_data)

    # def execute_class_file(self, class_data: bytes):
    #     """
    #     后续章节：解析字节码、执行指令
    #     当前阶段：仅打印前 30 字节
    #     """
    #     # print("🧠 字节码前 30 字节：")
    #     # print(class_data[:30])
    #     #解析字节码
    #     class_file = ClassFile(class_data)
    #     print(class_file)

    # def execute_class_file(self, class_data: bytes):
    #     class_file = ClassFile(class_data)

    #     # 1. 基本信息
    #     print("=" * 60)
    #     print(f"Class : {class_file.get_class_name()}")
    #     print(f"Super : {class_file.get_super_class_name()}")
    #     print(f"Magic : 0x{class_file.magic:08X}")
    #     print(f"Version: {class_file.major_version}.{class_file.minor_version}")
    #     print(f"Access : 0x{class_file.access_flags:04X}")
    #     print(f"Interfaces: {len(class_file.interfaces)}")
    #     print(f"Fields : {len(class_file.fields)}")
    #     print(f"Methods: {len(class_file.methods)}")
    #     print("=" * 60)

    #     # 2. 常量池（只打印 Utf8 和 Class，省屏）
    #     print("Constant Pool (snippet):")
    #     for idx, e in enumerate(class_file.constant_pool.entries):
    #         if e is None:
    #             continue
    #         tag = e['tag']
    #         if tag == 1:   # Utf8
    #             print(f"  #{idx:<3} Utf8     {e['value']}")
    #         elif tag == 7: # Class
    #             name = class_file.constant_pool.get_utf8(e['name_index'])
    #             print(f"  #{idx:<3} Class    {name}")
    #         elif tag == 9: # Fieldref
    #             print(f"  #{idx:<3} Fieldref")
    #         elif tag == 10:# Methodref
    #             print(f"  #{idx:<3} Methodref")
    #         elif tag == 12:# NameAndType
    #             print(f"  #{idx:<3} NameAndType")
    #         else:
    #             print(f"  #{idx:<3} tag={tag}")
    #     print("=" * 60)

    #     # 3. 方法列表（带描述符）
    #     print("Methods:")
    #     for m in class_file.methods:
    #         print(f"  {m.get_name()}{m.get_descriptor()}")
    #         # 如果有 Code 属性，把字节码长度也带上
    #         if hasattr(m, 'code') and m.code:
    #             print(f"    Code length: {len(m.code.code)} bytes")
    #     print("=" * 60)

    def execute_class_file(self, class_data: bytes):
        class_file = ClassFile(class_data)
        clazz = JClass(class_file)
        clazz.thread = Thread()

        # 找 main 方法
        main_method = class_file.find_method("main", "([Ljava/lang/String;)V")
        if not main_method:
            print("❌ main method not found")
            return

        # 创建帧并压栈
        code_attr = main_method.code
        frame = Frame(clazz.thread, code_attr.max_locals, code_attr.max_stack)
        clazz.thread.push_frame(frame)
        frame.method = main_method        # 反向引用，指令里要用
        # 把运行时类对象挂到方法上，供指令里使用
        main_method.clazz = clazz

        # 启动解释器
        interpret(main_method)



def main():
    # 简单命令行解析：python main.py -cp <classpath> <mainclass> [args...]
    args = sys.argv[1:]
    if not args:
        print("用法：python main.py [-cp 类路径] 主类名 [参数...]")
        return

    # 默认类路径为当前目录
    class_path = "."
    main_class = None
    i = 0
    if args[i] == "-cp":
        class_path = args[i + 1]
        i += 2
    if i < len(args):
        main_class = args[i]
        i += 1
    else:
        print("❌ 未指定主类名")
        return

    main_args = args[i:] if i < len(args) else []

    # 启动 JVM
    Main(class_path, main_class, main_args).start()


if __name__ == "__main__":
    main()