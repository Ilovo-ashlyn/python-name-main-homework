"""蒙特卡罗方法 —— numpy + matplotlib 对照版（可选，需要第三方库）。

这是一个**独立的可运行入口**，把 `draw_all.py` 的 5 个实验用 numpy 向量化
重写、用 matplotlib 出图，用来对照「手搓」与「用库」两种写法：

    python montecarlo_numpy.py           # 生成 5 张图 + 画廊，打印统计表
    python montecarlo_numpy.py --show    # 生成后自动用浏览器打开画廊

依赖（仅本文件需要，主程序 draw_all.py 与其余作业仍是零依赖）：

    pip install -r requirements.txt

图片输出到 output/numpy/，不覆盖手搓版的 output/*.png。
控制台是纯文本终端，不会显示图片本身；看图请双击 output/numpy/index.html。
"""

from __future__ import annotations

import argparse
import base64
import math
import webbrowser
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")                     # 无图形界面 / PyCharm 后台也能保存图片
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "numpy"
SEED = 20261116                           # 固定种子：结果每次运行都一样

HIT = "#1f6feb"        # 命中点：蓝
MISS = "#d8dee6"       # 未命中：浅灰
ACCENT = "#d1242f"     # 心形：红
GREEN = "#1a7f37"      # 分形：绿
INK = "#24292f"        # 线条 / 文字
THEORY = "#e36209"     # 理论参考线：橙

CAPTIONS = {
    "01_pi_darts.png": "实验 1 · numpy 向量化投点估算 π",
    "02_heart.png": "实验 2 · numpy 判断心形隐函数并估算面积",
    "03_sierpinski.png": "实验 3 · 混沌游戏画 Sierpinski 三角形",
    "04_integral.png": "实验 4 · 投点算定积分 ∫₀¹√(1-x²)dx",
    "05_convergence.png": "实验 5 · 误差随样本量收敛，对照 1/√N",
}


@dataclass
class Est:
    """一行统计结果，和手搓版 draw_all.py 的表格保持一致的口径。"""
    name: str
    hits: int
    total: int
    value: float
    reference: float | None
    error: float | None


def new_figure(title: str, subtitle: str) -> tuple:
    """统一建立 520×520 的画布。标题用英文，避免 matplotlib 缺中文字体变方块。"""
    fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=100, facecolor="white")
    fig.subplots_adjust(left=0.11, right=0.97, top=0.88, bottom=0.10)
    ax.set_facecolor("white")
    ax.set_title(title + "\n" + subtitle, fontsize=11, color=INK, pad=8)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(color="#eaeef2", linewidth=0.6)
    ax.set_axisbelow(True)
    return fig, ax


def save(fig, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=100, facecolor="white")
    plt.close(fig)
    return path


def draw_pi(rng: np.random.Generator) -> tuple[Est, Path]:
    """实验 1：[-1,1]² 里一次生成全部随机点，命中率估 π。"""
    n = 20000
    points = rng.uniform(-1.0, 1.0, size=(n, 2))
    x, y = points[:, 0], points[:, 1]
    inside = x * x + y * y <= 1.0
    estimate = 4.0 * inside.mean()

    fig, ax = new_figure(
        "1 MONTE CARLO PI (NUMPY)",
        f"N={n}  PI={estimate:.5f}  ERR={abs(estimate - math.pi):.5f}",
    )
    ax.scatter(x[~inside], y[~inside], s=2, c=MISS, linewidths=0, label="miss")
    ax.scatter(x[inside], y[inside], s=3, c=HIT, linewidths=0, label="hit")
    ax.add_patch(Circle((0, 0), 1, fill=False, edgecolor=INK, linewidth=1.4))
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    return (Est("pi (numpy)", int(inside.sum()), n, estimate, math.pi,
                abs(estimate - math.pi)), save(fig, "01_pi_darts.png"))


def draw_heart(rng: np.random.Generator) -> tuple[Est, Path]:
    """实验 2：向量化判断隐函数，命中率乘采样框面积得到心形面积。"""
    n = 60000
    side = 2.6
    points = rng.uniform(-1.3, 1.3, size=(n, 2))
    x, y = points[:, 0], points[:, 1]
    inside = (x * x + y * y - 1.0) ** 3 - x * x * y ** 3 <= 0.0
    estimate = side * side * inside.mean()

    # 参考值：600×600 确定性细网格，与手搓版 grid_reference() 一样取格子中心，
    # 这样两版的参考面积完全一致，便于直接对照。
    step = 2.6 / 600
    grid = -1.3 + (np.arange(600) + 0.5) * step
    gx, gy = np.meshgrid(grid, grid)
    mask = (gx * gx + gy * gy - 1.0) ** 3 - gx * gx * gy ** 3 <= 0.0
    reference = side * side * mask.mean()

    fig, ax = new_figure(
        "2 HEART BY RANDOM DOTS (NUMPY)",
        f"N={n}  AREA={estimate:.4f}  REF={reference:.4f}",
    )
    ax.scatter(x[~inside], y[~inside], s=2, c=MISS, linewidths=0)
    ax.scatter(x[inside], y[inside], s=3, c=ACCENT, linewidths=0)
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    return (Est("heart area", int(inside.sum()), n, estimate, reference,
                abs(estimate - reference)), save(fig, "02_heart.png"))


