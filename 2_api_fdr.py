"""
[2] API 기반 — FinanceDataReader

설치: pip install finance-datareader
키 발급 불필요. 한 줄 호출로 한국/미국 주식 시세 수집.
"""

from datetime import date, timedelta

import FinanceDataReader as fdr
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="시세 비교", layout="wide")
st.title("🌐 API 기반 — FinanceDataReader 시세 비교")

PRESETS = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "카카오": "035720",
    "네이버": "035420",
    "현대차": "005380",
    "LG에너지솔루션": "373220",
}

picked = st.multiselect("종목 선택", list(PRESETS.keys()), default=["삼성전자", "SK하이닉스", "카카오"])
end = st.date_input("종료일", date.today())
start = st.date_input("시작일", end - timedelta(days=365))

if not picked:
    st.info("종목을 1개 이상 선택하세요.")
    st.stop()

frames = []
metrics = []
for name in picked:
    code = PRESETS[name]
    df = fdr.DataReader(code, start, end)
    if df.empty:
        continue
    df = df.reset_index()[["Date", "Close"]].rename(columns={"Close": "종가"})
    df["종목"] = name
    df["기준가대비"] = df["종가"] / df["종가"].iloc[0] * 100
    frames.append(df)
    metrics.append({
        "종목": name,
        "현재가": int(df["종가"].iloc[-1]),
        "최고가": int(df["종가"].max()),
        "최저가": int(df["종가"].min()),
        "수익률(%)": round((df["종가"].iloc[-1] / df["종가"].iloc[0] - 1) * 100, 2),
    })

if not frames:
    st.warning("데이터가 없습니다.")
    st.stop()

st.subheader("📊 종목별 요약")
cols = st.columns(len(metrics))
for col, m in zip(cols, metrics):
    col.metric(m["종목"], f"{m['현재가']:,}원", f"{m['수익률(%)']}%")

merged = pd.concat(frames)
st.subheader("📈 정규화 수익률 (시작일=100)")
fig = px.line(merged, x="Date", y="기준가대비", color="종목")
st.plotly_chart(fig, width='stretch')

st.subheader("📋 상세")
st.dataframe(pd.DataFrame(metrics), hide_index=True, width='stretch')
