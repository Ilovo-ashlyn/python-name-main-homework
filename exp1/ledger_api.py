"""考题二核心：FastAPI 简易记账接口（内存存储 + 线程锁）。

启动：uvicorn ledger_api:app --reload
测试：pytest tests/test_ledger_api.py -q
"""

from __future__ import annotations

import threading
from datetime import date
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="简易记账接口", version="1.0")

_lock = threading.Lock()
_records: list[dict] = []
_next_id = 1

TYPES = ("收入", "支出")


def error(status: int, code: str, message: str) -> HTTPException:
    """统一的 4xx 结构化错误。"""
    return HTTPException(status_code=status, detail={"code": code, "message": message})


class RecordIn(BaseModel):
    amount: float = Field(gt=0, description="金额，必须 > 0")
    type: Literal["收入", "支出"]
    category: str = Field(min_length=1, max_length=20)
    day: date = Field(alias="date", description="日期 YYYY-MM-DD")

    @field_validator("category")
    @classmethod
    def category_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("分类不能是空白字符")
        return v.strip()


def parse_day(value: str | None, field: str) -> date | None:
    """把查询参数里的日期字符串转成 date，格式非法直接 422。"""
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise error(422, "INVALID_DATE", f"{field} 必须是 YYYY-MM-DD 格式，收到：{value!r}")


@app.post("/records", status_code=201)
def add_record(rec: RecordIn) -> dict:
    with _lock:
        global _next_id
        item = {"id": _next_id, **rec.model_dump(by_alias=True)}
        _next_id += 1
        _records.append(item)
        return item


@app.get("/records")
def list_records(
    type: str | None = Query(None, description="收入 / 支出"),
    category: str | None = Query(None),
    date_from: str | None = Query(None, description="YYYY-MM-DD，含当天"),
    date_to: str | None = Query(None, description="YYYY-MM-DD，含当天"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> dict:
    if type is not None and type not in TYPES:
        raise error(422, "INVALID_TYPE", f"type 只能是 {' / '.join(TYPES)}，收到：{type!r}")
    start, end = parse_day(date_from, "date_from"), parse_day(date_to, "date_to")
    if start and end and start > end:
        raise error(422, "INVALID_RANGE", "date_from 不能晚于 date_to")

    def match(r: dict) -> bool:
        d = date.fromisoformat(r["date"]) if isinstance(r["date"], str) else r["date"]
        return (type is None or r["type"] == type) \
            and (category is None or r["category"] == category) \
            and (start is None or d >= start) \
            and (end is None or d <= end)

    with _lock:
        hits = [r.copy() for r in _records if match(r)]
    total = len(hits)
    return {
        "total": total, "page": page, "page_size": page_size,
        "items": hits[(page - 1) * page_size: page * page_size],
    }


@app.get("/summary")
def summary(
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
) -> dict:
    start, end = parse_day(date_from, "date_from"), parse_day(date_to, "date_to")
    if start and end and start > end:
        raise error(422, "INVALID_RANGE", "date_from 不能晚于 date_to")

    def match(r: dict) -> bool:
        d = date.fromisoformat(r["date"]) if isinstance(r["date"], str) else r["date"]
        return (start is None or d >= start) and (end is None or d <= end)

    with _lock:
        hits = [r for r in _records if match(r)]
    income = sum(r["amount"] for r in hits if r["type"] == "收入")
    expense = sum(r["amount"] for r in hits if r["type"] == "支出")
    return {
        "date_from": date_from, "date_to": date_to,
        "income": round(income, 2), "expense": round(expense, 2),
        "balance": round(income - expense, 2),
    }
