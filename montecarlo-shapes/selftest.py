"""自检：验证估算精度与自写 PNG 的文件结构。

运行：python selftest.py（请先跑一次 python draw_all.py）
"""

from __future__ import annotations

import math
import random
import struct
from pathlib import Path

from draw_all import ROOT, OUT, SEED, heart, quarter_circle
from montecarlo import (area_experiment, convergence_pi, estimate_pi,
                        grid_reference, integral_experiment, sierpinski)


def check_png(path: Path) -> None:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name}: PNG 签名错误"
    assert data[12:16] == b"IHDR", f"{path.name}: 缺少 IHDR"
    width, height = struct.unpack(">II", data[16:24])
    assert (width, height) == (520, 520), f"{path.name}: 尺寸错误 {width}x{height}"
    assert data[-8:-4] == b"IEND", f"{path.name}: 缺少 IEND"
    assert len(data) > 1000, f"{path.name}: 文件异常小"
    print(f"  PNG ok  {path.name:<22} {width}x{height}  "
          f"{len(data) / 1024:.1f} KB")


def main() -> None:
    # 1. π：2 万点的标准误约 0.008，给 0.05 的宽松阈值
    pi_est = estimate_pi(random.Random(SEED), 20000)
    assert pi_est.error is not None and pi_est.error < 0.05, pi_est.row()
    print(f"  pi ok   {pi_est.row()}")

    # 2. 心形面积：与确定性细网格参照相差 < 3%
    box = (-1.3, 1.3, -1.3, 1.3)
    reference = grid_reference(heart, box, steps=400)
    heart_est, _ = area_experiment(random.Random(SEED + 1), 60000,
                                   heart, box, "heart area", reference)
    relative = abs(heart_est.value - reference) / reference
    assert relative < 0.03, f"heart relative error {relative:.4f}"
    print(f"  heart ok   {heart_est.row()}  rel={relative:.4%}")

    # 3. 积分：真值 π/4
    integral_est, _ = integral_experiment(
        random.Random(SEED + 2), 40000, quarter_circle,
        0.0, 1.0, 1.0, math.pi / 4,
    )
    assert integral_est.error is not None and integral_est.error < 0.02, \
        integral_est.row()
    print(f"  integral ok   {integral_est.row()}")

    # 4. 收敛曲线：误差非负且样本量递增
    curve = convergence_pi(SEED, [100, 1000, 10000, 100000])
    assert len(curve) == 4 and all(e >= 0 for _, e in curve)
    print(f"  convergence ok   {[(n, round(e, 5)) for n, e in curve]}")

    # 5. 混沌游戏：点数正确且都落在外三角形所在的单位框内
    points = list(sierpinski(random.Random(SEED + 3), 1000))
    assert len(points) == 1000
    assert all(0.0 <= x <= 1.0 and 0.0 <= y <= 1.0 for x, y in points)
    print("  sierpinski ok   1000 points inside unit box")

    # 6. 五张图都必须是结构合法的 PNG
    files = sorted(OUT.glob("*.png"))
    assert len(files) == 5, f"期望 5 张 PNG，实际 {len(files)} 张"
    for path in files:
        check_png(path)

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