def draw_sierpinski(rng: np.random.Generator) -> Path:
    """实验 3：随机选顶点走一半，用 numpy 数组保存全部迭代点。"""
    n = 60000
    vertices = np.array([[0.0, 0.0], [1.0, 0.0],
                         [0.5, math.sqrt(3) / 2]])
    choices = rng.integers(0, 3, size=n)      # 一次性生成全部随机选择
    points = np.empty((n, 2), dtype=float)
    x, y = 0.5, 0.1
    for i, k in enumerate(choices):
        vx, vy = vertices[k]
        x, y = (x + vx) / 2, (y + vy) / 2
        points[i] = x, y

    fig, ax = new_figure(
        "3 SIERPINSKI CHAOS GAME (NUMPY)",
        f"N={n}  MOVE HALF WAY TO A RANDOM VERTEX",
    )
    ax.scatter(points[:, 0], points[:, 1], s=0.6, c=GREEN, linewidths=0)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    return save(fig, "03_sierpinski.png")


def draw_integral(rng: np.random.Generator) -> tuple[Est, Path]:
    """实验 4：投点估算 ∫₀¹√(1-x²)dx = π/4。"""
    n = 40000
    points = rng.uniform(0.0, 1.0, size=(n, 2))
    x, y = points[:, 0], points[:, 1]
    curve = np.sqrt(np.maximum(0.0, 1.0 - x * x))
    inside = y <= curve
    estimate = inside.mean()

    fig, ax = new_figure(
        "4 MONTE CARLO INTEGRAL (NUMPY)",
        f"N={n}  INT={estimate:.5f}  PI/4={math.pi / 4:.5f}",
    )
    ax.scatter(x[~inside], y[~inside], s=2, c=MISS, linewidths=0)
    ax.scatter(x[inside], y[inside], s=3, c=HIT, linewidths=0)
    xx = np.linspace(0.0, 1.0, 461)
    ax.plot(xx, np.sqrt(np.maximum(0.0, 1.0 - xx * xx)),
            color=INK, linewidth=1.8)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    return (Est("integral", int(inside.sum()), n, estimate, math.pi / 4,
                abs(estimate - math.pi / 4)), save(fig, "04_integral.png"))


def draw_convergence(rng: np.random.Generator) -> Path:
    """实验 5：用累积命中数一次算出所有样本量下的误差，对数坐标对照 1/√N。"""
    sizes = np.array([100, 300, 1000, 3000, 10000, 30000, 100000, 200000])
    points = rng.uniform(-1.0, 1.0, size=(int(sizes[-1]), 2))
    inside = points[:, 0] ** 2 + points[:, 1] ** 2 <= 1.0
    cumulative = np.cumsum(inside)
    estimates = 4.0 * cumulative[sizes - 1] / sizes
    errors = np.abs(estimates - math.pi)

    fig, ax = plt.subplots(figsize=(5.2, 5.2), dpi=100, facecolor="white")
    fig.subplots_adjust(left=0.14, right=0.97, top=0.88, bottom=0.12)
    ax.set_title("5 ERROR VS SAMPLE SIZE (NUMPY)\n"
                 "BLUE: ABS ERROR   ORANGE: 1/SQRT(N)",
                 fontsize=11, color=INK, pad=8)
    ns = np.logspace(2, math.log10(float(sizes[-1])), 200)
    scale = float(errors[0]) * math.sqrt(float(sizes[0]))
    ax.loglog(ns, scale / np.sqrt(ns), linestyle="--",
              color=THEORY, linewidth=1.6, label="theory ~ 1/sqrt(N)")
    ax.loglog(sizes, errors, marker="o", color=HIT,
              linewidth=1.8, label="measured")
    ax.set_xlabel("N (log scale)")
    ax.set_ylabel("absolute error")
    ax.grid(True, which="both", color="#eaeef2", linewidth=0.6)
    ax.legend(fontsize=8, loc="upper right")
    return save(fig, "05_convergence.png")


