"""
[1] 파일 기반 — KRX 일별시세 CSV 분석

준비:
1) http://data.krx.co.kr/ 접속
2) [기본통계] → [주식] → [종목시세] → [전종목 시세]
3) 날짜 선택 후 'CSV' 버튼 클릭
4) 받은 파일을 이 스크립트와 같은 폴더에 'krx.csv'로 저장
"""

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="KRX 전종목 시세", layout="wide")
st.title("📁 파일 기반 — KRX 전종목 시세")

uploaded = st.file_uploader("KRX에서 받은 CSV 업로드", type=["csv"])
path = uploaded if uploaded is not None else "krx.csv"

try:
    df = pd.read_csv(path, encoding="cp949")
except (FileNotFoundError, UnicodeDecodeError):
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except FileNotFoundError:
        st.warning("krx.csv 파일을 같은 폴더에 두거나 위에서 업로드하세요.")
        st.stop()

st.caption(f"총 {len(df):,}개 종목 · 컬럼: {', '.join(df.columns)}")

if "시장구분" in df.columns:
    market = st.selectbox("시장 선택", ["전체"] + sorted(df["시장구분"].dropna().unique().tolist()))
    if market != "전체":
        df = df[df["시장구분"] == market]

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 등락률 상위 10")
    if "등락률" in df.columns:
        top = df.nlargest(10, "등락률")[["종목명", "종가", "등락률"]]
        fig = px.bar(top, x="등락률", y="종목명", orientation="h", text="등락률")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width='stretch')

with col2:
    st.subheader("💰 거래대금 상위 10")
    if "거래대금" in df.columns:
        top = df.nlargest(10, "거래대금")[["종목명", "종가", "거래대금"]]
        st.dataframe(top, width='stretch', hide_index=True)

st.subheader("🔍 전체 데이터")
st.dataframe(df, width='stretch', height=400)
