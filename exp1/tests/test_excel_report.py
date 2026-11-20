"""考题一测试：正常用例 + 5 个异常/边界用例。"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd
import pytest
from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from excel_report import FIELDS, SHEETS, ReportError, build_report, clean, read_raw  # noqa: E402

RAW = Path(__file__).resolve().parents[1] / "sales_raw.xlsx"


def test_normal_report(tmp_path):
    """正常用例：四个 sheet 齐全，清洗与统计数值与人工核对一致，原始文件不变。"""
    before = hashlib.sha256(RAW.read_bytes()).hexdigest()
    out = tmp_path / "report.xlsx"
    stats = build_report(RAW, out)

    assert stats == {
        "原始行数": 19, "缺失剔除": 3, "数量异常剔除": 2,
        "重复剔除": 2, "有效行数": 12, "总销售额": 270.0,
    }
    book = pd.ExcelFile(out, engine="openpyxl")
    assert book.sheet_names == SHEETS

    detail = pd.read_excel(book, sheet_name="明细清洗后")
    assert len(detail) == 12
    assert detail["销售额"].sum() == 270
    assert (detail["数量"] > 0).all()
    assert not detail[FIELDS].duplicated().any()

    person = pd.read_excel(book, sheet_name="按销售员").set_index("销售员")["销售额"].to_dict()
    region = pd.read_excel(book, sheet_name="按地区").set_index("地区")["销售额"].to_dict()
    month = pd.read_excel(book, sheet_name="总览").set_index("月份")["销售额"].to_dict()
    assert person == {"李四": 110, "张三": 95, "王五": 65}
    assert region == {"华北": 100, "华南": 90, "华东": 80}
    assert month == {"2026-01": 55, "2026-02": 95, "2026-03": 120, "合计": 270}
    assert hashlib.sha256(RAW.read_bytes()).hexdigest() == before


@pytest.mark.parametrize("name, header, data, keyword", [
    ("文件不存在", None, None, "找不到原始文件"),
    ("空文件零字节", "empty", None, "空文件"),
    ("只有表头", FIELDS, [], "没有数据行"),
    ("缺列", ["日期", "销售员", "数量"], [["2026-01-01", "张三", 2]], "缺少必需字段"),
    ("清洗后无有效数据", FIELDS, [["2026-01-01", "张三", "笔记本", -1, 10, "华东"]], "没有有效数据"),
])
def test_abnormal_inputs(tmp_path, name, header, data, keyword):
    """异常用例：均抛中文可读错误，不出现 Traceback。"""
    path = tmp_path / f"{name}.xlsx"
    if header == "empty":
        path.write_bytes(b"")
    elif header is not None:
        wb = Workbook()
        ws = wb.active
        ws.append(header)
        for row in data:
            ws.append(row)
        wb.save(path)

    with pytest.raises(ReportError, match=keyword):
        build_report(path, tmp_path / "out.xlsx")


def test_refuse_overwrite(tmp_path):
    """边界用例：输出路径与原始文件相同时拒绝，保护原始文件。"""
    src = tmp_path / "raw.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(FIELDS)
    ws.append(["2026-01-01", "张三", "笔记本", 2, 10, "华东"])
    wb.save(src)
    before = hashlib.sha256(src.read_bytes()).hexdigest()

    with pytest.raises(ReportError, match="不得修改原始文件"):
        build_report(src, src)
    assert hashlib.sha256(src.read_bytes()).hexdigest() == before


def test_clean_helpers():
    """单元级：空字符串也算缺失，数量<=0 被剔除，重复行去重。"""
    df = pd.DataFrame([
        ["2026-01-01", "张三", "笔记本", 2, 10, "华东"],
        ["2026-01-01", "  ", "笔记本", 2, 10, "华东"],
        ["2026-01-02", "李四", "钢笔", 0, 5, "华南"],
        ["2026-01-01", "张三", "笔记本", 2, 10, "华东"],
    ], columns=FIELDS)
    cleaned, stats = clean(df)
    assert len(cleaned) == 1 and stats["总销售额"] == 20.0
    assert stats["缺失剔除"] == 1 and stats["数量异常剔除"] == 1 and stats["重复剔除"] == 1
