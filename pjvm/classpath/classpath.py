"""总入口，模拟 JVM 的类路径解析"""
import os
from .entry import new_entry
from .wildcard_entry import new_wildcard_entry
from .entry import Entry

class Classpath:
    def __init__(self, jre_option: str = "", cp_option: str = "."):
        self.boot_classpath = self._parse_boot_classpath(jre_option)
        self.ext_classpath = self._parse_ext_classpath(jre_option)
        self.user_classpath = new_entry(cp_option if cp_option else ".")

    def _parse_boot_classpath(self, jre_option: str):
        jre_dir = self._get_jre_dir(jre_option)
        return new_wildcard_entry(os.path.join(jre_dir, "lib", "*"))

    def _parse_ext_classpath(self, jre_option: str):
        jre_dir = self._get_jre_dir(jre_option)
        return new_wildcard_entry(os.path.join(jre_dir, "lib", "ext", "*"))

    def _get_jre_dir(self, jre_option: str) -> str:
        if jre_option and os.path.isdir(jre_option):
            return jre_option
        if os.path.isdir("./jre"):
            return "./jre"
        java_home = os.environ.get("JAVA_HOME")
        if java_home:
            return os.path.join(java_home, "jre")
        raise RuntimeError("Cannot find JRE directory")

    def read_class(self, class_name: str) -> tuple[bytes, Entry, Exception | None]:
        class_file = class_name + ".class"
        for entry in [self.boot_classpath, self.ext_classpath, self.user_classpath]:
            data, from_entry, err = entry.read_class(class_file)
            if err is None:
                return data, from_entry, None
        return b'', self.user_classpath, FileNotFoundError(f"class not found: {class_name}")

    def __str__(self):
        return str(self.user_classpath)