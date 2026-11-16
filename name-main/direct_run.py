"""最小标准模板：可以直接复制进自己的脚本。

运行：python direct_run.py
"""


def main() -> None:
    """程序真正要做的事写在这里。"""
    print("[main()] direct_run 正在运行")
    print(f"[main()] 此时 __name__ = {__name__!r}")


if __name__ == '__main__':
    main()
