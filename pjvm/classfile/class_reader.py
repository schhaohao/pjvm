# classfile/class_reader.py
import struct

class ClassReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.length = len(data)

    def read_u1(self) -> int:
        if self.pos + 1 > self.length:
            raise EOFError("Unexpected EOF while reading u1")
        val = self.data[self.pos]
        self.pos += 1
        return val

    def read_u2(self) -> int:
        if self.pos + 2 > self.length:
            raise EOFError("Unexpected EOF while reading u2")
        val = struct.unpack_from('>H', self.data, self.pos)[0]
        self.pos += 2
        return val

    def read_u4(self) -> int:
        if self.pos + 4 > self.length:
            raise EOFError("Unexpected EOF while reading u4")
        val = struct.unpack_from('>I', self.data, self.pos)[0]
        self.pos += 4
        return val

    def read_bytes(self, n: int) -> bytes:
        if self.pos + n > self.length:
            raise EOFError("Unexpected EOF while reading bytes")
        val = self.data[self.pos:self.pos + n]
        self.pos += n
        return val

    def peek_u1(self) -> int:
        if self.pos >= self.length:
            raise EOFError("Unexpected EOF while peeking u1")
        return self.data[self.pos]

    def read_utf(self, length: int) -> str:
        bs = self.read_bytes(length)
        return bs.decode('utf-8', errors='replace')

if __name__ == "__main__":
    #读取字节码文件
    data = open("/Users/sunchenhao/Documents/Workspace1/Java_projects/Java_study/src/exp1/HelloWorld.class", "rb").read()
    reader = ClassReader(data)
    print(reader.read_u4())
    

