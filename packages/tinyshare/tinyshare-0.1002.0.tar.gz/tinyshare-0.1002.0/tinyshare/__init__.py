# -*- coding: utf-8 -*-
"""
TinyShare - A lightweight wrapper for tushare financial data API
"""

__version__ = "0.1002.0"

# 动态加载字节码模块
import sys
import importlib.util
from pathlib import Path

# 获取当前包目录
_pkg_dir = Path(__file__).parent

# 加载主模块字节码
_main_pyc = _pkg_dir / "__init__.pyc"
if _main_pyc.exists():
    # 使用exec直接执行字节码文件
    with open(_main_pyc, 'rb') as f:
        bytecode = f.read()
    
    # 创建代码对象并执行
    import marshal
    import types
    
    # 跳过.pyc文件头部信息（通常是16字节）
    code_offset = 16
    if len(bytecode) > code_offset:
        try:
            code_obj = marshal.loads(bytecode[code_offset:])
            exec(code_obj, globals())
        except Exception as e:
            print(f"字节码加载失败: {e}")
            # 如果字节码加载失败，尝试导入原始模块
            try:
                from . import *
            except ImportError:
                pass
else:
    # 如果没有字节码文件，尝试导入原始模块
    try:
        from . import *
    except ImportError:
        pass
