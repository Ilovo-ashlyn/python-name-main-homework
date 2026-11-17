"""按阶数生成科赫雪花（0~4 阶）图片与统计表（本作业的运行入口）。

运行：python draw_all.py                 # 生成 0~4 阶共 5 张 PNG + 图片画廊
      python draw_all.py 3               # 只生成 3 阶这一张
      python draw_all.py 0 2 4           # 只生成指定几阶
      python draw_all.py --show          # 生成后自动用浏览器打开画廊看图
输出：output/koch_0.png ... koch_4.png
      output/index.html —— 把已有图片内嵌在一起的画廊，双击即可看图。

注意：控制台是纯文本终端，不会显示图片本身；图片是 output/ 下的文件。
"""

from __future__ import annotations

import argparse
import base64
import webbrowser
from pathlib import Path

from koch_snowflake import (FILL, GUIDE, INK, MAX_ORDER, MIN_ORDER, TEXT,
                            Canvas, Viewport, area_ratio, check_order,
                            perimeter_ratio, segment_count, snowflake)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
W = H = 640
PLOT = (60, 80, 520, 520)            # 绘图区 left, top, width, height（正方形，不变形）
VIEW = (-1.6, 1.6, -1.6, 1.6)       # 数学坐标范围

CAPTIONS = {
    "koch_0.png": "0 阶 · 初始等边三角形（3 条线段）",
    "koch_1.png": "1 阶 · 每条边鼓出一个小三角（12 条线段）",
    "koch_2.png": "2 阶 · 六角星轮廓出现（48 条线段）",
    "koch_3.png": "3 阶 · 雪花细节开始密集（192 条线段）",
    "koch_4.png": "4 阶 · 题目要求的最高阶（768 条线段）",
}


def draw_one(order: int) -> Path:
    """画一张指定阶数的雪花，返回 PNG 路径。"""
    check_order(order)
    points = snowflake(order, side=2.0)
    vp = Viewport(*VIEW, *PLOT)

    c = Canvas(W, H)
    c.frame(PLOT[0], PLOT[1],
            PLOT[0] + PLOT[2] - 1, PLOT[1] + PLOT[3] - 1, GUIDE)

    pixels = [vp.to_px(x, y) for x, y in points]
    c.fill_polygon(pixels, FILL)                  # 淡蓝填充雪花内部
    width = 2 if order <= 2 else 1               # 高阶线段太密，细线才不糊
    for i in range(len(pixels) - 1):
        c.line(*pixels[i], *pixels[i + 1], INK, width)

    c.text(60, 16, "KOCH SNOWFLAKE", TEXT, 2)
    c.text(60, 46,
           f"ORDER {order}   SEGMENTS {segment_count(order)}   "
           f"PERIMETER X{perimeter_ratio(order):.4f}", TEXT, 1)
    c.text(60, 612,
           f"AREA RATIO {area_ratio(order):.4f}   LIMIT 1.6000   "
           f"DIMENSION LOG4/LOG3 = 1.2619", TEXT, 1)
    return c.save(OUT / f"koch_{order}.png")


