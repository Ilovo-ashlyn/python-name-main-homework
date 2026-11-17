"""自检：递归几何性质 + PNG 文件结构 + 图片画廊。

运行：python selftest.py（请先跑一次 python draw_all.py）
"""

from __future__ import annotations

import math
import struct
from pathlib import Path

from draw_all import H, OUT, W
from koch_snowflake import (MIN_ORDER, MAX_ORDER, area_ratio, check_order,
                            koch_segment, perimeter_ratio, polygon_area,
                            segment_count, snowflake)


def check_png(path: Path) -> None:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name}: PNG 签名错误"
    assert data[12:16] == b"IHDR", f"{path.name}: 缺少 IHDR"
    width, height = struct.unpack(">II", data[16:24])
    assert (width, height) == (W, H), f"{path.name}: 尺寸错误 {width}x{height}"
    assert data[-8:-4] == b"IEND", f"{path.name}: 缺少 IEND"
    assert len(data) > 1000, f"{path.name}: 文件异常小"
    print(f"  PNG ok  {path.name:<14} {width}x{height}  "
          f"{len(data) / 1024:.1f} KB")


def main() -> None:
    print("1. 递归几何：点数、闭合、等长线段、面积公式")
    base_area = polygon_area(snowflake(0))
    for order in range(MIN_ORDER, MAX_ORDER + 1):
        points = snowflake(order)
        assert len(points) == segment_count(order) + 1, order
        assert points[0] == points[-1], f"{order} 阶曲线没有闭合"

        lengths = [math.dist(points[i], points[i + 1])
                   for i in range(len(points) - 1)]
        expected = 2.0 / 3 ** order
        assert max(lengths) - min(lengths) < 1e-9, f"{order} 阶线段不等长"
        assert abs(max(lengths) - expected) < 1e-9, f"{order} 阶线段长度错误"

        measured = polygon_area(points) / base_area
        assert abs(measured - area_ratio(order)) < 1e-9, \
            f"{order} 阶面积 {measured} != 理论 {area_ratio(order)}"
        print(f"  order {order}: {segment_count(order):>3} 段, "
              f"周长 x{perimeter_ratio(order):.4f}, 面积 x{measured:.4f}")

    print("2. 一阶曲线的峰点（对应教材 turtle.left(60)）")
    segment = koch_segment((0.0, 0.0), (3.0, 0.0), 1)
    assert len(segment) == 5
    peak = segment[2]
    assert abs(peak[0] - 1.5) < 1e-9
    assert abs(peak[1] - math.sqrt(3) / 2) < 1e-9
    assert segment[1] == (1.0, 0.0) and segment[3] == (2.0, 0.0)
    print(f"  peak ok   (0,0)->(3,0) 变成 "
          f"(0,0) (1,0) (1.5,{math.sqrt(3)/2:.4f}) (2,0) (3,0)")

    print("3. 阶数校验：只接受 0~4 的整数")
    for bad in (-1, 5, 2.5, "3", True, None):
        try:
            check_order(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"非法阶数没有报错: {bad!r}")
    print("  order validation ok")

    print("4. 五张图片都必须是结构合法的 PNG")
    files = sorted(OUT.glob("koch_*.png"))
    assert len(files) == 5, f"期望 5 张 PNG，实际 {len(files)} 张"
    for path in files:
        check_png(path)

    print("5. 自包含图片画廊")
    gallery = OUT / "index.html"
    assert gallery.is_file(), "缺少 output/index.html"
    html = gallery.read_text(encoding="utf-8")
    assert html.count("data:image/png;base64,") == 5, "画廊内嵌图片数量不为 5"
    print(f"  gallery ok  output/index.html  5 embedded images  "
          f"{len(html.encode('utf-8')) / 1024:.1f} KB")

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
