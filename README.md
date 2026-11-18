# Python 作业合集

Python 课程作业，共 5 份。每份作业**只有一个 `.py` 文件 + 一个短 README**，代码都在 80 行以内，运行就出结果。

## 作业索引

| 作业 | 文件夹 | 内容 | 运行（进入该文件夹后） |
| --- | --- | --- | --- |
| 1 | [`name-main/`](name-main/README.md) | `if __name__ == '__main__':` 的含义与 why | `python name_main.py`（18 行） |
| 2 | [`montecarlo-shapes/`](montecarlo-shapes/README.md) | 蒙特卡罗投点：π、心形面积、谢尔宾斯基、定积分、收敛曲线 | `python montecarlo.py`（79 行，弹出图形窗口） |
| 3 | [`character-grid/`](character-grid/README.md) | 教材 5.1 字符田字格，函数 + 尺寸参数 | `python tianzige.py 4`（25 行） |
| 4 | [`koch-snowflake/`](koch-snowflake/README.md) | 科赫雪花 0~4 阶递归 | `python koch.py`（42 行，弹出图形窗口） |
| 5 | [`word-frequency/`](word-frequency/README.md) | 统计「十五五」规划纲要热词频率（jieba 分词 + Counter） | `python wordfreq.py`（43 行，控制台输出 Top 20） |

## 环境与依赖

- Python 3.13（本机 PyCharm 用 `D:\pycharm\venv`，Python 3.13.0）。
- 作业 1、3 只用标准库，不用装包；作业 2、4 需要 `pip install numpy matplotlib`（作业 4 只需 matplotlib）；作业 5 需要 `pip install jieba`。本机 venv 已全部装好。
- 作业 2、4 **运行即弹出图形窗口**，不用去点图片文件；作业 5 直接在控制台打印热词榜。
- 作业 5 的 `report.txt` 是报告全文语料，可直接换成老师指定的文本。
- 随机实验固定种子，几何实验完全确定，结果均可复现。

## 目录结构

```
python-name-main-homework/
├── README.md            ← 本文件：作业总索引
├── name-main/           ← 作业 1：name_main.py + README.md
├── montecarlo-shapes/   ← 作业 2：montecarlo.py + README.md
├── character-grid/      ← 作业 3：tianzige.py + README.md
├── koch-snowflake/      ← 作业 4：koch.py + README.md
├── word-frequency/      ← 作业 5：wordfreq.py + report.txt + README.md
├── pycharm-setup/       ← 非作业内容：本机 PyCharm 配置与同步脚本
└── .gitignore          ← Git 忽略清单
```

> 把网址发给老师时，看五个作业文件夹即可；`pycharm-setup/` 只是开发工具配置。
