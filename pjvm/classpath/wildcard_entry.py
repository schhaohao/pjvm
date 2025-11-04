"""通配符 *.jar"""

import os
import glob
from .composite_entry import CompositeEntry

def new_wildcard_entry(path: str) -> CompositeEntry:
    base_dir = path[:-1]  # 去掉末尾的 *
    jar_pattern = os.path.join(base_dir, "*.jar")
    jar_files = glob.glob(jar_pattern)
    path_list = os.pathsep.join(jar_files)
    return CompositeEntry(path_list)