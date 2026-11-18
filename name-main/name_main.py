"""作业 1：if __name__ == '__main__': 是什么意思，为什么要写。

运行：python name_main.py     （纯标准库，不用装任何包）
"""

# 顶层代码：不管这个文件是「被直接运行」还是「被 import」，都会执行
print("【顶层】模块已加载，__name__ =", __name__)


def main():
    """只在主动运行本文件时才该做的事，全部放进 main()。"""
    print("【main】只有直接运行本文件时才会执行这一段")
    print("       直接运行 -> __name__ == '__main__'")
    print("       被 import -> __name__ 变成模块名 'name_main'，上面这段不执行")


if __name__ == "__main__":
    main()