def write_gallery(files: list[Path]) -> Path:
    """把 5 张 PNG 用 base64 内嵌成自包含 HTML，双击即可看图。"""
    cards = []
    for path in files:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        caption = CAPTIONS.get(path.name, path.name)
        cards.append(
            "<figure>\n"
            '  <img src="data:image/png;base64,' + encoded + '" alt="'
            + path.name + '">\n'
            "  <figcaption><b>" + caption + "</b><br>\n"
            "    <code>output/numpy/" + path.name + "</code> · "
            + f"{path.stat().st_size / 1024:.1f}" + " KB\n"
            "  </figcaption>\n</figure>"
        )
    html = (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<title>蒙特卡罗 · numpy + matplotlib 对照版</title>\n"
        "<style>\n"
        "body { margin:0; padding:32px; background:#f6f7f9; color:#24292f;\n"
        "       font-family:'Microsoft YaHei',system-ui,sans-serif; }\n"
        "h1 { font-size:24px; margin:0 0 6px; }\n"
        "p.note { color:#57606a; margin:0 0 24px; line-height:1.7; }\n"
        ".grid { display:grid; gap:20px;\n"
        "        grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); }\n"
        "figure { margin:0; padding:14px; background:#fff;\n"
        "         border:1px solid #d0d7de; border-radius:8px; }\n"
        "figure img { width:100%; height:auto; display:block; }\n"
        "figcaption { margin-top:10px; font-size:14px; line-height:1.6; }\n"
        "code { color:#0969da; }\n"
        "</style>\n</head>\n<body>\n"
        "<h1>蒙特卡罗 · numpy + matplotlib 对照版</h1>\n"
        "<p class=\"note\">这 5 张图由 <code>montecarlo_numpy.py</code> 用 numpy "
        "向量化采样、matplotlib 绘图生成，与零依赖手搓版的 "
        "<code>output/*.png</code> 相互独立。<br>"
        "随机种子固定为 20261116，每次运行结果完全一致。图片已内嵌，"
        "此文件可单独发送。</p>\n"
        "<div class=\"grid\">\n" + "\n".join(cards) + "\n</div>\n"
        "</body>\n</html>\n"
    )
    target = OUT / "index.html"
    target.write_text(html, encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="蒙特卡罗方法 numpy + matplotlib 对照版（需要 pip install -r requirements.txt）"
    )
    parser.add_argument("--show", action="store_true",
                        help="生成后用浏览器自动打开 output/numpy/index.html 看图")
    args = parser.parse_args(argv)

    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    rows: list[Est] = []
    files: list[Path] = []

    est, path = draw_pi(rng)
    rows.append(est)
    files.append(path)
    est, path = draw_heart(rng)
    rows.append(est)
    files.append(path)
    files.append(draw_sierpinski(rng))
    est, path = draw_integral(rng)
    rows.append(est)
    files.append(path)
    files.append(draw_convergence(rng))

    print(f"numpy {np.__version__} / matplotlib {matplotlib.__version__}")
    print(f"seed = {SEED} (fixed, reproducible)")
    print("-" * 100)
    print(f"{'experiment':<18} {'hits':>8} {'total':>8} {'ratio':>8} "
          f"{'estimate':>10} {'reference':>10} {'error':>10}")
    for est in rows:
        print(f"{est.name:<18} {est.hits:>8} {est.total:>8} "
              f"{est.hits / est.total:>8.5f} {est.value:>10.5f} "
              f"{est.reference:>10.5f} {est.error:>10.5f}")
    print("-" * 100)
    for path in files:
        print(f"wrote {path.relative_to(ROOT)}  "
              f"({path.stat().st_size / 1024:.1f} KB)")

    gallery = write_gallery(files)
    print(f"wrote {gallery.relative_to(ROOT)}  (图片画廊，双击即可看到全部 5 张图)")
    print(">>> 图片在哪看：控制台是纯文本，不会显示图片本身；")
    print("    双击 output/numpy/index.html 一次看齐 5 张图，或展开 output/numpy/ 双击 .png。")

    # 自检：误差在统计合理范围内、5 张图都生成成功
    assert rows[0].error is not None and rows[0].error < 0.05, "π 估算偏离过大"
    assert rows[2].error is not None and rows[2].error < 0.02, "积分估算偏离过大"
    assert rows[1].error is not None and rows[1].error / rows[1].reference < 0.02, "心形面积偏离过大"
    assert len(files) == 5 and all(p.stat().st_size > 1000 for p in files), "图片未生成"
    assert gallery.stat().st_size > 1000, "画廊未生成"
    print("ALL CHECKS PASSED (numpy + matplotlib 版)")

    if args.show:
        try:
            opened = webbrowser.open(gallery.as_uri())
        except Exception as exc:                # 无图形环境下不让作业报错
            opened, message = False, str(exc)
        else:
            message = ""
        if opened:
            print("已在浏览器打开图片画廊；若窗口没弹出，请手动双击 output/numpy/index.html。")
        else:
            print("浏览器未能自动打开" + (f"（{message}）" if message else "")
                  + "，请手动双击 output/numpy/index.html。")

    print("done. 对照零依赖手搓版：python draw_all.py")


if __name__ == "__main__":
    main()
