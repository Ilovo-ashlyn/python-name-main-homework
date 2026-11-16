"""导入没有保护块的模块，观察「不该发生的副作用」。

运行：python import_no_guard.py
"""

print("[开始] 我其实只想用 no_guard.greet() 这一个函数")

import no_guard  # noqa: E402  —— 注意：还没调用任何函数，副作用就已经发生了

print(f"[本文件] import_no_guard.__name__ = {__name__!r}")
print("[本文件] 真正想要的只是：", no_guard.greet("GitHub"))
print("[结论] 没有保护块，import 会连带执行模块顶层的全部副作用")
