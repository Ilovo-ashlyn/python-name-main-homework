"""蒙特卡罗采样核心：只用标准库 random / math。

思想：想要某个量（面积、积分、π），就把它写成"随机点落入某区域的概率"，
再用频率去近似概率。大数定律保证 N 越大越准，误差量级约 1/sqrt(N)。
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, Iterator


@dataclass
class Estimate:
    """一次估算的结果。"""
    name: str
    hits: int
    total: int
    value: float
    reference: float | None = None

    @property
    def hit_ratio(self) -> float:
        return self.hits / self.total

    @property
    def error(self) -> float | None:
        if self.reference is None:
            return None
        return abs(self.value - self.reference)

    def row(self) -> str:
        ref = "n/a" if self.reference is None else f"{self.reference:.5f}"
        err = "n/a" if self.error is None else f"{self.error:.5f}"
        return (f"{self.name:<18} hits={self.hits:>7}/{self.total:<7} "
                f"ratio={self.hit_ratio:.5f}  value={self.value:.5f}  "
                f"ref={ref:>8}  err={err}")


def estimate_pi(rng: random.Random, n: int) -> Estimate:
    """单位正方形里的四分之一圆：命中率 ≈ π/4。"""
    hits = 0
    for _ in range(n):
        x, y = rng.random(), rng.random()
        if x * x + y * y <= 1.0:
            hits += 1
    return Estimate("pi by darts", hits, n, 4.0 * hits / n, math.pi)


def area_experiment(
    rng: random.Random,
    n: int,
    predicate: Callable[[float, float], bool],
    box: tuple[float, float, float, float],
    name: str = "area",
    reference: float | None = None,
) -> tuple[Estimate, list[tuple[float, float, bool]]]:
    """在矩形 box 内投 n 个点，估算满足 predicate 的区域面积。

    面积 ≈ 矩形面积 × 命中率。返回采样点是为了画图（不是估算必需的）。
    """
    xmin, xmax, ymin, ymax = box
    points: list[tuple[float, float, bool]] = []
    hits = 0
    for _ in range(n):
        x = rng.uniform(xmin, xmax)
        y = rng.uniform(ymin, ymax)
        inside = predicate(x, y)
        if inside:
            hits += 1
        points.append((x, y, inside))
    value = (xmax - xmin) * (ymax - ymin) * hits / n
    return Estimate(name, hits, n, value, reference), points


def integral_experiment(
    rng: random.Random,
    n: int,
    f: Callable[[float], float],
    a: float,
    b: float,
    ymax: float,
    reference: float | None = None,
) -> tuple[Estimate, list[tuple[float, float, bool]]]:
    """用投点估算 ∫[a,b] f(x) dx：点落在曲线下方的比例 × 矩形面积。"""
    points: list[tuple[float, float, bool]] = []
    hits = 0
    for _ in range(n):
        x = rng.uniform(a, b)
        y = rng.uniform(0.0, ymax)
        inside = y <= f(x)
        if inside:
            hits += 1
        points.append((x, y, inside))
    value = (b - a) * ymax * hits / n
    return Estimate("integral", hits, n, value, reference), points


def grid_reference(
    predicate: Callable[[float, float], bool],
    box: tuple[float, float, float, float],
    steps: int = 600,
) -> float:
    """确定性细网格求面积，给蒙特卡罗结果一个独立的参照值。"""
    xmin, xmax, ymin, ymax = box
    dx = (xmax - xmin) / steps
    dy = (ymax - ymin) / steps
    hits = 0
    for i in range(steps):
        x = xmin + (i + 0.5) * dx
        for j in range(steps):
            y = ymin + (j + 0.5) * dy
            if predicate(x, y):
                hits += 1
    return (xmax - xmin) * (ymax - ymin) * hits / (steps * steps)


def convergence_pi(seed: int, sizes: list[int]) -> list[tuple[int, float]]:
    """同一串随机点，记录不同样本量下的 |π_hat - π|，用于画收敛曲线。"""
    rng = random.Random(seed)
    sizes = sorted(sizes)
    result: list[tuple[int, float]] = []
    hits = 0
    index = 0
    for n in range(1, sizes[-1] + 1):
        x, y = rng.random(), rng.random()
        if x * x + y * y <= 1.0:
            hits += 1
        if index < len(sizes) and n == sizes[index]:
            result.append((n, abs(4.0 * hits / n - math.pi)))
            index += 1
    return result


def sierpinski(rng: random.Random, n: int,
               skip: int = 20) -> Iterator[tuple[float, float]]:
    """混沌游戏：每步随机选一个顶点，走到与它连线的中点。

    这是随机迭代（不是投点），但同样属于蒙特卡罗式的随机采样，
    点集几乎必然收敛到 Sierpinski 三角形。
    """
    vertices = ((0.0, 0.0), (1.0, 0.0), (0.5, math.sqrt(3) / 2))
    x, y = 0.5, 0.25
    for i in range(n + skip):
        vx, vy = rng.choice(vertices)
        x, y = (x + vx) / 2, (y + vy) / 2
        if i >= skip:
            yield x, y


if __name__ == "__main__":
    # 这是「工具模块」：被 draw_all.py / selftest.py 导入使用。
    # 单独运行时做一个最小演示，顺便说明该运行哪个文件。
    demo = estimate_pi(random.Random(20261116), 20000)
    print("montecarlo.py 是工具模块（随机采样与估算算法），不会自己输出作业结果。")
    print(f"演示：{demo.row()}")
    print("可用函数：estimate_pi / area_experiment / integral_experiment / "
          "grid_reference / convergence_pi / sierpinski")
    print("完整 5 个实验请运行：python draw_all.py；校验请运行：python selftest.py")
