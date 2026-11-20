"""实验 4：本地文档智能审查与摘要（最小可运行版）。

在 PyCharm 里右键运行本文件即可：
  遍历 docs/ 下的 .txt / .md -> jieba 精确模式分词 -> 过滤 -> 统计 Top50
  -> 生成中文词云 PNG 与关键词报告到 output/ -> 弹窗展示词云。
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# ---- 路径与常量：都相对本文件定位，换到任何目录运行都不会找不到文件 ----
ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
OUT = ROOT / "output"
STOPWORDS_FILE = ROOT / "stopwords.txt"
USER_DICT_FILE = ROOT / "user_dict.txt"
FONT = r"C:\Windows\Fonts\msyh.ttc"        # 微软雅黑，保证词云里的中文不是方框
TOP_N = 50                                 # 词云与全库报告取前 50 个词
PER_FILE_N = 10                            # 每篇文档在报告里列出前 10 个关键词
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


def write_report(top50: list[tuple[str, int]],
                 per_file: dict[str, list[tuple[str, int]]],
                 total_words: int, path: Path) -> None:
    """写关键词报告：全库 Top50 + 每篇文档各自的核心关键词。"""
    lines = [
        "本地文档关键词报告",
        f"文档数：{len(per_file)}　有效词数：{total_words}",
        "",
        "== 全库 Top 50 高频词 ==",
    ]
    lines += [f"{i:2d}. {w}\t{n}" for i, (w, n) in enumerate(top50, 1)]
    lines += ["", "== 各文档核心关键词 =="]
    for name, pairs in per_file.items():
        lines += [f"[{name}]", "  " + "、".join(f"{w}({n})" for w, n in pairs)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    # 1. 先检查输入目录和字体；缺了给可读提示并正常退出，不抛 Traceback
    if not DOCS.is_dir():
        print(f"[错误] 找不到文档目录：{DOCS}")
        return 1
    if not Path(FONT).is_file():
        print(f"[错误] 找不到中文字体：{FONT}，词云会显示成方框")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)

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

    all_words: list[str] = []
    per_file: dict[str, list[tuple[str, int]]] = {}
    for path in files:
        text = read_text(path)
        if text is None:
            print(f"[警告] {path.name} 编码无法识别或读取失败，已跳过")
            continue
        words = cut_words(text, stopwords)
        if not words:
            print(f"[警告] {path.name} 没提取到有效词，已跳过")
            continue
        all_words.extend(words)
        per_file[path.name] = Counter(words).most_common(PER_FILE_N)
        print(f"已处理 {path.name}：{len(words)} 个有效词")
    if not all_words:
        print("[错误] 所有文档都没有有效词，请检查内容或停用词表")
        return 1

    # 4. 统计全库 Top50，并写出关键词报告（TXT）
    top50 = Counter(all_words).most_common(TOP_N)
    report = OUT / "keywords_report.txt"
    write_report(top50, per_file, len(all_words), report)

    # 5. 生成词云：按实验要求指定中文字体、白底、1000x800、最多 50 词
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
    wc.to_file(str(png))       # 先落盘：窗口还开着时 output/ 里也已经有图了

    print(f"词云已保存：{png}")
    print(f"关键词报告已保存：{report}")
    print("Top 10：" + "、".join(f"{w}({n})" for w, n in top50[:10]))

    # 6. 弹窗展示词云；plt.show() 会阻塞到关闭窗口，所以放在保存之后
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.figure(figsize=(10, 8))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title("本地文档高频词云分析")
    plt.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
