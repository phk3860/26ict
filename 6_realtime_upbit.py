"""
[6] 실시간 데이터 — 업비트 WebSocket

설치: pip install websocket-client
인증 불필요. 코인 시세를 초 단위로 받아 화면에 표시.
주식 실시간(KIS, 키움)도 원리는 동일.
[참고] https://docs.upbit.com/kr/docs/websocket-best-practice
"""

import json
import threading
import time
import uuid
from collections import defaultdict

import streamlit as st
import websocket

st.set_page_config(page_title="실시간 시세", layout="wide")
st.title("⚡ 실시간 — 업비트 WebSocket")

MARKETS = ["KRW-BTC", "KRW-ETH", "KRW-XRP", "KRW-SOL", "KRW-DOGE"]

# WebSocket이 최신 가격만 계속 덮어씀
TICKER_DATA: dict = defaultdict(dict)
WORKER_STARTED = False
WORKER_LOCK = threading.Lock()


def run_ws(markets):
    def on_message(ws, message):
        data = json.loads(message)
        code = data.get("code")
        if not code:
            return
        TICKER_DATA[code] = {
            "price": data.get("trade_price"),
            "change_rate": data.get("signed_change_rate", 0) * 100,
        }

    def on_open(ws):
        sub = [
            {"ticket": str(uuid.uuid4())},
            {"type": "ticker", "codes": markets},
        ]
        ws.send(json.dumps(sub))

    ws = websocket.WebSocketApp(
        "wss://api.upbit.com/websocket/v1",
        on_open=on_open,
        on_message=on_message,
    )
    ws.run_forever()


picked = st.multiselect("종목", MARKETS, default=["KRW-BTC", "KRW-ETH", "KRW-XRP", "KRW-SOL", "KRW-DOGE"])

col1, col2 = st.columns([1, 5])
if col1.button("▶ 시작") and picked:
    with WORKER_LOCK:
        if not WORKER_STARTED:
            t = threading.Thread(target=run_ws, args=(MARKETS,), daemon=True)
            t.start()
            WORKER_STARTED = True
    col2.success(f"수신 중: {', '.join(picked)}")

placeholder = st.empty()

if picked:
    # 메인 루프에서 직전 스냅샷 관리 (1초마다 비교)
    prev_snapshot: dict = {}

    while True:
        with placeholder.container():
            cols = st.columns(len(picked))
            for col, code in zip(cols, picked):
                d = TICKER_DATA.get(code, {})
                price = d.get("price")
                rate = d.get("change_rate", 0)

                if price is None:
                    col.metric(code, "로딩 중...")
                else:
                    # 1초 전 스냅샷과 비교
                    prev_price = prev_snapshot.get(code)
                    delta = int(price - prev_price) if prev_price is not None else 0

                    if delta > 0:
                        arrow = "📈"
                    elif delta < 0:
                        arrow = "📉"
                    else:
                        arrow = "➡️"

                    col.metric(
                        f"{arrow} {code}",
                        f"{price:,.0f}",
                        delta=delta if prev_price is not None else None,
                    )
                    col.caption(f"변동률: {rate:+.2f}%")

            # 이번 루프의 가격을 다음 루프의 prev_snapshot 으로 저장
            for code in picked:
                d = TICKER_DATA.get(code, {})
                if d.get("price") is not None:
                    prev_snapshot[code] = d["price"]

        time.sleep(1)
