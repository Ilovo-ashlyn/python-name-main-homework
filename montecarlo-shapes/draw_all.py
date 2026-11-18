"""运行入口：跑完 5 个实验后自动弹出浏览器，直接把图案显示出来。

运行：python draw_all.py            # 生成 5 张 PNG，并自动弹出浏览器直接显示图案
      python draw_all.py --no-show  # 只生成文件、不自动显示（无图形界面时用）
输出：output/*.png —— 全部由本项目自己编码，可直接打开或交作业。
      output/index.html —— 把 5 张图内嵌在一起的画廊，运行时自动打开。

注意：控制台是纯文本终端，不会把图片画在文字窗口里；图案由运行时自动弹出的
      浏览器画廊显示，不需要手动去点图片文件。
"""

from __future__ import annotations

import argparse
import base64
import math
import random
import webbrowser
from pathlib import Path

from mc_canvas import (ACCENT, GREEN, GRID, HIT, INK, MISS, THEORY,
                       Canvas, Viewport)
from montecarlo import (Estimate, area_experiment, convergence_pi,
                        grid_reference, integral_experiment, sierpinski)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
SEED = 20261116               # 固定种子：结果每次运行都一样，方便复现
W = H = 520
PLOT = (30, 56, 460, 460)     # 绘图区 left, top, width, height


def heart(x: float, y: float) -> bool:
    """心形隐函数 (x²+y²-1)³ - x²y³ <= 0。"""
    return (x * x + y * y - 1) ** 3 - x * x * y ** 3 <= 0


def quarter_circle(x: float) -> float:
    """y = sqrt(1-x²)，[0,1] 上的四分之一圆，积分真值 π/4。"""
    return math.sqrt(max(0.0, 1.0 - x * x))


def title(c: Canvas, line1: str, line2: str) -> None:
    c.text(20, 12, line1, INK, 2)
    c.text(20, 36, line2, INK, 1)


def plot_frame(c: Canvas) -> None:
    left, top, width, height = PLOT
    c.frame(left, top, left + width - 1, top + height - 1, INK)


def draw_pi(rng: random.Random) -> tuple[Estimate, Path]:
    """实验 1：正方形内投点，命中圆的比例估 π。"""
    n = 20000
    est, points = area_experiment(
        rng, n, lambda x, y: x * x + y * y <= 1.0,
        (-1.0, 1.0, -1.0, 1.0), "pi by darts", math.pi,
    )
    c = Canvas(W, H)
    vp = Viewport(-1.05, 1.05, -1.05, 1.05, *PLOT)
    for x, y, inside in points:
        px, py = vp.to_px(x, y)
        c.dot(px, py, HIT if inside else MISS, 2 if inside else 1)

    # 自己描圆：参数方程采样 720 段，用直线连起来
    previous = None
    for k in range(721):
        angle = 2 * math.pi * k / 720
        point = vp.to_px(math.cos(angle), math.sin(angle))
        if previous is not None:
            c.line(previous[0], previous[1], point[0], point[1], INK)
        previous = point

    a, b = vp.to_px(-1.0, 1.0), vp.to_px(1.0, -1.0)
    c.frame(a[0], a[1], b[0], b[1], INK)
    title(c, "1 MONTE CARLO PI",
          f"N={n}  PI={est.value:.5f}  ERR={est.error:.5f}")
    return est, c.save(OUT / "01_pi_darts.png")


def draw_heart(rng: random.Random) -> tuple[Estimate, Path]:
    """实验 2：随机点填充隐函数曲线围成的心形，并估算面积。"""
    n = 60000
    box = (-1.3, 1.3, -1.3, 1.3)
    reference = grid_reference(heart, box, steps=600)
    est, points = area_experiment(rng, n, heart, box,
                                  "heart area", reference)
    c = Canvas(W, H)
    vp = Viewport(*box, *PLOT)
    for x, y, inside in points:
        px, py = vp.to_px(x, y)
        c.dot(px, py, ACCENT if inside else MISS, 2 if inside else 1)
    plot_frame(c)
    title(c, "2 HEART BY RANDOM DOTS",
          f"N={n}  AREA={est.value:.4f}  REF={reference:.4f}")
    return est, c.save(OUT / "02_heart.png")


