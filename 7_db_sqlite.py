"""
[7] DB/시스템 연동 — SQLite 매매일지

별도 서버 없이 'trades.db' 파일 하나로 DB 체험.
대시보드에서 매매 기록을 추가하면 즉시 DB에 저장되고 분석에 반영됨.
"""

import sqlite3
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = "trades.db"

st.set_page_config(page_title="매매일지 DB", layout="wide")
st.title("🗄️ DB 연동 — SQLite 매매일지")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            ticker TEXT NOT NULL,
            side TEXT NOT NULL,
            qty INTEGER NOT NULL,
            price INTEGER NOT NULL,
            fee INTEGER DEFAULT 0
        )
    """)
    return conn


def load_trades() -> pd.DataFrame:
    with get_conn() as conn:
        return pd.read_sql("SELECT * FROM trades ORDER BY date DESC", conn)


def insert_trade(d, ticker, side, qty, price, fee):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO trades(date,ticker,side,qty,price,fee) VALUES(?,?,?,?,?,?)",
            (d.isoformat(), ticker, side, qty, price, fee),
        )


with st.sidebar:
    st.header("➕ 매매 기록 추가")
    with st.form("add_trade", clear_on_submit=True):
        d = st.date_input("날짜", date.today())
        ticker = st.text_input("종목명", "삼성전자")
        side = st.selectbox("구분", ["매수", "매도"])
        qty = st.number_input("수량", min_value=1, value=10)
        price = st.number_input("단가", min_value=1, value=70000)
        fee = st.number_input("수수료", min_value=0, value=100)
        if st.form_submit_button("저장"):
            insert_trade(d, ticker, side, qty, price, fee)
            st.success("저장 완료")

    if st.button("🌱 샘플 데이터 넣기"):
        samples = [
            ("2026-04-01", "삼성전자", "매수", 10, 70000, 100),
            ("2026-04-10", "삼성전자", "매수", 5, 72000, 80),
            ("2026-04-20", "삼성전자", "매도", 8, 75000, 150),
            ("2026-04-05", "카카오", "매수", 20, 50000, 200),
            ("2026-04-25", "카카오", "매도", 10, 53000, 130),
            ("2026-02-05", "현대차", "매수", 5, 170000, 250),
            ("2026-03-10", "현대차", "매수", 3, 175000, 120),
            ("2026-01-15", "기아", "매수", 20, 90000, 180),
            ("2026-02-20", "기아", "매도", 15, 95000, 150),
        ]
        with get_conn() as conn:
            conn.executemany(
                "INSERT INTO trades(date,ticker,side,qty,price,fee) VALUES(?,?,?,?,?,?)",
                samples,
            )
        st.success("샘플 5건 추가")

df = load_trades()

if df.empty:
    st.info("왼쪽에서 매매를 입력하거나 '샘플 데이터 넣기'를 눌러보세요.")
    st.stop()

df["amount"] = df["qty"] * df["price"]
df["date"] = pd.to_datetime(df["date"])

st.subheader("📋 전체 매매 내역")
st.dataframe(df, hide_index=True, width='stretch')

st.subheader("📦 종목별 포지션")
pos_rows = []
for tk, g in df.groupby("ticker"):
    buy = g[g["side"] == "매수"]
    sell = g[g["side"] == "매도"]
    buy_qty = int(buy["qty"].sum())
    sell_qty = int(sell["qty"].sum())
    avg_buy = (buy["amount"].sum() / buy_qty) if buy_qty else 0
    realized = (sell["price"] * sell["qty"]).sum() - avg_buy * sell_qty - g["fee"].sum()
    pos_rows.append({
        "종목": tk,
        "보유수량": buy_qty - sell_qty,
        "평균매수단가": round(avg_buy, 0),
        "실현손익": round(realized, 0),
    })
st.dataframe(pd.DataFrame(pos_rows), hide_index=True, width='stretch')

st.subheader("📅 월별 매매 횟수")
monthly = df.groupby(df["date"].dt.to_period("M").astype(str)).size().reset_index(name="횟수")
monthly.columns = ["월", "횟수"]
fig = px.bar(monthly, x="월", y="횟수")
st.plotly_chart(fig, width='stretch')
