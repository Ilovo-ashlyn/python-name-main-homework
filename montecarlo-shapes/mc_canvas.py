"""点阵画布 + 手写 PNG 编码器（零第三方依赖）。

不调用 numpy / matplotlib / Pillow：
像素直接存在 bytearray 里，再按 PNG 规范自己拼
IHDR / IDAT / IEND 数据块，用 zlib 压缩扫描线、用 crc32 校验。
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

Color = tuple[int, int, int]

# 配色：浅底 + 深色点，方便截图交作业
BG = (250, 250, 248)          # 背景
MISS = (226, 231, 237)        # 落在图形外的采样点
HIT = (32, 92, 168)           # 落在图形内的采样点（蓝）
INK = (38, 44, 54)            # 轮廓、坐标轴、文字
ACCENT = (196, 62, 78)        # 心形（红）
GREEN = (28, 122, 92)         # 分形（绿）
THEORY = (214, 138, 40)       # 理论参考线（橙）
GRID = (228, 231, 235)        # 网格线

# 5x7 点阵字体：自己把字也"点"出来，避免依赖任何字体文件
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
        """画一个 size x size 的方点（蒙特卡罗的"投点"）。"""
        for dy in range(size):
            for dx in range(size):
                self.set_pixel(x + dx, y + dy, color)

    def line(self, x0: int, y0: int, x1: int, y1: int,
             color: Color, size: int = 1) -> None:
        """Bresenham 直线，用来描轮廓和坐标轴。"""
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
             color: Color = INK, scale: int = 1) -> None:
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
