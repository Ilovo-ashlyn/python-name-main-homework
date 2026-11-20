"""考题一：销售原始表清洗与报表生成（pandas + openpyxl）。

一键运行：python excel_report.py
只读 sales_raw.xlsx，输出 report.xlsx，绝不修改原始文件。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

FIELDS = ["日期", "销售员", "产品", "数量", "单价", "地区"]
SHEETS = ["明细清洗后", "按销售员", "按地区", "总览"]


class ReportError(Exception):
    """面向使用者的可读错误：调用方捕获后打印，不抛 Traceback。"""


def read_raw(path: str | Path) -> pd.DataFrame:
    """读入原始表并校验文件与字段。"""
    p = Path(path)
    if not p.is_file():
        raise ReportError(f"找不到原始文件：{p}")
    if p.stat().st_size == 0:
        raise ReportError(f"原始文件是空文件（0 字节）：{p}")
    try:
        df = pd.read_excel(p, engine="openpyxl")
    except Exception as exc:
        raise ReportError(f"原始文件无法读取，请确认是未损坏的 .xlsx：{p}\n  原因：{exc}") from exc

    missing = [c for c in FIELDS if c not in df.columns]
    if missing:
        raise ReportError(f"原始文件缺少必需字段：{'、'.join(missing)}；实际字段：{list(df.columns)}")
    if df.empty:
        raise ReportError("原始文件没有数据行（只有表头），无法生成报表")
    return df[FIELDS].copy()


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """删缺失 → 剔数量<=0 → 全字段去重 → 算销售额。"""
    raw_n = len(df)
    d = df.copy()
    d["日期"] = pd.to_datetime(d["日期"], errors="coerce")
    for c in ("数量", "单价"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    for c in ("销售员", "产品", "地区"):
        d[c] = d[c].astype("string").str.strip().replace("", pd.NA)

    d = d.dropna(subset=FIELDS)
    n_missing = len(d)
    d = d[d["数量"] > 0]
    n_bad = len(d)
    d = d.drop_duplicates(subset=FIELDS)
    if d.empty:
        raise ReportError("清洗后没有有效数据：可能全是缺失值、数量<=0 或重复行")

    d["销售额"] = d["数量"] * d["单价"]
    d = d.reset_index(drop=True)
    stats = {
        "原始行数": raw_n,
        "缺失剔除": raw_n - n_missing,
        "数量异常剔除": n_missing - n_bad,
        "重复剔除": n_bad - len(d),
        "有效行数": len(d),
        "总销售额": float(d["销售额"].sum()),
    }
    return d, stats


def build_report(src: str | Path, dst: str | Path | None = None) -> dict:
    """清洗并写出四个工作表，返回清洗统计。"""
    src, dst = Path(src), Path(dst) if dst else Path(src).with_name("report.xlsx")
    if src.resolve() == dst.resolve():
        raise ReportError("输出路径不能与原始文件相同：不得修改原始文件")

    clean_df, stats = clean(read_raw(src))
    by_person = (clean_df.groupby("销售员", as_index=False)
                 .agg(销售额=("销售额", "sum"), 笔数=("销售额", "size"))
                 .sort_values("销售额", ascending=False))
    by_region = (clean_df.groupby("地区", as_index=False)
                 .agg(销售额=("销售额", "sum"), 笔数=("销售额", "size"))
                 .sort_values("销售额", ascending=False))
    monthly = (clean_df.assign(月份=clean_df["日期"].dt.strftime("%Y-%m"))
               .groupby("月份", as_index=False)["销售额"].sum())
    overview = pd.concat(
        [monthly, pd.DataFrame([{"月份": "合计", "销售额": monthly["销售额"].sum()}])],
        ignore_index=True,
    )

    with pd.ExcelWriter(dst, engine="openpyxl") as writer:
        clean_df.to_excel(writer, sheet_name=SHEETS[0], index=False)
        by_person.to_excel(writer, sheet_name=SHEETS[1], index=False)
        by_region.to_excel(writer, sheet_name=SHEETS[2], index=False)
        overview.to_excel(writer, sheet_name=SHEETS[3], index=False)
    return stats


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    src = Path(args[0]) if args else Path(__file__).with_name("sales_raw.xlsx")
    dst = Path(args[1]) if len(args) > 1 else src.with_name("report.xlsx")
    try:
        stats = build_report(src, dst)
    except ReportError as exc:
        print(f"[错误] {exc}")
        return 1
    print(f"原始 {stats['原始行数']} 行 → 有效 {stats['有效行数']} 行"
          f"（缺失 {stats['缺失剔除']} / 数量异常 {stats['数量异常剔除']} / 重复 {stats['重复剔除']}）")
    print(f"总销售额：{stats['总销售额']:.2f}")
    print(f"已生成 {dst}，含 {len(SHEETS)} 个工作表：{'、'.join(SHEETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
