# 实验 4 · 本地文档智能审查与摘要（第二版）

批量读取 `docs/` 下的 `.txt` / `.md`，用 jieba 精确模式分词、过滤停用词与单字，统计 Top 50 高频词，生成中文词云和关键词报告。只做基础功能，不接大模型 API、不做 watchdog 文件夹监控、不做蒙特卡洛模拟。

第二版在第一版基础上补了两份 CSV 输出、读取失败的逐条记录、全部无有效词时的正常退出，并把 `main()` 拆成几个单一职责的小函数。

## 目录

```
exp4/
├── analyze.py                   主程序，右键运行
├── docs/                        待分析的 .txt / .md 文档
├── stopwords.txt                停用词表，每行一词，UTF-8
├── user_dict.txt                自定义词典，每行一词，UTF-8
├── output/                      程序输出目录
│   ├── document_wordcloud.png   词云成品（1000×800）
│   ├── keywords_report.txt      关键词报告：全库 Top50 + 各文档 Top10 + 跳过记录
│   ├── top50_words.csv          全库 Top50：排名 / 关键词 / 词频
│   └── keywords_report.csv      各文档 Top10：文件名 / 关键词 / 词频
├── requirements.txt             依赖版本
└── README.md                    本文件
```

## 安装与运行

```bash
pip install -r requirements.txt
python analyze.py
```

在 PyCharm 里右键 `analyze.py` → Run 即可。程序**先**把 4 份输出写进 `output/`，**再**弹出窗口显示词云，所以窗口开着时文件已经写好（PyCharm 开着 Scientific Mode 时图在右侧 SciView）。

## 输出说明

两份 CSV 都用 `utf-8-sig` 写入（带 BOM），Excel 双击打开中文不会乱码，用标准库 `csv` 模块生成。

| 文件 | 列 | 行数 |
| --- | --- | --- |
| `top50_words.csv` | 排名、关键词、词频 | 全库 Top 50，排名 1～50 |
| `keywords_report.csv` | 文件名、关键词、词频 | 每篇成功处理的文档各最多 10 行 |

`keywords_report.txt` 保留纯文本版，末尾另有「未参与统计的文件」一节，把读取失败和没提出有效词的文件连原因一起记下来。

## 实现要点

- `pathlib` 遍历 `docs/` 下的 `.txt` 和 `.md`，按文件名排序，结果可复现
- 读取依次尝试 `utf-8-sig` / `utf-8` / `gbk`；`jieba.load_userdict()` 加载自定义词典；停用词表不存在就用空集合
- 过滤停用词、单字、纯数字、纯标点；`Counter` 统计词频，取 Top 50
- 函数结构：`read_text` / `load_lines` / `cut_words` / `collect_words` / `write_csv` / `write_report` / `draw_wordcloud`，`main()` 只负责按步骤编排，没有类和配置项
- **单个文件读不动**：记一笔 `(文件名, 原因)`，控制台逐条报错、报告里也留档，其余文件继续处理，不会整批中断
- **所有文件都没有有效词**：打印明确提示，不生成任何输出文件，返回 0 正常退出
- 目录或中文字体缺失：中文提示并返回 1，不抛 Traceback
- `WordCloud` 指定 `C:\Windows\Fonts\msyh.ttc`，白底 1000×800、`max_words=50`、`collocations=False`、`random_state=42`

## 实测结果（本机 Python 3.13.0）

- 4 篇示例文档、380 个有效词、跳过 0 个文件；`output/` 生成 4 份文件
- 词云里的中文正常显示，不是方框；`plt.show()` 弹出 `Figure 1` 窗口
- `top50_words.csv` 50 行、`keywords_report.csv` 40 行（4 篇 × 10）；BOM、表头、排名连续性和词频均已核对，与 TXT 报告数值一致
- 全库 Top 10：文档(17)、词云(14)、分词(11)、停用词(9)、中文(8)、关键词(6)、关键词报告(5)、文件夹(5)、词频统计(4)、过滤(4)
- 异常回归：坏编码文件 + 无有效词文件同时存在时其余文档照常出结果；全部无有效词、全部读取失败都正常退出且不生成空文件；`docs/` 缺失或空目录会明确报错

## 换成自己的文档

把要分析的 `.txt` / `.md` 放进 `docs/`，删掉示例文件即可；`stopwords.txt` 和 `user_dict.txt` 按每行一个词补充。若本机没有微软雅黑，把 `analyze.py` 里的 `FONT` 换成 `C:\Windows\Fonts\simhei.ttf` 的完整路径。
