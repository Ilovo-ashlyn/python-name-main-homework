"""自检：形状规格、边框位置、参数校验、自定义字符、打印接口、示例文件。

运行：python selftest.py（请先跑一次 python demo.py）
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

from tianzige import (Style, build_grid, draw_grid, grid_spec, tian)
from demo import CUSTOM_STYLE

ROOT = Path(__file__).resolve().parent


def test_textbook_spec() -> None:
    """教材答案口径：n 格 -> 5n+1 行，每行 11n+1 字符，每 5 行一条边框。"""
    for n in (1, 2, 4, 8):
        lines = tian(n).splitlines()
        assert len(lines) == 5 * n + 1, f"n={n} 行数错误"
        assert all(len(line) == 11 * n + 1 for line in lines), f"n={n} 行宽不一致"
        for index, line in enumerate(lines):
            if index % 5 == 0:
                assert line == ("+" + "-" * 10) * n + "+", f"n={n} 第 {index} 行边框错误"
            else:
                assert line == ("|" + " " * 10) * n + "|", f"n={n} 第 {index} 行格身错误"
        print(f"  n={n:<2}  {len(lines):>3} 行 x {len(lines[0]):>3} 字符  OK")


def test_spec_function() -> None:
    spec = grid_spec(4)
    assert spec["lines"] == 21 and spec["width"] == 45
    assert grid_spec(3, cell_height=2)["lines"] == 10
    print("  grid_spec 规格推算 OK")


def test_arbitrary_size() -> None:
    """任意行列、任意格宽格高。"""
    grid = build_grid(cols=3, rows=2)
    assert len(grid.splitlines()) == 2 * 5 + 1
    assert len(grid.splitlines()[0]) == 3 * 11 + 1
    grid2 = build_grid(3, cell_width=6, cell_height=2)
    assert len(grid2.splitlines()) == 3 * 3 + 1
    assert len(grid2.splitlines()[0]) == 3 * 7 + 1
    print("  非正方形 / 自定义格宽格高 OK")


def test_custom_style() -> None:
    grid = build_grid(2, style=CUSTOM_STYLE)
    assert grid.splitlines()[0] == ("*" + "=" * 10) * 2 + "*"
    assert grid.splitlines()[1] == (":" + "." * 10) * 2 + ":"
    print("  自定义边框字符 OK")


def test_invalid_input() -> None:
    for bad in (0, -1, 1.5, "4", True, None):
        try:
            build_grid(bad)
        except ValueError:
            continue
        raise AssertionError(f"应当拒绝 cols={bad!r}")
    for kwargs in ({"rows": 0}, {"cell_width": 0}, {"cell_height": -2}):
        try:
            build_grid(2, **kwargs)
        except ValueError:
            continue
        raise AssertionError(f"应当拒绝 {kwargs}")
    print("  非法参数（0 / 负数 / 小数 / 字符串 / 布尔）OK")


def test_print_interface() -> None:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        draw_grid(2)
    assert buffer.getvalue().strip() == tian(2)
    print("  draw_grid 打印与 tian 返回一致 OK")


def test_output_files() -> None:
    expected = {
        "grid_n4.txt": build_grid(4),
        "grid_n2.txt": build_grid(2),
        "grid_custom.txt": build_grid(3, cell_width=6, cell_height=2,
                                     style=Style("*", "=", ":", ".")),
    }
    for name, grid in expected.items():
        path = ROOT / "output" / name
        assert path.exists(), f"缺少示例文件 {name}"
        assert path.read_text(encoding="utf-8").strip() == grid
        print(f"  {name:<18} {len(grid.splitlines()):>3} 行  OK")


def main() -> None:
    test_textbook_spec()
    test_spec_function()
    test_arbitrary_size()
    test_custom_style()
    test_invalid_input()
    test_print_interface()
    test_output_files()
    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
