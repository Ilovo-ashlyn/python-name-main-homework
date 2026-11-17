# Python 作业合集

Python 课程作业，共 3 份。每份作业独立占一个文件夹，全部使用 Python 标准库实现，**零第三方依赖**，不需要 `pip install` 任何东西。

## 作业索引

| 作业 | 文件夹 | 内容 | 运行方式（进入该文件夹后） |
| --- | --- | --- | --- |
| 作业 1 | [`name-main/`](name-main/README.md) | `if __name__ == '__main__':` 的含义与 why：5 组对照实验 | `python run_all_demos.py` |
| 作业 2 | [`montecarlo-shapes/`](montecarlo-shapes/README.md) | 蒙特卡罗方法手搓图形：手写 PNG 编码器 + 投点估 π、心形、Sierpinski、定积分、收敛曲线 | `python draw_all.py` / `python selftest.py` |
| 作业 3 | [`character-grid/`](character-grid/README.md) | 教材 5.1 字符田字格绘制：函数化、任意尺寸 | `python demo.py 4` / `python selftest.py` |

每个作业文件夹里都自带：

- `README.md` —— 题目、思路、**完整答案**与实测结果（图片用相对路径，在 GitHub 页面上会直接显示）
- `*.py` —— 可直接运行的源代码
- `output/` —— 运行后生成的示例图片 / 文本（作业 1 的结果打印在控制台，不生成文件）
- `selftest.py` —— 一键自检（作业 1 用 `run_all_demos.py` 的对照输出代替）

## 目录结构

```
python-name-main-homework/
├── README.md            ← 本文件：作业总索引
├── name-main/           ← 作业 1：__name__ 与程序入口
├── montecarlo-shapes/   ← 作业 2：蒙特卡罗手搓图形
├── character-grid/      ← 作业 3：字符田字格
├── pycharm-setup/       ← 非作业内容：本机 PyCharm 配置与同步脚本
└── .gitignore           ← Git 忽略清单（缓存、虚拟环境等）
```

> `pycharm-setup/` 只是开发工具配置，不是作业内容，说明见其中的 `README.md`。

## 统一约定

- 只用标准库，Python 3.8+ 即可运行（本机 3.13 实测通过）。
- 随机实验固定种子，结果可复现。
- 进入对应文件夹后运行命令即可，不需要从仓库根目录运行。
- 在 PyCharm 中打开本项目的方法见 [`pycharm-setup/README.md`](pycharm-setup/README.md)。