def draw_sierpinski(rng: random.Random) -> Path:
    """实验 3：混沌游戏，随机迭代画 Sierpinski 三角形。"""
    n = 60000
    c = Canvas(W, H)
    vp = Viewport(-0.02, 1.02, -0.02, 1.02, *PLOT)
    for x, y in sierpinski(rng, n):
        px, py = vp.to_px(x, y)
        c.dot(px, py, GREEN, 1)

    vertices = ((0.0, 0.0), (1.0, 0.0), (0.5, math.sqrt(3) / 2))
    for i in range(3):
        a = vp.to_px(*vertices[i])
        b = vp.to_px(*vertices[(i + 1) % 3])
        c.line(a[0], a[1], b[0], b[1], INK)
    title(c, "3 SIERPINSKI CHAOS GAME",
          f"N={n}  MOVE HALF WAY TO A RANDOM VERTEX")
    return c.save(OUT / "03_sierpinski.png")


def draw_integral(rng: random.Random) -> tuple[Estimate, Path]:
    """实验 4：投点估算四分之一圆面积，也就是定积分 ∫₀¹ sqrt(1-x²) dx。"""
    n = 40000
    est, points = integral_experiment(
        rng, n, quarter_circle, 0.0, 1.0, 1.0, math.pi / 4,
    )
    c = Canvas(W, H)
    vp = Viewport(-0.02, 1.02, -0.02, 1.02, *PLOT)
    for x, y, inside in points:
        px, py = vp.to_px(x, y)
        c.dot(px, py, HIT if inside else MISS, 2 if inside else 1)

    previous = None
    for k in range(461):
        x = k / 460
        point = vp.to_px(x, quarter_circle(x))
        if previous is not None:
            c.line(previous[0], previous[1], point[0], point[1], INK, 2)
        previous = point

    a, b = vp.to_px(0.0, 1.0), vp.to_px(1.0, 0.0)
    c.frame(a[0], a[1], b[0], b[1], INK)
    title(c, "4 MONTE CARLO INTEGRAL",
          f"N={n}  INT={est.value:.5f}  PI/4={math.pi / 4:.5f}")
    return est, c.save(OUT / "04_integral.png")


def draw_convergence(seed: int) -> Path:
    """实验 5：误差随样本量下降，对照 1/sqrt(N) 理论量级。"""
    sizes = [100, 300, 1000, 3000, 10000, 30000, 100000, 200000]
    data = convergence_pi(seed, sizes)
    c = Canvas(W, H)
    left, top, pw, ph = 60, 80, 420, 380
    ymax = max(0.02, max(error for _, error in data) * 1.15)
    xmin, xmax = 2.0, math.log10(sizes[-1])

    def xy(n: float, error: float) -> tuple[int, int]:
        px = left + round((math.log10(n) - xmin) / (xmax - xmin) * (pw - 1))
        py = top + round((ymax - error) / ymax * (ph - 1))
        return px, py

    for k in range(2, 6):
        if k > xmax:
            break
        px = left + round((k - xmin) / (xmax - xmin) * (pw - 1))
        c.line(px, top, px, top + ph - 1, GRID)
        c.text(px - 10, top + ph + 8, str(10 ** k), INK, 1)
    for i in range(5):
        error = ymax * i / 4
        py = top + round((ymax - error) / ymax * (ph - 1))
        c.line(left, py, left + pw - 1, py, GRID)
        c.text(8, py - 3, f"{error:.3f}", INK, 1)
    c.line(left, top, left, top + ph - 1, INK)
    c.line(left, top + ph - 1, left + pw - 1, top + ph - 1, INK)

    # 理论参考：误差 ~ c/sqrt(N)，取 c 让曲线从第一个实测点出发
    scale = data[0][1] * math.sqrt(data[0][0])
    previous = None
    for k in range(121):
        n = 10 ** (xmin + (xmax - xmin) * k / 120)
        error = min(ymax, scale / math.sqrt(n))
        point = xy(n, error)
        if previous is not None:
            c.line(previous[0], previous[1], point[0], point[1], THEORY)
        previous = point

    previous = None
    for n, error in data:
        point = xy(n, error)
        c.dot(point[0] - 1, point[1] - 1, HIT, 3)
        if previous is not None:
            c.line(previous[0], previous[1], point[0], point[1], HIT, 2)
        previous = point

    c.text(20, 12, "5 ERROR VS SAMPLE SIZE", INK, 2)
    c.text(20, 36, "BLUE: ABS ERROR   ORANGE: 1/SQRT(N)", INK, 1)
    c.text(20, 52, "X: N ON LOG SCALE   Y: ABSOLUTE ERROR", INK, 1)
    c.text(60, top + ph + 28, "N (LOG SCALE)", INK, 1)
    return c.save(OUT / "05_convergence.png")


