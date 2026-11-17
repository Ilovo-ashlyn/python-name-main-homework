"""科赫雪花的递归算法 + 点阵画布 + 手写 PNG 编码器（零第三方依赖）。

本文件是**被导入的工具模块**：只提供函数与类，不负责生成作业图片。
入口是 draw_all.py。单独运行本文件会打印说明，不会一片空白。
"""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

Color = tuple[int, int, int]
Point = tuple[float, float]

BG = (250, 250, 248)          # 背景
FILL = (214, 230, 246)        # 雪花内部（淡蓝）
INK = (30, 64, 112)           # 雪花轮廓（深蓝）
TEXT = (38, 44, 54)           # 文字
GUIDE = (226, 231, 237)       # 画框

COS60 = 0.5
SIN60 = math.sqrt(3) / 2
MIN_ORDER = 0
MAX_ORDER = 4                 # 题目要求生成 0~4 阶

# 5x7 点阵字模：自己把字也「点」出来，不依赖任何字体文件
_FONT = {
    "0": "01110 10001 10011 10101 11001 10001 01110",
    "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111",
    "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010",
    "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110",
    "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110",
    "9": "01110 10001 10001 01111 00001 00010 01100",
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01111 10000 10000 10000 10000 10000 01111",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01111 10000 10000 10111 10001 10001 01111",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "11111 00100 00100 00100 00100 00100 11111",
    "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001",
    "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 11011 10001",
    "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "Z": "11111 00001 00010 00100 01000 10000 11111",
    ".": "00000 00000 00000 00000 00000 01100 01100",
    "-": "00000 00000 00000 11111 00000 00000 00000",
    "/": "00001 00001 00010 00100 01000 10000 10000",
    "=": "00000 11111 00000 11111 00000 00000 00000",
    "%": "11001 11010 00010 00100 01000 01011 10011",
    ":": "00000 01100 01100 00000 01100 01100 00000",
    " ": "00000 00000 00000 00000 00000 00000 00000",
}


def _chunk(tag: bytes, data: bytes) -> bytes:
    """PNG 数据块 = 4 字节长度 + 4 字节类型 + 数据 + 4 字节 CRC32。"""
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


