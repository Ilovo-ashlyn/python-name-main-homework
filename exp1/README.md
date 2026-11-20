# 实验 1 · Python Vibe Coding 实操考核

两道考题的可运行工程：考题一（Excel 报表生成，必做）+ 考题二（FastAPI 记账接口，核心实现）。
环境：Python 3.10+（本机 `D:\pycharm\venv` 为 3.13.0）。

## 目录

```
exp1/
├── sales_raw.xlsx            原始样例数据（只读，任何脚本都不修改它）
├── excel_report.py          考题一：清洗 + 统计 + 输出四 sheet 报表
├── ledger_api.py            考题二：FastAPI 三接口 + 校验 + 并发保护
├── report.xlsx              运行考题一生成的报表结果
├── requirements.txt         依赖版本
├── README.md                本文件
├── run_output.png           测试与脚本运行结果截图
├── tests/
│   ├── test_excel_report.py 考题一：1 正常 + 5 异常 + 2 边界
│   └── test_ledger_api.py   考题二：1 正常 + 7 POST 异常 + 7 查询异常 + 并发
└── ai_logs/
    ├── 需求澄清.md          交付物 1（初稿，待本人补充）
    ├── 复盘.md              交付物 5（初稿，待本人补充）
    └── 协作记录.md          交付物 4：对话摘要 + diff（初稿，待本人补充）
```

## 安装与运行

```bash
pip install -r requirements.txt
```

**考题一**（在 `exp1/` 目录下）：

```bash
python excel_report.py                  # 读 sales_raw.xlsx → 生成 report.xlsx
python excel_report.py 其他.xlsx 输出.xlsx   # 也可指定路径
```

**考题二**：

```bash
uvicorn ledger_api:app --reload        # 打开 http://localhost:8000/docs 看交互文档
```

**测试**（交付物 3）：

```bash
pytest -q                              # 全部 24 个用例
pytest tests/test_excel_report.py -q   # 考题一 8 个
pytest tests/test_ledger_api.py -q    # 考题二 16 个
```

`httpx` 仅供 `TestClient` 使用；运行 pytest 时 Starlette 会提示 `httpx` 将被 `httpx2` 取代，这是无害的弃用告警，本次按约定不引入额外依赖。

## 考题一：清洗规则与报表口径

| 步骤 | 规则 | 本样例结果 |
|---|---|---|
| 读入校验 | 文件不存在 / 0 字节 / 只有表头 / 缺少必需字段 / 文件损坏 → 中文可读报错，不抛 Traceback | — |
| 删缺失 | 六个字段任一为空（含纯空白）即删除该行 | 剔除 3 行 |
| 剔异常 | 数量 ≤ 0 删除；数量、单价无法转数字也视为缺失 | 剔除 2 行 |
| 全字段去重 | 六个字段完全相同的行只保留第一条 | 剔除 2 行 |
| 销售额 | 数量 × 单价 | 12 行合计 270.00 |

四个工作表：`明细清洗后`（12 行，含销售额列）、`按销售员`（李四 110 / 张三 95 / 王五 65）、`按地区`（华北 100 / 华南 90 / 华东 80）、`总览`（月度 55 / 95 / 120 + 合计 270）。三张汇总表之和均等于 270，便于人工核对。

**不修改原始文件**：全程只读；`build_report` 在输出路径解析后与输入路径相同时直接报「不得修改原始文件」。测试 `test_normal_report` 与 `test_refuse_overwrite` 都用 SHA-256 验证了 `sales_raw.xlsx` 未被改动。

异常输入的实测表现：

| 输入 | 结果 |
|---|---|
| 路径不存在 | `[错误] 找不到原始文件：…` |
| 0 字节文件 | `[错误] 原始文件是空文件（0 字节）：…` |
| 只有表头 | `[错误] 原始文件没有数据行（只有表头），无法生成报表` |
| 缺少「单价」等列 | `[错误] 原始文件缺少必需字段：…` |
| 清洗后无有效数据 | `[错误] 清洗后没有有效数据：可能全是缺失值、数量<=0 或重复行` |

## 考题二：接口说明

| 接口 | 参数 | 返回 |
|---|---|---|
| `POST /records` | `amount`（>0）、`type`（收入/支出）、`category`（非空）、`date`（YYYY-MM-DD） | `201` + 含自增 `id` 的记录 |
| `GET /records` | `type`、`category`、`date_from`、`date_to`、`page`（≥1）、`page_size`（1~100） | `{total, page, page_size, items}` |
| `GET /summary` | `date_from`、`date_to` | `{income, expense, balance, date_from, date_to}` |

校验：POST 由 Pydantic 校验，金额≤0、非法类型、非法日期、分类空白、缺字段一律 `422` + 结构化 `detail`；查询参数非法由业务代码返回 `422` + `{detail: {code, message}}`（`INVALID_TYPE` / `INVALID_DATE` / `INVALID_RANGE`），分页越界由 FastAPI 返回 `422`。所有异常请求都不会写入数据。

**并发写入如何保证**：内存列表 `_records` 与自增 `_next_id` 全部在同一把 `threading.Lock` 内读写；`GET` 也在锁内做一次快照拷贝后再过滤，避免遍历时被并发修改。`tests/test_ledger_api.py::test_concurrent_writes` 用 8 线程写 16 条，断言 id 连续且不重复、总数不丢失。说明：本实现是单进程内存存储，多进程/重启后数据不持久化——这是题目允许的「内存存储」取舍，已在复盘里列为风险。

## 验收对照

- 一键运行生成正确报表：`python excel_report.py` ✅
- 统计数值与人工核对一致：三张汇总表之和均为 270 ✅
- 异常输入不崩溃且有可读提示：5 类异常均有中文报错 ✅
- 接口可启动并正常调用：`uvicorn ledger_api:app` 真实启动后，用 HTTP 请求验证 POST 201 / GET 200 / summary 100-30=70、非法参数 422、`/openapi.json` 200 ✅
- pytest 覆盖核心用例：`24 passed` ✅
- 不得修改原始文件：SHA-256 前后一致 ✅
- 结果截图：`run_output.png` ✅
