# 从0到1用Python实现Java虚拟机

## 先看怎么用

```python
git clone https://github.com/schhaohao/pjvm.git

cd pjvm

pip install .

pjvm -cp /path/to/classfile HelloWorld
```

## 然后一句话总结pjvm怎么实现jvm的

> **“把磁盘上的 `.class` 字节码，变成 Python 对象，再一条条指令喂给解释器，最终用 Python 的 `print()` 兑现了 `System.out.println()`。”**

## 不要着急，先全流程一览（从文件到文字）

| 阶段                      | 输入 → 输出                                                                      | 关键模块                                     |
| ------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------- |
| ①**寻找字节码**    | `HelloWorld.class` 路径 → 437 字节原始数据                                     | `Classpath`                                |
| ②**解析静态结构**  | 437 字节 →`ClassFile` 对象（常量池、方法表、Code 属性）                        | `ClassFile` + `ConstantPool`             |
| ③**装载运行时类**  | `ClassFile` → `JClass`（运行时壳）                                           | `JClass`                                   |
| ④**定位入口**      | 在方法表里找 `main([Ljava/lang/String;)V`                                       | `find_method()`                            |
| ⑤**创建栈帧**      | `max_locals=1, max_stack=3` → 新建 `Frame`                                   | `Frame` + `LocalVars` + `OperandStack` |
| ⑥**指令解码**      | 字节码流 → 指令对象数组（`ldc`, `getstatic`, `invokevirtual`, `return`） | `decode_opcode()`                          |
| ⑦**解释执行**      | 循环取指 → 执行 → 修改 PC/栈/局部变量                                           | `interpreter`                              |
| ⑧**硬编码 native** | 遇到 `System.out.println` → 直接 `print(ref)`                                | `GET_STATIC` + `INVOKE_VIRTUAL` 桩       |
| ⑨**正常返回**      | `return` 指令 → 弹帧 → 线程结束                                               | `RETURN`                                   |

## 不废话，不讲什么理论，直接上干货

```Java
//java代码

public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, Class File!");
    }
}
```

```shell
# javac HelloWorld.java. --> HelloWorld.class
# vim HelloWorld.class.  没错，此时你会看到一堆乱码。 只要输入:%!xdd就可以看到十六进制代码

00000000: cafe babe 0000 0037 001d 0a00 0600 0f09  .......7........
00000010: 0010 0011 0800 120a 0013 0014 0700 1507  ................
00000020: 0016 0100 063c 696e 6974 3e01 0003 2829  .....<init>...()
00000030: 5601 0004 436f 6465 0100 0f4c 696e 654e  V...Code...LineN
00000040: 756d 6265 7254 6162 6c65 0100 046d 6169  umberTable...mai
00000050: 6e01 0016 285b 4c6a 6176 612f 6c61 6e67  n...([Ljava/lang
00000060: 2f53 7472 696e 673b 2956 0100 0a53 6f75  /String;)V...Sou
00000070: 7263 6546 696c 6501 000f 4865 6c6c 6f57  rceFile...HelloW
00000080: 6f72 6c64 2e6a 6176 610c 0007 0008 0700  orld.java.......
00000090: 170c 0018 0019 0100 1248 656c 6c6f 2c20  .........Hello,
000000a0: 436c 6173 7320 4669 6c65 2107 001a 0c00  Class File!.....
000000b0: 1b00 1c01 000f 6578 7031 2f48 656c 6c6f  ......exp1/Hello
000000c0: 576f 726c 6401 0010 6a61 7661 2f6c 616e  World...java/lan
000000d0: 672f 4f62 6a65 6374 0100 106a 6176 612f  g/Object...java/
000000e0: 6c61 6e67 2f53 7973 7465 6d01 0003 6f75  lang/System...ou
000000f0: 7401 0015 4c6a 6176 612f 696f 2f50 7269  t...Ljava/io/Pri
00000100: 6e74 5374 7265 616d 3b01 0013 6a61 7661  ntStream;...java
00000110: 2f69 6f2f 5072 696e 7453 7472 6561 6d01  /io/PrintStream.
00000120: 0007 7072 696e 746c 6e01 0015 284c 6a61  ..println...(Lja
00000130: 7661 2f6c 616e 672f 5374 7269 6e67 3b29  va/lang/String;)
00000140: 5600 2100 0500 0600 0000 0000 0200 0100  V.!.............
00000150: 0700 0800 0100 0900 0000 1d00 0100 0100  ................
00000160: 0000 052a b700 01b1 0000 0001 000a 0000  ...*............
00000170: 0006 0001 0000 0003 0009 000b 000c 0001  ................
00000180: 0009 0000 0025 0002 0001 0000 0009 b200  .....%..........
00000190: 0212 03b6 0004 b100 0000 0100 0a00 0000  ................
000001a0: 0a00 0200 0000 0500 0800 0600 0100 0d00  ................
000001b0: 0000 0200 0e0a                           ......
```

