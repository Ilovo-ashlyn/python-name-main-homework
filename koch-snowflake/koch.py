"""作业 4：科赫雪花 0~4 阶。

运行：python koch.py   （自动弹出窗口，一次看齐 5 个阶数）
依赖：pip install matplotlib
"""
from math import sqrt
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]


def koch(a, b, n):
    """返回从复数点 a 到 b 的 n 阶科赫折线的点列。

    把线段三等分，中间一段向外凸起 60° 尖角，再对 4 小段递归。
    """
    if n == 0:
        return [a, b]
    d = (b - a) / 3
    p, q = a + d, a + 2 * d
    tip = p + d * complex(0.5, -sqrt(3) / 2)   # 旋转 -60°，尖角朝外
    return (koch(a, p, n - 1)[:-1] + koch(p, tip, n - 1)[:-1]
            + koch(tip, q, n - 1)[:-1] + koch(q, b, n - 1))


# 初始等边三角形（逆时针排列，保证尖角朝外）
V = [1 + 0j, complex(-0.5, sqrt(3) / 2), complex(-0.5, -sqrt(3) / 2)]

fig, ax = plt.subplots(2, 3, figsize=(10, 7))
for n, a in zip(range(5), ax.flat):
    pts = []
    for i in range(3):
        pts += koch(V[i], V[(i + 1) % 3], n)[:-1]
    pts.append(pts[0])                       # 首尾相接
    a.plot([z.real for z in pts], [z.imag for z in pts], lw=1, c="#4c78a8")
    a.set_aspect("equal")
    a.axis("off")
    a.set_title(f"{n} 阶：{3 * 4**n} 条边")

ax.flat[5].axis("off")
plt.tight_layout()
plt.show()
