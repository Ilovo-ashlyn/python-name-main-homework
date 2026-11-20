"""考题二测试：正常用例 + 8 个异常/边界用例。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ledger_api  # noqa: E402


@pytest.fixture()
def client():
    """每个用例重置内存数据，保证互不干扰。"""
    with ledger_api._lock:
        ledger_api._records.clear()
        ledger_api._next_id = 1
    return TestClient(ledger_api.app)


def post(c, amount, type_, category, day):
    return c.post("/records", json={
        "amount": amount, "type": type_, "category": category, "date": day,
    })


def seed(c):
    for row in [
        (100, "收入", "工资", "2026-01-05"),
        (30, "支出", "餐饮", "2026-01-06"),
        (50, "收入", "兼职", "2026-02-01"),
        (20, "支出", "餐饮", "2026-02-03"),
    ]:
        assert post(c, *row).status_code == 201


def test_normal_crud_and_summary(client):
    """正常用例：新增、筛选、分页、区间汇总、id 连续。"""
    seed(client)
    all_rows = client.get("/records").json()
    assert all_rows["total"] == 4
    assert [r["id"] for r in all_rows["items"]] == [1, 2, 3, 4]

    income = client.get("/records", params={"type": "收入"}).json()
    assert income["total"] == 2 and {r["category"] for r in income["items"]} == {"工资", "兼职"}

    catering = client.get("/records", params={"category": "餐饮"}).json()
    assert catering["total"] == 2

    ranged = client.get("/records", params={"date_from": "2026-02-01", "date_to": "2026-02-28"}).json()
    assert ranged["total"] == 2

    page2 = client.get("/records", params={"page": 2, "page_size": 2}).json()
    assert page2["total"] == 4 and [r["id"] for r in page2["items"]] == [3, 4]

    summary = client.get("/summary", params={
        "date_from": "2026-01-01", "date_to": "2026-01-31",
    }).json()
    assert summary == {
        "date_from": "2026-01-01", "date_to": "2026-01-31",
        "income": 100.0, "expense": 30.0, "balance": 70.0,
    }
    assert client.get("/summary").json()["balance"] == 100.0


@pytest.mark.parametrize("body, field", [
    ({"amount": 0, "type": "收入", "category": "工资", "date": "2026-01-01"}, "amount"),
    ({"amount": -5, "type": "收入", "category": "工资", "date": "2026-01-01"}, "amount"),
    ({"amount": 10, "type": "转账", "category": "工资", "date": "2026-01-01"}, "type"),
    ({"amount": 10, "type": "收入", "category": "工资", "date": "2026-13-45"}, "date"),
    ({"amount": 10, "type": "收入", "category": "工资", "date": "01/02/2026"}, "date"),
    ({"amount": 10, "type": "收入", "category": "  ", "date": "2026-01-01"}, "category"),
    ({"amount": 10, "type": "收入", "date": "2026-01-01"}, "category"),
])
def test_invalid_post(client, body, field):
    """异常用例：金额、类型、日期、分类、缺字段均返回 422 且未写入数据。"""
    r = client.post("/records", json=body)
    assert r.status_code == 422
    assert "detail" in r.json()
    assert client.get("/records").json()["total"] == 0


@pytest.mark.parametrize("path, params, code", [
    ("/records", {"type": "无效类型"}, "INVALID_TYPE"),
    ("/records", {"date_from": "bad"}, "INVALID_DATE"),
    ("/records", {"date_from": "2026-02-01", "date_to": "2026-01-01"}, "INVALID_RANGE"),
    ("/records", {"page": 0}, None),
    ("/records", {"page_size": 101}, None),
    ("/summary", {"date_from": "2026-99-99"}, "INVALID_DATE"),
    ("/summary", {"date_from": "2026-02-01", "date_to": "2026-01-01"}, "INVALID_RANGE"),
])
def test_invalid_query(client, path, params, code):
    """异常用例：非法查询参数一律 4xx，自定义错误带业务 code。"""
    r = client.get(path, params=params)
    assert 400 <= r.status_code < 500
    if code:
        assert r.json()["detail"]["code"] == code


def test_concurrent_writes(client):
    """并发写入：16 个线程各写 1 条，id 不重复、数据不丢失。"""
    from concurrent.futures import ThreadPoolExecutor

    def one(i):
        return post(client, 1, "收入", "并发", "2026-01-01").status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        codes = list(pool.map(one, range(16)))
    assert codes == [201] * 16
    rows = client.get("/records", params={"page_size": 100}).json()
    ids = [r["id"] for r in rows["items"]]
    assert rows["total"] == 16 and len(set(ids)) == 16 and ids == list(range(1, 17))
