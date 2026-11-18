"""作业 2：蒙特卡罗方法手搓图形 —— 投点估 π、心形面积、定积分，画分形与收敛曲线。

运行：python montecarlo.py   （自动弹出图形窗口，不用去点图片文件）
依赖：pip install numpy matplotlib
"""
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

rng = np.random.default_rng(20261116)   # 固定种子，每次跑结果一样
N = 20000                               # 投点数，调大更准

# ① 在 [0,1]² 正方形投点，落在 1/4 圆内 -> π ≈ 4 × 命中率
darts = rng.random((N, 2))
x, y = darts[:, 0], darts[:, 1]
hit_pi = x**2 + y**2 <= 1
pi_hat = 4 * hit_pi.mean()

# ② 在 [-1.5,1.5]² 投点，落在心形 (x²+y²-1)³ ≤ x²y³ 内 -> 心形面积
heart = rng.uniform(-1.5, 1.5, (N, 2))
hx, hy = heart[:, 0], heart[:, 1]
hit_heart = (hx**2 + hy**2 - 1)**3 <= hx**2 * hy**3
heart_area = 9 * hit_heart.mean()        # 采样框面积 = 3×3 = 9

# ③ 投点算定积分 ∫₀¹ √(1-x²) dx：数落在曲线下方的点
ix, iy = rng.random(N), rng.random(N)
hit_int = iy <= np.sqrt(1 - ix**2)
integral = hit_int.mean()

# ④ 谢尔宾斯基三角形：随机选一个顶点，走到和它的中点，重复
corners = np.array([[0., 0.], [1., 0.], [0.5, 3**0.5 / 2]])
chaos = [np.array([0.1, 0.1])]
for _ in range(20000):
    chaos.append((chaos[-1] + corners[rng.integers(3)]) / 2)
chaos = np.array(chaos)

# ⑤ π 的估计值随投点数增加而变化
curve = 4 * np.cumsum(hit_pi) / np.arange(1, N + 1)

print(f"π ≈ {pi_hat:.5f}   心形面积 ≈ {heart_area:.5f}   定积分 ≈ {integral:.5f}")

# ---------- 画图：一个窗口摆 6 格，运行即弹出 ----------
fig, ax = plt.subplots(2, 3, figsize=(12, 7))
fig.suptitle("蒙特卡罗投点法（种子 20261116，N = 20000）")

ax[0, 0].scatter(x[hit_pi], y[hit_pi], s=1, c="crimson")
ax[0, 0].scatter(x[~hit_pi], y[~hit_pi], s=1, c="lightgray")
ax[0, 0].set_title(f"① 1/4 圆投点 → π ≈ {pi_hat:.4f}")

ax[0, 1].scatter(hx[hit_heart], hy[hit_heart], s=1, c="crimson")
ax[0, 1].scatter(hx[~hit_heart], hy[~hit_heart], s=1, c="lightgray")
ax[0, 1].set_title(f"② 心形面积 ≈ {heart_area:.4f}")

ax[0, 2].scatter(chaos[:, 0], chaos[:, 1], s=0.2, c="#4c78a8")
ax[0, 2].set_title("③ 随机中点 → 谢尔宾斯基")

ax[1, 0].scatter(ix[hit_int], iy[hit_int], s=1, c="crimson")
ax[1, 0].scatter(ix[~hit_int], iy[~hit_int], s=1, c="lightgray")
ax[1, 0].set_title(f"④ 曲线下投点 → 积分 ≈ {integral:.4f}")

ax[1, 1].plot(curve, lw=1, label="估计值")
ax[1, 1].axhline(np.pi, ls="--", c="gray", label="π 真值")
ax[1, 1].set_ylim(2.8, 3.5)
ax[1, 1].legend(fontsize=8)
ax[1, 1].set_title("⑤ 估计值逐渐收敛")

ax[1, 2].axis("off")
ax[1, 2].text(0.05, 0.6, f"π        ≈ {pi_hat:.5f}   真值 3.14159\n"
                          f"心形面积  ≈ {heart_area:.5f}\n"
                          f"定积分    ≈ {integral:.5f}   真值 π/4\n"
                          f"投点数 N  = {N}", fontsize=10)

for a in (ax[0, 0], ax[0, 1], ax[0, 2], ax[1, 0]):
    a.set_aspect("equal")

plt.tight_layout()
plt.show()