把这一长串十六进制「拆成 JVM 能懂的表格」→「喂给我们的解释器」→「在终端打印出文字」的完整旅程，用「一行十六进制 → 一步动作」的方式讲给你听。

---

### ✅ 全局鸟瞰（4 大步）

1. 寻找字节码     `Classpath`
2. 静态解析      `ClassFile` + `ConstantPool`
3. 运行时装载     `JClass` + `Thread` + `Frame`
4. 解释执行      `interpreter` + `instructions` 桩

---

### ✅ 把 0x 流切成 JVM 标准chunk

| 偏移      | 十六进制                 | 含义（JVM 规范）                                                                                       | 我们代码的对应动作                               |
| --------- | ------------------------ | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------ |
| 0x00-0x03 | `CA FE BA BE`          | 魔数                                                                                                   | `ClassFile.parse()` 校验 `magic==0xCAFEBABE` |
| 0x04-0x05 | `00 00`                | 次版本号                                                                                               | `minor_version=0`                              |
| 0x06-0x07 | `00 37`                | 主版本号                                                                                               | `major_version=55` → Java 11                  |
| 0x08-0x09 | `00 1D`                | 常量池项数                                                                                             | `cp_count=29`（索引 0 空，实际 28 项）         |
| 0x0A-...  | 后面全是 28 个常量池条目 | 我们逐字节 `read_u1` 判 tag → 构造 `{'tag':xx,'value':xx}` dict → 丢进 `ConstantPool(entries)` |                                                  |

---

### ✅ 常量池「翻译」成人类可读（片段）

| 索引 | tag | 内容（我们解析后）                                      |
| ---- | --- | ------------------------------------------------------- |
| #1   | 10  | Methodref `java/lang/Object."<init>":()V`             |
| #2   | 9   | Fieldref `java/lang/System.out:Ljava/io/PrintStream;` |
| #3   | 7   | Class `exp1/HelloWorld`                               |
| #4   | 7   | Class `java/lang/Object`                              |
| #18  | 8   | String 指向 #19 → "Hello, Class File!"                 |

#### 怎么翻译常量池？

常量池的解析 = **「先读 1 字节 tag → 再按 tag 规定读后面 N 字节」** 的循环。
下面把 **HelloWorld 的 28 项** 一行行拆开给你看（只列关键几项，其余同理）。

**前置知识**

- 索引从 **1** 开始，0 留空
- 每项第一个字节 = **tag**（对应 JVM 规范）
- tag 决定 **后续字节数和含义**

| tag | 常量类型    | 后面跟多少字节                                  |
| --- | ----------- | ----------------------------------------------- |
| 1   | Utf8        | 2 字节长度 + 任意 utf8 内容                     |
| 7   | Class       | 2 字节 name_index                               |
| 8   | String      | 2 字节 string_index                             |
| 9   | Fieldref    | 2 字节 class_index + 2 字节 name_and_type_index |
| 10  | Methodref   | 同上 4 字节                                     |
| 12  | NameAndType | 2 字节 name_index + 2 字节 descriptor_index     |

**正式拆解（从 0x0A 开始）**

```
偏移  十六进制        解析过程                     结果项
0x0A  0A             tag=10 Methodref             #1
      00 06            class_index=6
      00 0F            name_and_type_index=15

0x0F  09             tag=9 Fieldref               #2
      00 10            class_index=16
      00 11            name_and_type_index=17

0x14  08             tag=8 String                 #3
      00 12            string_index=18

0x17  0A             tag=10 Methodref             #4
      00 13            class_index=19
      0x1B 00 1C        name_and_type_index=28

...（下面同理）...
```

**对应我们代码里的动作（`ClassFile._read_constant_pool()`）**

```python
i = 1
while i < cp_count:
    tag = reader.read_u1()      # ① 先读 tag
    if tag == 1:                # ② Utf8
        length = reader.read_u2()
        value  = reader.read_bytes(length).decode('utf-8')
        entries[i] = {'tag': 1, 'value': value}
    elif tag == 7:              # ③ Class
        name_index = reader.read_u2()
        entries[i] = {'tag': 7, 'name_index': name_index}
    elif tag in (9, 10):        # ④ Fieldref / Methodref
        class_index = reader.read_u2()
        name_and_type_index = reader.read_u2()
        entries[i] = {'tag': tag, 'class_index': class_index,
                      'name_and_type_index': name_and_type_index}
    elif tag == 8:              # ⑤ String
        string_index = reader.read_u2()
        entries[i] = {'tag': 8, 'string_index': string_index}
    elif tag == 12:             # ⑥ NameAndType
        name_index = reader.read_u2()
        descriptor_index = reader.read_u2()
        entries[i] = {'tag': 12, 'name_index': name_index,
                      'descriptor_index': descriptor_index}
    # ... 其余 tag 同理 ...
    i += 1
```

