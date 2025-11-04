# setup.py
from setuptools import setup, find_packages

setup(
    name="pjvm",
    version="0.1.0",
    description="A toy JVM written in pure Python",
    author="sunchenhao",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "pjvm=pjvm.__main__:main",   # ← 命令名 → 函数
        ]
    },
)