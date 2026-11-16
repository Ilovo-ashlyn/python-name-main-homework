"""字符田字格绘制 —— 教材 P196 程序练习题 5.1。

原题要求：用字符方式打印输出田字格（教材图 5.12 / 5.16 的"更大的田字格"），
采用函数方式，以田字格宽度为参数，能够根据参数绘制任意大小的田字格。

教材样例规格：每边 n 个小格，每格 10 个短横、4 行格身：
    边框行 = ("+" + "-" * 10) * n + "+"
    格身行 = ("|" + " " * 10) * n + "|"
    总行数  = n * (1 + 4) + 1 = 5n + 1
    每行字符数 = n * (1 + 10) + 1 = 11n + 1
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_CELL_WIDTH = 10    # 每个小格横向的字符数（短横个数）
DEFAULT_CELL_HEIGHT = 4    # 每个小格纵向的行数（空格行数）


@dataclass(frozen=True)
class Style:
    """构成田字格的四种字符；换成别的单宽字符就能得到不同风格。"""
    cross: str = "+"       # 交点
    horizontal: str = "-"  # 横线
    vertical: str = "|"    # 竖线
    fill: str = " "        # 格内填充


DEFAULT_STYLE = Style()


def _positive_int(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} 必须是正整数，收到 {value!r}")


def grid_spec(cols: int, rows: int | None = None,
              cell_width: int = DEFAULT_CELL_WIDTH,
              cell_height: int = DEFAULT_CELL_HEIGHT) -> dict[str, int]:
    """动手写循环之前先算输出规格，改参数后有数可核对。"""
    if rows is None:
        rows = cols
    for value, name in ((cols, "cols"), (rows, "rows"),
                        (cell_width, "cell_width"),
                        (cell_height, "cell_height")):
        _positive_int(value, name)
    return {
        "cols": cols,
        "rows": rows,
        "lines": rows * (cell_height + 1) + 1,
        "width": cols * (cell_width + 1) + 1,
    }


def build_grid(cols: int, rows: int | None = None,
               cell_width: int = DEFAULT_CELL_WIDTH,
               cell_height: int = DEFAULT_CELL_HEIGHT,
               style: Style = DEFAULT_STYLE) -> str:
    """构造田字格，返回完整字符串（不直接打印，便于复用和测试）。

    cols / rows      横向、纵向小格数量；rows 省略时等于 cols（正方形）
    cell_width       每个小格的字符宽
    cell_height      每个小格的字符高
    style            四种构成字符，见 Style
    """
    spec = grid_spec(cols, rows, cell_width, cell_height)
    rows = spec["rows"]

    # 整行用「字符串乘法 + 拼接」一次生成，不用两层循环逐字符拼
    border = (style.cross + style.horizontal * cell_width) * cols + style.cross
    body = (style.vertical + style.fill * cell_width) * cols + style.vertical

    lines: list[str] = []
    for _ in range(rows):
        lines.append(border)
        lines.extend([body] * cell_height)
    lines.append(border)          # 补最后一条底边，否则少一行
    return "\n".join(lines)


def tian(n: int) -> str:
    """题目要求的接口：一个宽度参数 n，画出 n x n 的更大田字格。

    这正是教材课后答案 tian(n) 的形状（a = 5*n+1 行），
    区别是这里返回字符串而不是直接 print，方便复用与自检。
    """
    return build_grid(cols=n)


def draw_grid(n: int, *, rows: int | None = None,
              cell_width: int = DEFAULT_CELL_WIDTH,
              cell_height: int = DEFAULT_CELL_HEIGHT,
              style: Style = DEFAULT_STYLE) -> None:
    """直接打印版本，对应教材答案里的 print 写法。"""
    print(build_grid(n, rows, cell_width, cell_height, style))
