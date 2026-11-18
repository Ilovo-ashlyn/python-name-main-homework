"""作业 5：统计《「十五五」规划纲要》热词频率。

运行：python wordfreq.py      （同目录下要有 report.txt）
依赖：pip install jieba
"""
import logging
import re
from collections import Counter
from pathlib import Path
import jieba
import jieba.posseg as pseg

TOP_N = 20                          # 输出前 20 个热词
jieba.setLogLevel(logging.ERROR)     # 关掉分词库自带的加载提示

# 报告里的专有名词，加进词典才不会被切碎
for w in ("新质生产力", "数智化", "高质量发展", "现代化产业体系", "全国统一大市场"):
    jieba.add_word(w, tag="n")

# 没有实际意义的虚词，统计时跳过
STOP = set("以及 其中 一是 二是 我们 他们 通过 对于 关于 按照 根据 有关 相关 各类 各种 一个 一些 "
           "可以 能够 这个 那个 这些 那些 同时 并且 或者 还是 主要 进一步 不断 更加 积极 大力".split())


def words(text):
    """只留 2 字以上的中文名词，自动去掉「推进、加强」这类动词套话。"""
    for w, flag in pseg.lcut(text):
        if (flag.startswith(("n", "vn")) and len(w) >= 2
                and re.fullmatch(r"[\u4e00-\u9fff]+", w) and w not in STOP):
            yield w


def main():
    text = Path(__file__).with_name("report.txt").read_text(encoding="utf-8")
    counter = Counter(words(text))
    print(f"《「十五五」规划纲要》共 {len(text):,} 字，{sum(counter.values()):,} 个有效词\n")
    print(f"热词 Top {TOP_N}：")
    for i, (w, n) in enumerate(counter.most_common(TOP_N), 1):
        print(f"{i:>2}. {w}{' ' * max(1, 12 - 2 * len(w))}{n:>5}")  # 中文按 2 列宽对齐


if __name__ == "__main__":
    main()