def write_gallery(files: list[Path]) -> Path:
    """把已有图片内嵌成自包含 HTML 画廊，单文件双击即可看图。"""
    cards = []
    for path in files:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        caption = CAPTIONS.get(path.name, path.name)
        cards.append(
            "<figure>\n"
            '  <img src="data:image/png;base64,' + encoded + '" alt="'
            + path.name + '">\n'
            "  <figcaption><b>" + caption + "</b><br>\n"
            "    <code>output/" + path.name + "</code> · "
            + f"{path.stat().st_size / 1024:.1f}" + " KB\n"
            "  </figcaption>\n"
            "</figure>"
        )
    html = (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n<head>\n'
        '<meta charset="utf-8">\n'
        "<title>科赫雪花 0~4 阶 · 作业成果</title>\n"
        "<style>\n"
        'body { margin: 0; padding: 32px; background: #f6f7f9; color: #24292f;\n'
        '       font-family: "Microsoft YaHei", system-ui, sans-serif; }\n'
        "h1 { font-size: 24px; margin: 0 0 6px; }\n"
        "p.note { color: #57606a; margin: 0 0 24px; line-height: 1.7; }\n"
        ".grid { display: grid; gap: 20px;\n"
        "        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }\n"
        "figure { margin: 0; padding: 14px; background: #fff;\n"
        "         border: 1px solid #d0d7de; border-radius: 8px; }\n"
        "figure img { width: 100%; height: auto; display: block;\n"
        "             image-rendering: pixelated; }\n"
        "figcaption { margin-top: 10px; font-size: 14px; line-height: 1.6; }\n"
        "code { color: #0969da; }\n"
        "</style>\n</head>\n<body>\n"
        "<h1>科赫雪花 · 0~4 阶作业成果</h1>\n"
        '<p class="note">用递归把每条线段三等分并向外鼓出等边三角形，'
        "阶数每加 1，线段数乘 4、周长乘 4/3。<br>"
        "图片全部由本项目用标准库逐字节编码生成，未使用 turtle / numpy / "
        "matplotlib / Pillow；结果完全确定、可复现。图片已内嵌，此文件可单独发送。</p>\n"
        '<div class="grid">\n' + "\n".join(cards) + "\n</div>\n"
        "</body>\n</html>\n"
    )
    target = OUT / "index.html"
    target.write_text(html, encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="按阶数生成科赫雪花 PNG（默认 0~4 阶全部生成）"
    )
    parser.add_argument(
        "orders", nargs="*", type=int,
        help=f"要生成的阶数（{MIN_ORDER}~{MAX_ORDER}），不写则生成全部 5 阶",
    )
    parser.add_argument(
        "--show", action="store_true",
        help="生成后用浏览器自动打开 output/index.html 看图",
    )
    args = parser.parse_args(argv)
    orders = sorted(set(args.orders)) if args.orders else list(
        range(MIN_ORDER, MAX_ORDER + 1)
    )
    try:
        for order in orders:
            check_order(order)
    except ValueError as exc:
        parser.error(str(exc))

    files = [draw_one(order) for order in orders]

    print(f"科赫雪花 · 阶数 {orders}（初始边长 2.0，等边三角形）")
    print("-" * 78)
    print(f"{'order':>5} {'segments':>9} {'vertices':>9} "
          f"{'perimeter':>11} {'area ratio':>11}  file")
    for order in orders:
        print(f"{order:>5} {segment_count(order):>9} "
              f"{len(snowflake(order)):>9} "
              f"{perimeter_ratio(order):>11.4f} "
              f"{area_ratio(order):>11.4f}  output/koch_{order}.png")
    print("-" * 78)
    for path in files:
        print(f"wrote {path.relative_to(ROOT)}  "
              f"({path.stat().st_size / 1024:.1f} KB)")

    gallery = write_gallery(sorted(OUT.glob("koch_*.png")))
    print(f"wrote {gallery.relative_to(ROOT)}  (图片画廊，双击即可看到全部雪花)")
    print(">>> 图片在哪看：控制台是纯文本，不会显示图片本身；")
    print("    PyCharm 左侧项目树展开 koch-snowflake/output/，双击 .png 即可预览，")
    print("    或双击 output/index.html 一次看齐 5 张图。")

    if args.show:
        try:
            opened = webbrowser.open(gallery.as_uri())
        except Exception as exc:                 # 无图形环境时不让作业报错
            opened, message = False, str(exc)
        else:
            message = ""
        if opened:
            print("已在浏览器打开图片画廊；若窗口没弹出，请手动双击 output/index.html。")
        else:
            print("浏览器未能自动打开" + (f"（{message}）" if message else "")
                  + "，请手动双击 output/index.html。")

    print("done. run `python selftest.py` to verify.")


if __name__ == "__main__":
    main()