class Canvas:
    """RGB 点阵画布，坐标原点在左上角。"""

    def __init__(self, width: int, height: int, bg: Color = BG) -> None:
        self.width = width
        self.height = height
        self.pixels = bytearray(bytes(bg) * (width * height))

    def set_pixel(self, x: int, y: int, color: Color) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = (y * self.width + x) * 3
            self.pixels[offset:offset + 3] = bytes(color)

    def dot(self, x: int, y: int, color: Color, size: int = 1) -> None:
        for dy in range(size):
            for dx in range(size):
                self.set_pixel(x + dx, y + dy, color)

    def line(self, x0: int, y0: int, x1: int, y1: int,
             color: Color, size: int = 1) -> None:
        """Bresenham 直线。"""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.dot(x0, y0, color, size)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def frame(self, x0: int, y0: int, x1: int, y1: int,
              color: Color, size: int = 1) -> None:
        self.line(x0, y0, x1, y0, color, size)
        self.line(x1, y0, x1, y1, color, size)
        self.line(x1, y1, x0, y1, color, size)
        self.line(x0, y1, x0, y0, color, size)

    def text(self, x: int, y: int, s: str,
             color: Color = TEXT, scale: int = 1) -> None:
        """5x7 点阵字，支持 A-Z / 0-9 / . - / = % : 空格。"""
        cursor = x
        for ch in s.upper():
            glyph = _FONT.get(ch, _FONT[" "])
            for row_index, row in enumerate(glyph.split()):
                for col_index, bit in enumerate(row):
                    if bit == "1":
                        self.dot(cursor + col_index * scale,
                                 y + row_index * scale, color, scale)
            cursor += 6 * scale

    def fill_polygon(self, points: list[tuple[int, int]], color: Color) -> None:
        """扫描线奇偶填充：科赫雪花边界是简单闭合曲线，可直接填充内部。"""
        edges = []
        for i in range(len(points) - 1):
            x0, y0 = points[i]
            x1, y1 = points[i + 1]
            if y0 != y1:
                edges.append((x0, y0, x1, y1))
        if not edges:
            return
        y_min = max(0, int(min(min(e[1], e[3]) for e in edges)))
        y_max = min(self.height - 1, int(max(max(e[1], e[3]) for e in edges)))
        for y in range(y_min, y_max + 1):
            scan = y + 0.5
            xs = []
            for x0, y0, x1, y1 in edges:
                if min(y0, y1) <= scan < max(y0, y1):
                    xs.append(x0 + (scan - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                left = max(0, round(xs[i]))
                right = min(self.width - 1, round(xs[i + 1]))
                for x in range(left, right + 1):
                    self.set_pixel(x, y, color)

    def save(self, path: str | Path) -> Path:
        """把像素写成真正的 PNG 文件（RGB 8bit / filter 0 / zlib）。"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        stride = self.width * 3
        raw = bytearray()
        for y in range(self.height):
            raw.append(0)  # 每行开头 1 字节 filter type：0 = None
            raw.extend(self.pixels[y * stride:(y + 1) * stride])
        data = (
            b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", struct.pack(">IIBBBBB",
                                          self.width, self.height,
                                          8, 2, 0, 0, 0))
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b"")
        )
        path.write_bytes(data)
        return path


class Viewport:
    """数学坐标 -> 像素坐标；数学 y 轴向上，屏幕 y 轴向下，故翻转。"""

    def __init__(self, xmin: float, xmax: float, ymin: float, ymax: float,
                 left: int, top: int, width: int, height: int) -> None:
        self.xmin, self.xmax = xmin, xmax
        self.ymin, self.ymax = ymin, ymax
        self.left, self.top = left, top
        self.width, self.height = width, height

    def to_px(self, x: float, y: float) -> tuple[int, int]:
        px = self.left + round((x - self.xmin) / (self.xmax - self.xmin)
                               * (self.width - 1))
        py = self.top + round((self.ymax - y) / (self.ymax - self.ymin)
                              * (self.height - 1))
        return px, py


def check_order(order: int) -> None:
    """题目要求 0~4 阶；超出范围直接报错，避免生成糊成一片的图。"""
    if (not isinstance(order, int) or isinstance(order, bool)
            or not MIN_ORDER <= order <= MAX_ORDER):
        raise ValueError(
            f"阶数必须是 {MIN_ORDER}~{MAX_ORDER} 的整数，收到 {order!r}"
        )


def rotate_ccw60(v: Point) -> Point:
    """向量逆时针转 60°，对应教材 turtle.left(60)。"""
    x, y = v
    return (x * COS60 - y * SIN60, x * SIN60 + y * COS60)


def koch_segment(p: Point, q: Point, order: int) -> list[Point]:
    """返回 p->q 这条线段的 order 阶科赫曲线点列（含两端点）。

    把线段三等分，中间那段换成一个向外的等边三角形的两条边，
    于是 1 段变成 4 段、总长变成 4/3 倍。
    """
    check_order(order)
    if order == 0:
        return [p, q]
    dx, dy = (q[0] - p[0]) / 3, (q[1] - p[1]) / 3
    a = (p[0] + dx, p[1] + dy)
    b = (p[0] + 2 * dx, p[1] + 2 * dy)
    rx, ry = rotate_ccw60((dx, dy))
    apex = (a[0] + rx, a[1] + ry)
    return (
        koch_segment(p, a, order - 1)[:-1]
        + koch_segment(a, apex, order - 1)[:-1]
        + koch_segment(apex, b, order - 1)[:-1]
        + koch_segment(b, q, order - 1)
    )


def snowflake(order: int, side: float = 2.0) -> list[Point]:
    """闭合的 order 阶科赫雪花点列。

    初始等边三角形按顺时针排列，使每条边的「左转 60°」都朝图形外侧；
    三条边各画一次科赫曲线，首尾相接即成雪花。
    """
    check_order(order)
    radius = side / math.sqrt(3)          # 中心到顶点的距离
    vertices = [
        (radius * math.cos(math.radians(angle)),
         radius * math.sin(math.radians(angle)))
        for angle in (210.0, 90.0, 330.0)
    ]
    points: list[Point] = []
    for i in range(3):
        segment = koch_segment(vertices[i], vertices[(i + 1) % 3], order)
        points.extend(segment[:-1])
    points.append(points[0])              # 闭合
    return points


def segment_count(order: int) -> int:
    """线段条数：3 * 4^n。"""
    check_order(order)
    return 3 * 4 ** order


def perimeter_ratio(order: int) -> float:
    """周长相对 0 阶的倍数：(4/3)^n —— 阶数越大周长越发散。"""
    check_order(order)
    return (4 / 3) ** order


def area_ratio(order: int) -> float:
    """面积相对初始三角形的倍数：1 + 3/5 * (1 - (4/9)^n)，极限 8/5。"""
    check_order(order)
    return 1 + 3 / 5 * (1 - (4 / 9) ** order)


def polygon_area(points: list[Point]) -> float:
    """鞋带公式算多边形面积，用来和 area_ratio 的理论值对照。"""
    total = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        total += x0 * y1 - x1 * y0
    return abs(total) / 2


if __name__ == "__main__":
    # 工具模块单独运行时给一句明确说明，避免控制台一片空白。
    print("koch_snowflake.py 是工具模块（递归算法 + 画布 + 手写 PNG 编码器）。")
    print(f"演示：3 阶雪花有 {segment_count(3)} 条线段、"
          f"周长是 0 阶的 {perimeter_ratio(3):.3f} 倍。")
    print("可用函数：snowflake / koch_segment / polygon_area / segment_count ...")
    print("要生成 0~4 阶作业图片，请运行：python draw_all.py")
