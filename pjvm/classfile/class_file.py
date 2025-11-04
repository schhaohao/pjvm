# classfile/class_file.py
from .class_reader import ClassReader
from .constant_pool import ConstantPool, CONSTANT_Class, CONSTANT_Fieldref, CONSTANT_Methodref, CONSTANT_InterfaceMethodref, CONSTANT_String, CONSTANT_Integer, CONSTANT_Float, CONSTANT_Long, CONSTANT_Double, CONSTANT_NameAndType, CONSTANT_Utf8
from .field_info import FieldInfo
from .method_info import MethodInfo, CodeAttribute
from typing import List, Optional

class ClassFile:
    def __init__(self, data: bytes):
        self.reader = ClassReader(data)
        self.magic = None
        self.minor_version = None
        self.major_version = None
        self.constant_pool: Optional[ConstantPool] = None
        self.access_flags = None
        self.this_class = None
        self.super_class = None
        self.interfaces = []
        self.fields: List[FieldInfo] = []
        self.methods: List[MethodInfo] = []
        self.attributes = []
        self.parse()

    def parse(self):
        r = self.reader
        self.magic = r.read_u4()
        if self.magic != 0xCAFEBABE:
            raise ValueError(f"Invalid class file magic: {hex(self.magic)}")
        self.minor_version = r.read_u2()
        self.major_version = r.read_u2()
        self._read_constant_pool()
        self.access_flags = r.read_u2()
        self.this_class = r.read_u2()
        self.super_class = r.read_u2()
        interfaces_count = r.read_u2()
        for _ in range(interfaces_count):
            self.interfaces.append(r.read_u2())
        self._read_fields()
        self._read_methods()
        self._read_attributes()

    def _read_constant_pool(self):
        r = self.reader
        cp_count = r.read_u2()
        # index 0 unused
        entries = [None] * cp_count
        i = 1
        while i < cp_count:
            tag = r.read_u1()
            if tag == CONSTANT_Utf8:
                length = r.read_u2()
                value = r.read_utf(length)
                entries[i] = {'tag': tag, 'value': value}
            elif tag in (CONSTANT_Integer, CONSTANT_Float):
                bytes_ = r.read_u4()
                entries[i] = {'tag': tag, 'bytes': bytes_}
            elif tag in (CONSTANT_Long, CONSTANT_Double):
                high_bytes = r.read_u4()
                low_bytes = r.read_u4()
                # Store as tuple high/low for now
                entries[i] = {'tag': tag, 'high': high_bytes, 'low': low_bytes}
                i += 1  # long/double take two cp entries
            elif tag == CONSTANT_Class:
                name_index = r.read_u2()
                entries[i] = {'tag': tag, 'name_index': name_index}
            elif tag in (CONSTANT_Fieldref, CONSTANT_Methodref, CONSTANT_InterfaceMethodref):
                class_index = r.read_u2()
                name_and_type_index = r.read_u2()
                entries[i] = {'tag': tag, 'class_index': class_index, 'name_and_type_index': name_and_type_index}
            elif tag == CONSTANT_String:
                string_index = r.read_u2()
                entries[i] = {'tag': tag, 'string_index': string_index}
            elif tag == CONSTANT_NameAndType:
                name_index = r.read_u2()
                descriptor_index = r.read_u2()
                entries[i] = {'tag': tag, 'name_index': name_index, 'descriptor_index': descriptor_index}
            elif tag in (15, 16, 18):  # MethodHandle, MethodType, InvokeDynamic - read minimal
                if tag == 15:
                    ref_kind = r.read_u1()
                    ref_index = r.read_u2()
                    entries[i] = {'tag': tag, 'ref_kind': ref_kind, 'ref_index': ref_index}
                elif tag == 16:
                    descriptor_index = r.read_u2()
                    entries[i] = {'tag': tag, 'descriptor_index': descriptor_index}
                elif tag == 18:
                    bootstrap_method_attr_index = r.read_u2()
                    name_and_type_index = r.read_u2()
                    entries[i] = {'tag': tag, 'bootstrap_method_attr_index': bootstrap_method_attr_index, 'name_and_type_index': name_and_type_index}
            else:
                raise NotImplementedError(f"Constant pool tag {tag} not implemented at index {i}")
            i += 1
        self.constant_pool = ConstantPool(entries)

    def _read_fields(self):
        r = self.reader
        fields_count = r.read_u2()
        for _ in range(fields_count):
            access_flags = r.read_u2()
            name_index = r.read_u2()
            descriptor_index = r.read_u2()
            attributes = self._read_attributes_raw()
            field = FieldInfo(access_flags, name_index, descriptor_index, attributes)
            self.fields.append(field)

    def _read_methods(self):
        r = self.reader
        methods_count = r.read_u2()
        for _ in range(methods_count):
            access_flags = r.read_u2()
            name_index = r.read_u2()
            descriptor_index = r.read_u2()
            attributes = self._read_attributes_raw(constant_pool=self.constant_pool)
            # convert Code attribute into CodeAttribute instance when present
            processed_attrs = []
            code_attr_obj = None
            for attr in attributes:
                if attr['name'] == 'Code':
                    info = attr['info']
                    processed_attrs.append({'name': 'Code', 'info': info})
                    code_attr_obj = info
                else:
                    processed_attrs.append(attr)
            method = MethodInfo(access_flags, name_index, descriptor_index, processed_attrs, cp=self.constant_pool)
            # attach CodeAttribute if we parsed one
            if code_attr_obj:
                method.code = code_attr_obj
            self.methods.append(method)

    def _read_attributes(self):
        # top-level attributes (class attributes)
        r = self.reader
        attrs = self._read_attributes_raw()
        self.attributes = attrs

    def _read_attributes_raw(self, constant_pool: ConstantPool = None) -> List[dict]:
        if constant_pool is None:
            constant_pool = self.constant_pool
        r = self.reader
        attrs = []
        attributes_count = r.read_u2()
        for _ in range(attributes_count):
            name_index = r.read_u2()
            attr_name = constant_pool.get_utf8(name_index)
            attr_length = r.read_u4()
            if attr_name == 'Code':
                max_stack = r.read_u2()
                max_locals = r.read_u2()
                code_length = r.read_u4()
                code_bytes = r.read_bytes(code_length)
                exception_table_length = r.read_u2()
                exception_table = []
                for _ in range(exception_table_length):
                    start_pc = r.read_u2()
                    end_pc = r.read_u2()
                    handler_pc = r.read_u2()
                    catch_type = r.read_u2()
                    exception_table.append({'start_pc': start_pc, 'end_pc': end_pc, 'handler_pc': handler_pc, 'catch_type': catch_type})
                # read attributes inside Code
                code_attrs = []
                code_attrs_count = r.read_u2()
                for _ in range(code_attrs_count):
                    sub_name_index = r.read_u2()
                    sub_attr_name = constant_pool.get_utf8(sub_name_index)
                    sub_attr_len = r.read_u4()
                    sub_info = r.read_bytes(sub_attr_len)
                    # we can parse some sub-attributes later; for now store raw bytes
                    code_attrs.append({'name': sub_attr_name, 'info_raw': sub_info})
                code_attr = CodeAttribute(max_stack, max_locals, code_bytes, exception_table, code_attrs)
                attrs.append({'name': 'Code', 'info': code_attr})
            else:
                # generic attribute: read raw bytes
                info_bytes = r.read_bytes(attr_length)
                attrs.append({'name': attr_name, 'info_raw': info_bytes})
        return attrs

    # convenience methods
    def get_class_name(self) -> str:
        return self.constant_pool.get_class_name(self.this_class)

    def get_super_class_name(self) -> Optional[str]:
        if self.super_class == 0:
            return None
        return self.constant_pool.get_class_name(self.super_class)

    def find_method(self, name: str, descriptor: str):
        for m in self.methods:
            try:
                if m.get_name() == name and m.get_descriptor() == descriptor:
                    return m
            except Exception:
                pass
        return None

    def __repr__(self):
        return f"<ClassFile {self.get_class_name()} v{self.major_version}.{self.minor_version} methods={len(self.methods)} fields={len(self.fields)}>"