CAPTIONS = {
    "01_pi_darts.png": "实验 1 · 投点估算 π（蓝色点落在单位圆内）",
    "02_heart.png": "实验 2 · 随机点填出心形（红色点为命中）",
    "03_sierpinski.png": "实验 3 · 混沌游戏画出 Sierpinski 三角形",
    "04_integral.png": "实验 4 · 投点算定积分 ∫₀¹√(1-x²)dx",
    "05_convergence.png": "实验 5 · 误差随样本量 N 收敛，对照 1/√N",
}


def write_gallery(files: list[Path]) -> Path:
    """把 5 张 PNG 内嵌成一个 HTML 画廊，双击该文件即可看图。

    只用标准库 base64：图片以 data URI 内嵌，因此这个文件可以单独发给
    别人，不依赖同目录下的 PNG，也不依赖任何网络或第三方库。
    """
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
        "<title>蒙特卡罗方法手搓图形 · 作业成果</title>\n"
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
        "<h1>蒙特卡罗方法手搓图形 · 作业成果</h1>\n"
        '<p class="note">5 张 520×520 PNG 全部由本项目用标准库逐字节编码生成，'
        "未使用 numpy / matplotlib / Pillow。<br>"
        "随机种子固定为 20261116，每次运行结果完全一致。"
        "图片已内嵌在本页面里，此文件可单独发送。</p>\n"
        '<div class="grid">\n' + "\n".join(cards) + "\n</div>\n"
        "</body>\n</html>\n"
    )
    target = OUT / "index.html"
    target.write_text(html, encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="生成蒙特卡罗手搓图形（5 张 PNG + 可双击查看的图片画廊）"
    )
    parser.add_argument(
        "--show", action="store_true",
        help="兼容旧命令：现在默认就会自动显示图案，此参数可省略",
    )
    parser.add_argument(
        "--no-show", action="store_true",
        help="只生成图片文件、不自动弹出显示（无图形界面时使用）",
    )
    args = parser.parse_args(argv)

    rng = random.Random(SEED)
    estimates: list[Estimate] = []
    files: list[Path] = []

    est, path = draw_pi(rng)
    estimates.append(est)
    files.append(path)

    est, path = draw_heart(rng)
    estimates.append(est)
    files.append(path)

    files.append(draw_sierpinski(rng))

    est, path = draw_integral(rng)
    estimates.append(est)
    files.append(path)

    files.append(draw_convergence(SEED))

    print(f"seed = {SEED} (fixed, reproducible)")
    print("-" * 100)
    print(f"{'experiment':<18} {'hits':>8} {'total':>8} {'ratio':>8} "
          f"{'estimate':>10} {'reference':>10} {'error':>10}")
    for est in estimates:
        ref = "n/a" if est.reference is None else f"{est.reference:.5f}"
        err = "n/a" if est.error is None else f"{est.error:.5f}"
        print(f"{est.name:<18} {est.hits:>8} {est.total:>8} "
              f"{est.hit_ratio:>8.5f} {est.value:>10.5f} "
              f"{ref:>10} {err:>10}")
    print("-" * 100)
    for path in files:
        print(f"wrote {path.relative_to(ROOT)}  "
              f"({path.stat().st_size / 1024:.1f} KB)")

    gallery = write_gallery(files)
    print(f"wrote {gallery.relative_to(ROOT)}  (图片画廊，运行时自动打开)")

    if not args.no_show:
        try:
            opened = webbrowser.open(gallery.as_uri())
        except Exception as exc:                 # 无图形环境下不让作业报错
            opened, message = False, str(exc)
        else:
            message = ""
        if opened:
            print(">>> 图案已自动弹出：浏览器里一次显示 5 张图，不需要手动去点图片文件。")
        else:
            print(">>> 自动显示失败" + (f"（{message}）" if message else "")
                  + "，图片仍已生成在 output/ 下。")
    else:
        print(">>> 已跳过自动显示（--no-show）；图片保存在 output/ 下。")

    print("done. run `python selftest.py` to verify.")


if __name__ == "__main__":
    main()
