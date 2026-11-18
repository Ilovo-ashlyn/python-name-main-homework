# 开发工具配置（非作业内容）

> 这个文件夹里**没有作业代码**，只是本机 PyCharm 和 Git 同步用的辅助文件。
> 查看作业时请直接看仓库根目录的四个文件夹：`name-main/`、`montecarlo-shapes/`、`character-grid/`、`koch-snowflake/`。

## 里面都有什么

| 文件 | 作用 |
| --- | --- |
| `sync_from_pycharm.py` | 把本机 `D:\pycharm` 里四份作业的改动同步到本仓库对应子目录 |
| `idea-config/modules.xml` | PyCharm 的模块清单，记录项目由哪个 `.iml` 描述 |
| `idea-config/runConfigurations/*.xml` | 9 个「一键运行」按钮的配置（运行哪个脚本、工作目录、解释器） |
| `python-name-main-homework.iml` | PyCharm 模块定义：把四个作业目录设为源码根、排除虚拟环境 |

`.idea/` 是 PyCharm 自己的配置目录，正常应放在项目根目录。为了不让工程文件混在作业里，这里把可共享的那份配置改名为 `idea-config/` 收进本文件夹；本机实际使用的 `.idea/` 和 `.iml` 仍留在仓库根目录，由 `.gitignore` 排除，不会上传到 GitHub。

## 在新电脑上用 PyCharm 打开

1. clone 本仓库，用 **File → Open** 选仓库根目录。
2. 把 `idea-config/` 复制成根目录的 `.idea/`，把 `python-name-main-homework.iml` 复制到根目录。
3. 解释器选本机 Python 3.8+：四份作业的主实现只用标准库，**不需要 `pip install`**。
   如果要跑蒙特卡罗的 numpy 对照版，再在 PyCharm 的 Terminal 里执行
   `pip install -r montecarlo-shapes/requirements.txt`（安装 numpy 与 matplotlib）。
4. 右上角运行配置下拉里会出现 9 个配置，选一个点 ▶ 即可运行。

| 运行配置 | 作用 |
| --- | --- |
| `01 name-main \| 五个实验` | 一次跑完 `__name__` 的全部对照实验 |
| `02 montecarlo \| 生成图形` | 生成 5 张 PNG，并自动弹出浏览器画廊直接显示图案 |
| `02 montecarlo \| 生成图形并看图` | 同上（旧参数名，现在默认就会自动显示） |
| `02 montecarlo \| 自检` | 校验 PNG 结构、统计结果与图片画廊 |
| `02 montecarlo \| 运行即显示图案（numpy）` | **运行后弹出图形窗口，直接显示 5 张图案**，需先装 requirements.txt |
| `03 character-grid \| n=4 示例` | 画 4×4 田字格并生成示例文本 |
| `03 character-grid \| 自检` | 校验行数、列数、边框位置 |
| `04 koch-snowflake \| 生成 0~4 阶并看图` | 生成 5 个阶数的雪花 PNG 并打开画廊 |
| `04 koch-snowflake \| 自检` | 校验递归几何、面积公式、PNG 结构与画廊 |

> 运行配置里的解释器路径是本机专用的，换电脑后按第 3 步重新选一次即可。
>
> 蒙特卡罗的两个入口**运行即显示图案**：手搓版自动打开浏览器画廊，numpy 版弹出 matplotlib 图形窗口；都不需要手动去 `output/` 里点图片文件。无图形界面时加 `--no-show` 只生成文件。科赫雪花作业的图片仍是 `output/*.png`，双击 `output/index.html` 可一次看齐。
>
> 装完第三方包后，PyCharm 的 **Settings → Python Interpreter** 软件包列表若没立即显示，点一下刷新或重新打开项目即可。

## 改完代码怎么上传

在**仓库根目录**执行：

```bash
python pycharm-setup/sync_from_pycharm.py
git add . && git commit -m "sync homework from PyCharm" && git push
```

同步脚本只覆盖四个作业目录内的文件，不会动其它内容；源目录可用 `--source` 指定。
