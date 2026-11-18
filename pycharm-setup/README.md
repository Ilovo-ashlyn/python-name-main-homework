# 开发工具配置（非作业内容）

> 这个文件夹里**没有作业代码**，只是本机 PyCharm 和 Git 同步用的辅助文件。
> 查看作业请直接看仓库根目录的四个文件夹：`name-main/`、`montecarlo-shapes/`、`character-grid/`、`koch-snowflake/`。

## 里面都有什么

| 文件 | 作用 |
| --- | --- |
| `sync_from_pycharm.py` | 把本机 `D:\pycharm` 里四份作业同步到本仓库对应子目录 |
| `idea-config/modules.xml` | PyCharm 的模块清单，记录项目由哪个 `.iml` 描述 |
| `idea-config/runConfigurations/*.xml` | 4 个「一键运行」配置，每份作业一个 |
| `python-name-main-homework.iml` | 模块定义：把四个作业目录设为源码根、排除虚拟环境 |

本机实际使用的 `.idea/` 和 `.iml` 留在项目根目录，由 `.gitignore` 排除，不会上传到 GitHub；这里的可共享副本改名为 `idea-config/` 收进本文件夹，避免工程文件混在作业里。

## 在新电脑上用 PyCharm 打开

1. clone 本仓库，用 **File → Open** 选仓库根目录。
2. 把 `idea-config/` 复制成根目录的 `.idea/`，把 `python-name-main-homework.iml` 复制到根目录。
3. 解释器选 Python 3.8+；在 PyCharm Terminal 里执行 `pip install numpy matplotlib`（作业 1、3 不需要装包）。
4. 右上角运行配置下拉里会出现 4 个配置，选一个点 ▶ 即可运行。

| 运行配置 | 作用 |
| --- | --- |
| `01 name-main \| 运行` | 演示 `__name__` 在直接运行 / 被导入时的区别 |
| `02 montecarlo \| 运行即显示图案` | 弹出窗口显示 5 张投点图 |
| `03 character-grid \| 田字格 n=4` | 打印 4×4 田字格 |
| `04 koch \| 运行即显示 0~4 阶` | 弹出窗口显示 5 个阶数的雪花 |

> 运行配置里的解释器路径是本机专用的，换电脑后按第 3 步重新选一次即可。
> 作业 2、4 用 `plt.show()` 弹窗；若 PyCharm 开着 Scientific Mode，图会显示在右侧 SciView 里，关掉它就弹独立窗口。

## 本机已知问题：Tcl/Tk 路径（2026-11-18 已修复）

系统 Python 装在 `D:\` 根目录，它的 `_tkinter` 只按 `D:/lib/tcl8.6` 之类的路径找 `init.tcl`，而文件实际在 `D:\tcl\tcl8.6\`，所以 matplotlib 默认的 `TkAgg` 后端一创建窗口就报 `_tkinter.TclError: Can't find a usable init.tcl`，两道画图作业会崩。

修复写在本机 venv 的 `Lib/site-packages/sitecustomize.py`（Python 启动时自动加载，**作业代码一行都不用改**）：

```python
import os
os.environ.setdefault("TCL_LIBRARY", r"D:\tcl\tcl8.6")
os.environ.setdefault("TK_LIBRARY", r"D:\tcl\tk8.6")
```

换电脑若遇到同样报错，给解释器设置这两个环境变量，或把 Python 装到正常目录即可；官方安装的 Python 自带完整 Tcl，不需要这一步。

## 改完代码怎么上传

在**仓库根目录**执行：

```bash
python pycharm-setup/sync_from_pycharm.py
git add . && git commit -m "sync homework from PyCharm" && git push
```

同步脚本只覆盖四个作业目录内的文件，不会动其它内容；源目录可用 `--source` 指定。
