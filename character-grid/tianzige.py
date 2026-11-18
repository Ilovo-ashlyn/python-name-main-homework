"""作业 3：字符田字格（教材 P196 5.1）。

运行：python tianzige.py 4     （参数 = 每边格子数，默认 2；纯标准库）
"""
import sys


def tian(n):
    """返回 n×n 个田字格组成的字符串：每格 10 个短横、4 行格身。"""
    if n < 1:
        raise ValueError("n 必须是正整数")
    border = ("+" + "-" * 10) * n + "+"
    body = ("|" + " " * 10) * n + "|"
    rows = []
    for _ in range(n):
        rows.append(border)
        rows += [body] * 4
    rows.append(border)          # 别忘了最后一条底边
    return "\n".join(rows)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    print(tian(n))
    print(f"\n共 {5 * n + 1} 行，每行 {11 * n + 1} 个字符")
