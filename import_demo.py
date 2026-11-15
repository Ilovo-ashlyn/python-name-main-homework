"""导入 demo_module，观察保护块里的代码不会自动执行。

运行：python import_demo.py
"""

print("[开始] 准备 import demo_module")

import demo_module  # noqa: E402  —— 导入时会执行 demo_module 的顶层代码

print(f"[本文件] import_demo.__name__ = {__name__!r}")
print("[本文件] 我只是想复用一个函数：", demo_module.greet("GitHub"))
print("[本文件] 需要时也可以手动调用：demo_module.main()，但默认不会自动跑")
