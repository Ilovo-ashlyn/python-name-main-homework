"""把本机 PyCharm 项目里的六份作业同步到本仓库对应子目录。

用法（在仓库根目录执行）：
    python pycharm-setup/sync_from_pycharm.py                    # 默认源目录 D:/pycharm
    python pycharm-setup/sync_from_pycharm.py --source D:/pycharm

同步方向：PyCharm 项目 -> 本仓库，只覆盖六个作业目录内的文件，
不会删除仓库里其它内容。同步完成后按提示 commit / push 即可上传 GitHub。
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path

# 本脚本位于 pycharm-setup/ 下，仓库根目录是它的上一级目录
REPO = Path(__file__).resolve().parent.parent
HOMEWORKS = ("name-main", "montecarlo-shapes", "character-grid",
             "koch-snowflake", "word-frequency", "lonely-poem")
SKIP = {"__pycache__", ".git", ".idea", "venv", ".venv", ".pytest_cache"}


def source_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP for part in rel.parts):
            continue
        yield rel


def sync(source: Path) -> int:
    changed = 0
    for name in HOMEWORKS:
        src_root, dst_root = source / name, REPO / name
        if not src_root.is_dir():
            print(f"[跳过] 源目录不存在: {src_root}")
            continue
        dst_root.mkdir(parents=True, exist_ok=True)
        for rel in source_files(src_root):
            src, dst = src_root / rel, dst_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists() and filecmp.cmp(src, dst, shallow=False):
                continue
            shutil.copy2(src, dst)
            print(f"[更新] {name}/{rel.as_posix()}")
            changed += 1
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="把 PyCharm 项目中的六份作业同步到本仓库对应子目录"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("D:/pycharm"),
        help="PyCharm 项目根目录（默认 D:/pycharm）",
    )
    args = parser.parse_args()
    changed = sync(args.source.resolve())
    if changed:
        print(f"\n同步完成，共更新 {changed} 个文件。接下来在仓库根目录执行：")
        print('  git add . && git commit -m "sync homework from PyCharm" && git push')
    else:
        print("\n六个作业目录已与仓库完全一致，没有文件需要更新。")


if __name__ == "__main__":
    main()
