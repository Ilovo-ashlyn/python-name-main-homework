# 开发工具配置（非作业内容）

> 这个文件夹里**没有作业代码**，只是本机 PyCharm 和 Git 同步用的辅助文件。
> 查看作业时请直接看仓库根目录的三个文件夹：`name-main/`、`montecarlo-shapes/`、`character-grid/`。

## 里面都有什么

| 文件 | 作用 |
| --- | --- |
| `sync_from_pycharm.py` | 把本机 `D:\pycharm` 里三份作业的改动同步到本仓库对应子目录 |
| `idea-config/modules.xml` | PyCharm 的模块清单，记录项目由哪个 `.iml` 描述 |
| `idea-config/runConfigurations/*.xml` | 5 个「一键运行」按钮的配置（运行哪个脚本、工作目录、解释器） |
| `python-name-main-homework.iml` | PyCharm 模块定义：把三个作业目录设为源码根、排除虚拟环境 |

`.idea/` 是 PyCharm 自己的配置目录，正常应放在项目根目录。为了不让工程文件混在作业里，这里把可共享的那份配置改名为 `idea-config/` 收进本文件夹；本机实际使用的 `.idea/` 和 `.iml` 仍留在仓库根目录，由 `.gitignore` 排除，不会上传到 GitHub。

## 在新电脑上用 PyCharm 打开

1. clone 本仓库，用 **File → Open** 选仓库根目录。
2. 把 `idea-config/` 复制成根目录的 `.idea/`，把 `python-name-main-homework.iml` 复制到根目录。
3. 解释器选本机 Python（作业只用标准库，Python 3.8+ 即可，不需要 `pip install`）。
4. 右上角运行配置下拉里会出现 5 个配置，选一个点 ▶ 即可运行。

| 运行配置 | 作用 |
| --- | --- |
| `01 name-main \| 五个实验` | 一次跑完 `__name__` 的全部对照实验 |
| `02 montecarlo \| 生成图形` | 生成 5 张 PNG 到 `montecarlo-shapes/output/` |
| `02 montecarlo \| 自检` | 校验 PNG 结构与统计结果 |
| `03 character-grid \| n=4 示例` | 画 4×4 田字格并生成示例文本 |
| `03 character-grid \| 自检` | 校验行数、列数、边框位置 |

> 运行配置里的解释器路径是本机专用的，换电脑后按第 3 步重新选一次即可。

## 改完代码怎么上传

在**仓库根目录**执行：

```bash
python pycharm-setup/sync_from_pycharm.py
git add . && git commit -m "sync homework from PyCharm" && git push
```

同步脚本只覆盖三个作业目录内的文件，不会动其它内容；源目录可用 `--source` 指定。
