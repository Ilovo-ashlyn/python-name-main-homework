# Python 作业合集

Python 课程作业与实验。6 份编程作业都是**一个 `.py` + 一个短 README**，代码简短、运行就出结果；四个实验按课程实验要求单独成目录，各自带实验报告／说明与运行截图。

## 作业索引（6 份）

| 作业 | 文件夹 | 内容 | 运行（进入该文件夹后） |
| --- | --- | --- | --- |
| 1 | [`name-main/`](name-main/README.md) | `if __name__ == '__main__':` 的含义与 why | `python name_main.py`（18 行） |
| 2 | [`montecarlo-shapes/`](montecarlo-shapes/README.md) | 蒙特卡罗投点：π、心形面积、谢尔宾斯基、定积分、收敛曲线 | `python montecarlo.py`（79 行，弹出图形窗口） |
| 3 | [`character-grid/`](character-grid/README.md) | 教材 5.1 字符田字格，函数 + 尺寸参数 | `python tianzige.py 4`（25 行） |
| 4 | [`koch-snowflake/`](koch-snowflake/README.md) | 科赫雪花 0~4 阶递归 | `python koch.py`（42 行，弹出图形窗口） |
| 5 | [`word-frequency/`](word-frequency/README.md) | 统计「十五五」规划纲要热词频率（jieba 分词 + Counter） | `python wordfreq.py`（43 行，控制台输出 Top 20） |
| 6 | [`lonely-poem/`](lonely-poem/README.md) | 教材 P205 实例 6A 孤独的古诗词 + 练习 6.1/6.2/6.3（列表与集合） | `python lonely_poem.py`（38 行，控制台输出） |

## 实验

| 实验 | 文件夹 | 内容 | 运行（进入该文件夹后） |
| --- | --- | --- | --- |
| 实验 1 | [`exp1/`](exp1/README.md) | Python Vibe Coding 实操考核：Excel 报表清洗统计（四 sheet）+ FastAPI 记账接口；含 pytest 测试、运行截图与 AI 协作记录 | `python excel_report.py`；`uvicorn ledger_api:app`；`pytest -q` |
| 实验 2 | [`exp2/`](exp2/README.md) | 数据看板的设计与实现（仅基础部分）：Streamlit + Pandas + Plotly 静态看板 | `streamlit run app.py`，服务就绪后自动打开 http://localhost:8501 |
| 实验 3 | [`exp3/`](exp3/README.md) | Python 列表、元组、集合：切片删除预判、可哈希辨析、集合运算、保序去重、选课综合设计 | `python list_tuple_set.py`（138 行，控制台一次输出 5 个任务 + 拓展） |
| 实验 4 | [`exp4/`](exp4/README.md) | 本地文档智能审查与摘要（第一版）：批量读取 txt/md、jieba 分词、停用词过滤、Top 50 词频统计、中文词云与关键词报告 | `python analyze.py`（弹出词云窗口，在 `output/` 生成 PNG 与报告） |

> `exp1/`～`exp4/` 是课程实验，与上面 6 份编程作业分开，目录按实验号单独命名；各自的实验报告、成品／运行截图都在目录里。实验 1 按考核要求是多文件工程（含 `requirements.txt`、`tests/`、`ai_logs/`），实验 4 因题目指定依赖也单列 `requirements.txt`，与前面「单文件」的编程作业不同。

## 环境与依赖

- Python 3.13（本机 PyCharm 用 `D:\pycharm\venv`，Python 3.13.0）。
- 作业 1、3、6 与**实验 3 只用标准库**，不用装包；作业 2、4 需要 `pip install numpy matplotlib`（作业 4 只需 matplotlib）；作业 5 需要 `pip install jieba`。
- **实验 1 需要 `pip install -r exp1/requirements.txt`**（pandas / openpyxl / fastapi / uvicorn / pytest / httpx / pydantic；本机 venv 已装好）。
- **实验 2 需要 `pip install streamlit pandas plotly`**；本机 venv 已装好 streamlit 1.67.0 / pandas 3.1.1 / plotly 7.1.0。
- **实验 4 需要 `pip install -r exp4/requirements.txt`**（jieba / wordcloud / matplotlib / numpy / pillow；本机 venv 已装好 wordcloud 1.9.6、jieba 0.42.1）。
- 作业 2、4 与**实验 4 运行即弹出图形窗口**，不用去点图片文件；作业 5、6 与实验 3 直接在控制台打印结果；实验 1 生成 `report.xlsx` 并可启动本地接口，实验 2 启动本地网页看板。
- 作业 5 的 `report.txt` 是报告全文语料，可直接换成老师指定的文本；实验 4 的 `docs/` 是示例语料，换成自己的 `.txt` / `.md` 即可。
- 随机实验固定种子，几何实验与词云布局完全确定，结果均可复现。

## 目录结构

```
python-name-main-homework/
├── README.md            ← 本文件：作业与实验总索引
├── name-main/           ← 作业 1：name_main.py + README.md
├── montecarlo-shapes/   ← 作业 2：montecarlo.py + README.md
├── character-grid/      ← 作业 3：tianzige.py + README.md
├── koch-snowflake/      ← 作业 4：koch.py + README.md
├── word-frequency/      ← 作业 5：wordfreq.py + report.txt + README.md
├── lonely-poem/         ← 作业 6：lonely_poem.py + README.md
├── exp1/                ← 实验 1：两个脚本 + tests/ + ai_logs/ + 数据与报表 + 截图
├── exp2/                ← 实验 2：app.py + data.csv + dashboard.png + README.md
├── exp3/                ← 实验 3：list_tuple_set.py + run_output.png + README.md
├── exp4/                ← 实验 4：analyze.py + docs/ + 词表 + output/ 成品 + README.md
├── pycharm-setup/       ← 非作业内容：本机 PyCharm 配置与同步脚本
└── .gitignore          ← Git 忽略清单
```
