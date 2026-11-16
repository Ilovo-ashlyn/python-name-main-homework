"""反例：没有 if __name__ 保护，把「只想运行时做」的事情写在顶层。

运行：python no_guard.py          —— 直接运行，看起来没问题
      python import_no_guard.py  —— 被导入时，副作用会被意外触发
"""

print(f"[顶层] no_guard.__name__ = {__name__!r}，副作用代码已执行")


def greet(name: str) -> str:
    return f"Hello, {name}!"


# 这些本该只在「自己主动运行」时执行，却暴露在顶层
print("[顶层] 假装正在执行一段耗时的测试 / 演示代码 ……")
print("[顶层] 假装正在连接数据库、写文件、发请求 ……")
