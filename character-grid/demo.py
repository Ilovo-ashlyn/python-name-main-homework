"""命令行演示与示例输出生成。

运行：
    python demo.py          # 教材样例 n=4，并写出 output/ 示例文件
    python demo.py 6        # 任意大小：每边 6 格
    python demo.py 2 --no-save
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tianzige import Style, build_grid, grid_spec, tian

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"

CUSTOM_STYLE = Style(cross="*", horizontal="=", vertical=":", fill=".")


def save_examples() -> int:
    """把三份示例输出存成文本，方便贴作业 / 博客。"""
    OUT.mkdir(parents=True, exist_ok=True)
    examples = {
        "grid_n4.txt": build_grid(4),                    # 教材样例规格
        "grid_n2.txt": build_grid(2),                    # 小田字格
        "grid_custom.txt": build_grid(3, cell_width=6,  # 自定义参数与字符
                                     cell_height=2, style=CUSTOM_STYLE),
    }
    for name, grid in examples.items():
        (OUT / name).write_text(grid + "\n", encoding="utf-8")
    return len(examples)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="字符田字格绘制（教材 P196 程序练习题 5.1）")
    parser.add_argument("n", nargs="?", type=int, default=4,
                        help="每边小格数量，默认 4（教材样例）")
    parser.add_argument("--no-save", action="store_true",
                        help="不写出 output/ 下的示例文件")
    args = parser.parse_args(argv)

    try:
        grid = tian(args.n)
    except ValueError as exc:
        parser.error(str(exc))
        return

    lines = grid.splitlines()
    print(grid)
    print()
    print(f"规格：n={args.n}，共 {len(lines)} 行，每行 {len(lines[0])} 字符"
          f"（理论 5n+1={5 * args.n + 1} 行，11n+1={11 * args.n + 1} 字符）")
    spec = grid_spec(args.n)
    print(f"核对：grid_spec({args.n}) -> {spec['lines']} 行 x {spec['width']} 字符")
    if not args.no_save:
        count = save_examples()
        print(f"已写出 output/ 下 {count} 个示例文件")


if __name__ == "__main__":
    main()
