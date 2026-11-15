"""一键运行全部实验，把输出和 README.md 的「预期输出」表格对照看。

运行：python run_all_demos.py
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

CASES = [
    ("实验 1 | 直接运行带保护的模块", "demo_module.py"),
    ("实验 2 | 导入带保护的模块", "import_demo.py"),
    ("实验 3 | 直接运行没有保护的模块（反例）", "no_guard.py"),
    ("实验 4 | 导入没有保护的模块（反例）", "import_no_guard.py"),
    ("实验 5 | 最小标准模板", "direct_run.py"),
]


def main() -> None:
    # 子进程直接写 stdout；父进程改为行缓冲，避免重定向时输出顺序错乱
    sys.stdout.reconfigure(line_buffering=True)

    for title, script in CASES:
        print("=" * 62)
        print(f"{title}   →   python {script}")
        print("-" * 62)
        result = subprocess.run([sys.executable, str(HERE / script)], cwd=HERE)
        if result.returncode != 0:
            print(f"（该脚本退出码：{result.returncode}）")
        print()

    print("=" * 62)
    print("对照 README.md 第 3 节看结论：保护块只控制缩进内的代码。")


if __name__ == '__main__':
    main()