**以 HelloWorld 为例，前几项结果**

| 索引 | 我们解析后得到的 dict                                         |
| ---- | ------------------------------------------------------------- |
| #1   | `{'tag': 10, 'class_index': 6, 'name_and_type_index': 15}`  |
| #2   | `{'tag': 9, 'class_index': 16, 'name_and_type_index': 17}`  |
| #3   | `{'tag': 8, 'string_index': 18}`                            |
| #4   | `{'tag': 10, 'class_index': 19, 'name_and_type_index': 20}` |

**一句话总结**

> **“读 1 字节 tag → 按表拿长度 → 读后续字节 → 装进 dict”** 循环 28 次，
> 常量池就从冰冷的十六进制变成 **Python 能查的 `ConstantPool` 对象**！

---

### ✅ 方法表 & Code 属性

主方法 `main` 在方法表第 2 项：

```
access_flags=0x0009 (public static)
name_index=#11 → "main"
descriptor_index=#12 → "([Ljava/lang/String;)V"
attributes_count=1
└─ Code attribute
    max_stack=3
    max_locals=1
    code_length=9
    code=[B2 00 02 12 03 B6 00 04 B1]  ← 9 字节真指令
```

---

### ✅ 9 字节指令流 → 我们逐条解释

| PC | 字节码       | 助记符            | 我们的 `instructions` 动作                                         |
| -- | ------------ | ----------------- | -------------------------------------------------------------------- |
| 0  | `B2 00 02` | getstatic #2      | `GET_STATIC` 把常量池 #2 解析 → `System.out` 伪对象压栈         |
| 3  | `12 03`    | ldc #18           | `LDC` 把 #18 常量池项（"Hello, Class File!"）压栈                  |
| 5  | `B6 00 04` | invokevirtual #27 | `INVOKE_VIRTUAL` 桩：弹出两参数 → `print("Hello, Class File!")` |
| 8  | `B1`       | return            | `RETURN` 指令 → `frame.thread.pop_frame()` → 解释器循环结束    |

---

### ✅ 我们自制 PJVM 的「执行时间线」

1. `pjvm -cp xxx HelloWorld`
2. `Classpath` 找到 `./HelloWorld.class` → 437 字节 → `ClassFile(data)`
3. 解析常量池、方法表 → 拿到 `main` 方法 `Code` 属性
4. 创建 `Thread` → 推 `Frame(max_locals=1, max_stack=3)`
5. `interpreter` 循环：`decode_opcode()` → 指令对象 → `inst.execute(frame)`
6. 遇到 `System.out.println` 硬编码桩 → 直接 `print(ref)`
7. `return` 弹帧 → 线程栈空 → 程序正常退出

---

### ✅ 一句话收尾

> **「CA FE BA BE」进门，常量池当字典，栈帧做舞台，9 字节指令跳完一支舞，Python 的 `print()` 替 JVM 喊出了第一声 Hello！**
>

### ✅ 时序图（HelloWorld 主方法 4 条指令）

```
PC=0  ldc           #18  "Hello, Class File!"   → 压栈
PC=2  getstatic     #16  System.out             → 压 FakePrintStream
PC=5  invokevirtual #27  PrintStream.println    → 弹出两参数，print()
PC=8  return                                       → 弹帧，结束
```

---

### ✅ 你现在拥有的「迷你 JVM」功能

| 模块       | 已实现                          |
| ---------- | ------------------------------- |
| 类路径加载 | ✅ 目录、JAR、通配符            |
| 常量池解析 | ✅ 15 种 tag 全覆盖             |
| 栈帧结构   | ✅ 局部变量表 + 操作数栈        |
| 指令框架   | ✅ 可无限扩展                   |
| 解释器循环 | ✅ PC 驱动                      |
| native 桩  | ✅`System.out.println` 硬编码 |
| 程序返回   | ✅`return` 正常结束           |

---

### ✅ 下一步（可选，随时继续）

1. **补跳转指令** (`if_icmpeq`, `goto`) → 让 `if/while` 可用
2. **实现 `invokestatic` / `invokespecial`** → 支持普通方法调用栈
3. **Java 字符串池** → 不再用 Python `str` 冒充
4. **类验证 & 异常抛栈** → 行号、StackMapTable
5. **native 方法注册表** → 把硬编码挪出去，支持 `java.lang.Math` 等

---

🎯 **今天你已经让 Java 代码在 Python 里跑起来了！**
**下一步想补哪条指令，随时喊我手把手继续！**
