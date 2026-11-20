"""实验 4：本地文档智能审查与摘要。

在 PyCharm 里右键运行本文件即可：
  遍历 docs/ 下的 .txt / .md -> jieba 精确模式分词 -> 过滤 -> 统计词频
  -> output/ 里生成词云 PNG、关键词报告（TXT + CSV）、Top50 词频 CSV
  -> 弹窗展示词云。
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# ---- 路径与常量：相对本文件定位 ----
ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
OUT = ROOT / "output"
STOPWORDS_FILE = ROOT / "stopwords.txt"
USER_DICT_FILE = ROOT / "user_dict.txt"
FONT = r"C:\Windows\Fonts\msyh.ttc"        # 微软雅黑，保证词云里的中文不是方框
TOP_N = 50                                 # 词云与全库报告取前 50 个词
PER_FILE_N = 10                            # 每篇文档列出前 10 个关键词
ENCODINGS = ("utf-8-sig", "utf-8", "gbk")  # 依次尝试，兼容带 BOM 和 GBK 的旧文档


def read_text(path: Path) -> str | None:
    """按多种编码尝试读文件；都失败就返回 None，不让一个坏文件中断整批处理。"""
    for enc in ENCODINGS:
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, OSError):
            continue
    return None


def load_lines(path: Path) -> list[str]:
    """词表每行一个词；文件不存在或读不了时返回空列表，程序照常往下跑。"""
    if not path.is_file():
        return []
    text = read_text(path)
    if text is None:
        print(f"[警告] 读不了 {path.name}，已跳过")
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]


def cut_words(text: str, stopwords: set[str]) -> list[str]:
    """jieba 精确模式分词，再过滤停用词、单字、纯数字和纯标点。"""
    kept = []
    for word in jieba.lcut(text):
        w = word.strip()
        # len>1 去单字，isdigit 去纯数字，alnum 保证至少含一个汉字/字母/数字
        if (len(w) > 1 and not w.isdigit()
                and any(ch.isalnum() for ch in w) and w not in stopwords):
            kept.append(w)
    return kept


def collect_words(files: list[Path], stopwords: set[str]):
    """逐篇读文档、分词、统计，返回 (全库词列表, 每篇 Top10, 未参与统计的文件)。

    单个文件读取失败只记一笔 (文件名, 原因)，然后继续处理后面的文件。
    """
    all_words: list[str] = []
    per_file: dict[str, list[tuple[str, int]]] = {}
    failed: list[tuple[str, str]] = []
    for path in files:
        try:
            text = read_text(path)
        except OSError as exc:                       # 权限等意外也只跳过这一个文件
            failed.append((path.name, f"读取失败：{exc}"))
            continue
        if text is None:
            failed.append((path.name, "编码无法识别或读取失败"))
            continue
        words = cut_words(text, stopwords)
        if not words:
            failed.append((path.name, "没有提取到有效词"))
            continue
        # 全库词频靠 all_words 汇总；每篇自己的 Top10 单独存，供报告和 CSV 用
        all_words.extend(words)
        per_file[path.name] = Counter(words).most_common(PER_FILE_N)
        print(f"已处理 {path.name}：{len(words)} 个有效词")
    return all_words, per_file, failed


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    """写一份 CSV：utf-8-sig 带 BOM，Excel 双击打开中文不会乱码。

    newline="" 是 csv 模块的固定写法，避免 Windows 下多出空行。
    """
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def write_report(top50: list[tuple[str, int]],
                 per_file: dict[str, list[tuple[str, int]]],
                 failed: list[tuple[str, str]],
                 total_words: int, path: Path) -> None:
    """写 TXT 版关键词报告：全库 Top50 + 每篇文档核心词 + 失败记录。"""
    lines = [
        "本地文档关键词报告",
        f"文档数：{len(per_file)}　有效词数：{total_words}　跳过文件数：{len(failed)}",
        "",
        "== 全库 Top 50 高频词 ==",
    ]
    lines += [f"{i:2d}. {w}\t{n}" for i, (w, n) in enumerate(top50, 1)]
    lines += ["", "== 各文档核心关键词 =="]
    for name, pairs in per_file.items():
        lines += [f"[{name}]", "  " + "、".join(f"{w}({n})" for w, n in pairs)]
    if failed:                                     # 把错误也留在报告里，方便回头查
        lines += ["", "== 未参与统计的文件 =="]
        lines += [f"- {name}：{reason}" for name, reason in failed]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def draw_wordcloud(top50: list[tuple[str, int]]) -> Path:
    """生成词云、保存 PNG，再弹窗展示。

    先 to_file 落盘再 plt.show()，窗口没关时 output/ 里也已经有图。
    """
    wc = WordCloud(
        font_path=FONT,
        width=1000, height=800,
        background_color="white",
        max_words=TOP_N,
        collocations=False,
        random_state=42,       # 固定布局，结果可复现
    )
    wc.generate_from_frequencies(dict(top50))
    png = OUT / "document_wordcloud.png"
    wc.to_file(str(png))

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.figure(figsize=(10, 8))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title("本地文档高频词云分析")
    plt.show()
    return png


def main() -> int:
    # 1. 先检查输入目录和字体；缺了给可读提示并正常退出，不抛 Traceback
    if not DOCS.is_dir():
        print(f"[错误] 找不到文档目录：{DOCS}")
        return 1
    if not Path(FONT).is_file():
        print(f"[错误] 找不到中文字体：{FONT}，词云会显示成方框")
        return 1

    # 2. 自定义词典必须在分词之前加载；停用词表不存在就用空集合
    if USER_DICT_FILE.is_file():
        try:
            jieba.load_userdict(str(USER_DICT_FILE))
            print("已加载自定义词典")
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            print(f"[警告] 自定义词典加载失败，已跳过：{exc}")
    stopwords = set(load_lines(STOPWORDS_FILE))
    print(f"停用词 {len(stopwords)} 个")

    # 3. 遍历 docs/ 下的 .txt 与 .md；按文件名排序，保证每次运行结果一致
    files = sorted(p for p in DOCS.iterdir()
                   if p.is_file() and p.suffix.lower() in (".txt", ".md"))
    if not files:
        print(f"[错误] {DOCS} 里没有 .txt / .md 文档")
        return 1

    # 4. 逐篇处理，同时把读不动的文件记进 failed 清单
    all_words, per_file, failed = collect_words(files, stopwords)
    for name, reason in failed:
        print(f"[错误] {name}：{reason}，已跳过并继续处理其他文件")

    # 5. 全部文件都没提出有效词：打印提示，不生成输出，正常退出
    if not all_words:
        print("[提示] 所有文件都没有提取到有效词，本次不生成词云和报告")
        return 0

    # 6. 统计全库 Top50，输出目录这时才建，避免上面那种情况留下空文件
    OUT.mkdir(parents=True, exist_ok=True)
    top50 = Counter(all_words).most_common(TOP_N)

    write_report(top50, per_file, failed, len(all_words),
                 OUT / "keywords_report.txt")
    # 全库 Top50：排名 / 关键词 / 词频
    write_csv(OUT / "top50_words.csv", ["排名", "关键词", "词频"],
              [[i, w, n] for i, (w, n) in enumerate(top50, 1)])
    # 按文件展开：一个文件对应最多 10 行，列名 文件名 / 关键词 / 词频
    write_csv(OUT / "keywords_report.csv", ["文件名", "关键词", "词频"],
              [[name, w, n] for name, pairs in per_file.items() for w, n in pairs])

    # 7. 词云：先写 PNG，再弹窗
    png = draw_wordcloud(top50)

    # 8. 打印本次结果摘要
    print(f"已处理 {len(per_file)} 篇文档、{len(all_words)} 个有效词"
          f"，跳过 {len(failed)} 个文件")
    print("output/ 已生成：document_wordcloud.png、keywords_report.txt、"
          "top50_words.csv、keywords_report.csv")
    print(f"词云已保存：{png}")
    print("Top 10：" + "、".join(f"{w}({n})" for w, n in top50[:10]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
