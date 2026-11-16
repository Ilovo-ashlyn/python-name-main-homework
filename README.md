# Python 作业合集

> Python 课程作业 · 纯标准库、零第三方依赖 · Python 3.8+

每份作业各占一个子目录，进入目录即可运行；作业答案与讲解见各目录内的 `README.md`。

## 作业索引

| 目录 | 作业内容 | 运行方式 |
| --- | --- | --- |
| [`name-main/`](name-main/README.md) | `if __name__ == '__main__':` 的含义与 why（5 组对照实验） | `python run_all_demos.py` |
| [`montecarlo-shapes/`](montecarlo-shapes/README.md) | 蒙特卡罗方法手搓图形（手写 PNG 编码器，5 个实验） | `python draw_all.py` / `python selftest.py` |
| [`character-grid/`](character-grid/README.md) | 教材 5.1 字符田字格绘制（函数化、任意尺寸） | `python demo.py 4` / `python selftest.py` |

## 目录结构

```
python-name-main-homework/
├── README.md            ← 本文件：仓库总索引
├── name-main/           ← 作业 1：__name__ 与程序入口
├── montecarlo-shapes/   ← 作业 2：蒙特卡罗手搓图形
├── character-grid/      ← 作业 3：字符田字格
└── .gitignore
```

## 统一约定

- 全部代码只用标准库，不需要 `pip install` 任何东西（本机 Python 3.13.14 实测通过）。
- 随机实验固定种子，结果可复现。
- 每份作业自带讲解型 `README.md`、`output/` 示例和自检脚本。
- 子目录 README 中的图片使用相对路径，在 GitHub 页面上会直接显示。
