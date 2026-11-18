# -*- coding: utf-8 -*-
"""实验 2 数据看板（基础部分）：校园超市销售数据静态看板。"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).parent / "data.csv"
MAIN, ACCENT, BG = "#1F6FEB", "#F59E0B", "#F5F7FA"   # 主色 / 辅助色 / 背景色
PALETTE = [MAIN, ACCENT, "#10B981", "#8B5CF6", "#EF4444"]


def load_data():
    """任务 2：读入 CSV，剔除空值、异常值与重复行，整理三个统计维度。"""
    raw = pd.read_csv(DATA, encoding="utf-8-sig")
    df = raw.copy()
    df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    for col in ("销售额", "订单数"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["日期", "品类", "校区", "销售额", "订单数"])
    df = df[(df["销售额"] > 0) & (df["销售额"] < 20000) & (df["订单数"] > 0)]
    df = df.drop_duplicates().sort_values("日期").reset_index(drop=True)
    df["月份"] = df["日期"].dt.strftime("%Y-%m")      # 时间维度
    return df, len(raw)                                # 品类/校区为分类维度，销售额/订单数为数值维度


def style(fig, legend=False):
    """统一图表的字体、配色、背景和边距，保证视觉一致。"""
    fig.update_layout(
        font=dict(family="Microsoft YaHei", size=12, color="#334155"),
        paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=legend, legend=dict(orientation="h", y=-0.15),
    )
    fig.update_xaxes(gridcolor="#EEF2F7")
    fig.update_yaxes(gridcolor="#EEF2F7")
    return fig


def main():
    st.set_page_config(page_title="校园超市销售数据看板", layout="wide")
    st.markdown(f"""<style>
        .stApp {{ background-color: {BG}; }}
        #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {{ visibility: hidden; }}
        .block-container {{ padding: 1.6rem 2.4rem 2.4rem; }}
        h1 {{ color: {MAIN}; font-size: 1.9rem; }}
        h2, h3 {{ color: #1E293B; font-size: 1.15rem; }}
        [data-testid="stMetric"] {{
            background: white; border-radius: 10px;
            padding: 14px 18px; box-shadow: 0 2px 8px #E6EBF2;
        }}
    </style>""", unsafe_allow_html=True)

    df, raw_n = load_data()
    st.title("校园超市销售数据看板")
    st.caption("业务场景：校园超市 2026 年 3—8 月销售监控　|　静态数据看板（实验 2 基础部分）")
    st.caption(f"数据预处理：原始 {raw_n} 行 → 有效 {len(df)} 行，剔除空值 / 异常值 / 重复行 {raw_n - len(df)} 行")

    # ① 数据概览区：数据卡片（总数、平均值、增长率）
    with st.container(border=True):
        st.subheader("① 数据概览")
        month_sum = df.groupby("月份")["销售额"].sum()
        growth = (month_sum.iloc[-1] / month_sum.iloc[-2] - 1) * 100
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("总销售额", f"¥{df['销售额'].sum():,.0f}", border=True)
        c2.metric("总订单数", f"{df['订单数'].sum():,.0f}", border=True)
        c3.metric("日均销售额", f"¥{df['销售额'].mean():,.0f}", border=True)
        c4.metric("销售额环比（8 月 / 7 月）", f"{growth:+.1f}%", border=True)

    # ② 维度统计区：柱状图（分类对比）+ 环形图（占比结构）
    with st.container(border=True):
        st.subheader("② 维度统计")
        left, right = st.columns(2)
        by_cat = df.groupby("品类", as_index=False)["销售额"].sum().sort_values("销售额", ascending=False)
        bar = px.bar(by_cat, x="品类", y="销售额", color="品类",
                     color_discrete_sequence=PALETTE, text_auto=".0f")
        left.plotly_chart(style(bar))
        by_campus = df.groupby("校区", as_index=False)["销售额"].sum()
        pie = px.pie(by_campus, names="校区", values="销售额", hole=0.45,
                     color_discrete_sequence=PALETTE)
        right.plotly_chart(style(pie, legend=True))

    # ③ 趋势分析区：折线图（时间变化趋势）
    with st.container(border=True):
        st.subheader("③ 趋势分析")
        trend = df.groupby("月份", as_index=False)["销售额"].sum()
        line = px.line(trend, x="月份", y="销售额", markers=True,
                       color_discrete_sequence=[MAIN])
        line.update_traces(line=dict(width=3), marker=dict(size=9))
        line.update_xaxes(type="category")            # 保持 2026-03 这类月份标签，不被转成英文月名
        st.plotly_chart(style(line))

    # ④ 明细数据区：数据表格
    with st.container(border=True):
        st.subheader("④ 明细数据")
        detail = df[["日期", "品类", "校区", "销售额", "订单数"]].copy().sort_values("日期", ascending=False)
        detail["日期"] = detail["日期"].dt.strftime("%Y-%m-%d")
        st.dataframe(detail, hide_index=True, height=300)


if __name__ == "__main__":
    import subprocess
    import sys
    from streamlit.runtime.scriptrunner import get_script_run_ctx

    if get_script_run_ctx(suppress_warning=True) is None:
        # 直接 python app.py 时没有网页服务上下文，自动改用 streamlit run 启动
        print("检测到直接运行本文件，已自动改用 streamlit run 启动网页服务…", flush=True)
        print("浏览器打开 http://localhost:8501；看完在 PyCharm 点 ■ 停止。", flush=True)
        raise SystemExit(subprocess.call(
            [sys.executable, "-m", "streamlit", "run", str(Path(__file__).resolve())]))
    main()
