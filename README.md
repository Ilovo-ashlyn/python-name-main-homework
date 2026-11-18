# Python 作业合集

Python 课程作业与实验。6 份编程作业都是**一个 `.py` + 一个短 README**，代码简短、运行就出结果；实验 2 是单独的网页数据看板。

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
| 实验 2 | [`exp2/`](exp2/README.md) | 数据看板的设计与实现（仅基础部分）：Streamlit + Pandas + Plotly 静态看板 | `streamlit run app.py`，浏览器打开 http://localhost:8501 |

> `exp2/` 是课程实验，与上面 6 份编程作业分开，目录按要求单独命名；内含 `app.py`、`data.csv`、`dashboard.png` 和实验说明。

## 环境与依赖

- Python 3.13（本机 PyCharm 用 `D:\pycharm\venv`，Python 3.13.0）。
- 作业 1、3、6 只用标准库，不用装包；作业 2、4 需要 `pip install numpy matplotlib`（作业 4 只需 matplotlib）；作业 5 需要 `pip install jieba`。
- **实验 2 需要 `pip install streamlit pandas plotly`**；本机 venv 已装好 streamlit 1.67.0 / pandas 3.1.1 / plotly 7.1.0。
- 作业 2、4 **运行即弹出图形窗口**，不用去点图片文件；作业 5、6 直接在控制台打印结果；实验 2 启动本地网页看板。
- 作业 5 的 `report.txt` 是报告全文语料，可直接换成老师指定的文本。
- 随机实验固定种子，几何实验完全确定，结果均可复现。

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
├── exp2/                ← 实验 2：app.py + data.csv + dashboard.png + README.md
├── pycharm-setup/       ← 非作业内容：本机 PyCharm 配置与同步脚本
└── .gitignore          ← Git 忽略清单
```
