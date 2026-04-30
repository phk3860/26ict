"""
SQLite 매매일지 직접 조회 예제
5_db_sqlite.py 를 먼저 실행해 샘플 데이터를 만들고,
이 스크립트로 조회하면 된다.
"""

import sqlite3
import pandas as pd

DB_PATH = "trades.db"

# 1. 기본 연결 및 전체 조회
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM trades ORDER BY date DESC", conn)
print("=== 전체 매매 기록 ===")
print(df.to_string())
print()

# # 2. 종목별 요약
# print("=== 종목별 보유 포지션 ===")
# for ticker, group in df.groupby("ticker"):
#     buy = group[group["side"] == "매수"]
#     sell = group[group["side"] == "매도"]
#     buy_qty = int(buy["qty"].sum())
#     sell_qty = int(sell["qty"].sum())
#     holding = buy_qty - sell_qty
#     avg_buy = (buy["qty"] * buy["price"]).sum() / buy_qty if buy_qty else 0
#     print(f"{ticker}: 보유 {holding}주, 평균 매수가 {avg_buy:,.0f}원")
# print()

# # 3. 월별 거래 건수
# print("=== 월별 거래 건수 ===")
# df["year_month"] = pd.to_datetime(df["date"]).dt.to_period("M")
# monthly = df.groupby("year_month").size()
# print(monthly)

conn.close()
