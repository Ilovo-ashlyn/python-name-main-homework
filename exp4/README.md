# 实验 4 · 本地文档智能审查与摘要（第一版）

批量读取 `docs/` 下的 `.txt` / `.md`，用 jieba 精确模式分词、过滤停用词与单字，统计 Top 50 高频词，生成中文词云和关键词报告。只做基础功能，不接大模型 API、不做 watchdog 文件夹监控、不做蒙特卡洛模拟。

## 目录

```
exp4/
├── analyze.py                   主程序，右键运行
├── docs/                        待分析的 .txt / .md 文档
├── stopwords.txt                停用词表，每行一词，UTF-8
├── user_dict.txt                自定义词典，每行一词，UTF-8
├── output/                      程序输出目录
│   ├── document_wordcloud.png   词云成品
│   └── keywords_report.txt      关键词报告
├── requirements.txt             依赖版本
└── README.md                    本文件
```

## 安装与运行

```bash
pip install -r requirements.txt
python analyze.py
```

在 PyCharm 里右键 `analyze.py` → Run 即可。程序**先**生成 `output/` 里的词云 PNG 和关键词报告，**再**弹出窗口显示词云，所以窗口开着时文件已经写好（PyCharm 开着 Scientific Mode 时图在右侧 SciView）。

## 实现要点

- `pathlib` 遍历 `docs/` 下的 `.txt` 和 `.md`，按文件名排序，结果可复现
- 读取依次尝试 `utf-8-sig` / `utf-8` / `gbk`；单个文件读不了只警告并跳过，不中断整批
- `jieba.load_userdict()` 加载自定义词典；停用词表不存在就用空集合
- 过滤停用词、单字、纯数字、纯标点；`Counter` 统计词频，取 Top 50
- `WordCloud` 指定 `C:\Windows\Fonts\msyh.ttc`，白底 1000×800、`max_words=50`、`collocations=False`、`random_state=42`
- 报告含全库 Top 50 与每篇文档各自的 Top 10 关键词
- 输入目录、字体缺失或读取失败都有中文提示，正常退出，不抛 Traceback

## 实测结果（本机 Python 3.13.0）

- 4 篇示例文档，输出 `output/document_wordcloud.png`（1000×800）与 `output/keywords_report.txt`
- 词云里的中文正常显示，不是方框；窗口由 `plt.show()` 自动弹出
- 共提取 380 个有效词；全库 Top 10：文档(17)、词云(14)、分词(11)、停用词(9)、中文(8)、关键词(6)、关键词报告(5)、文件夹(5)、词频统计(4)、过滤(4)，完整 Top 50 见报告

## 换成自己的文档

把要分析的 `.txt` / `.md` 放进 `docs/`，删掉示例文件即可；`stopwords.txt` 和 `user_dict.txt` 按每行一个词补充。若本机没有微软雅黑，把 `analyze.py` 里的 `FONT` 换成 `C:\Windows\Fonts\simhei.ttf` 的完整路径。
