"""
[3] API 기반 — 기상청 단기예보

공공데이터포털 기상청 단기예보 조회서비스
인증키 필요 (data.go.kr 회원가입 후 발급)
"공공데이터포털에서 API 키 한 번 발급하면 이런 데이터를 무료로 실시간으로 가져올 수 있습니다" — 기상청,
  교통, 부동산 등 수백 개 API가 같은 방식으로 작동함
"""

import os
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(".env.local")

st.set_page_config(page_title="기상청 단기예보", layout="wide")
st.title("🌤️ API 기반 — 기상청 단기예보")

API_KEY = os.getenv("WEATHER_API_KEY", "")
XLSX_PATH = "weather/기상청41_단기예보 조회서비스_오픈API활용가이드_격자_위경도(2510).xlsx"

CATEGORY_INFO = {
    "TMP":  ("기온",       "°C"),
    "REH":  ("습도",       "%"),
    "POP":  ("강수확률",   "%"),
    "PTY":  ("강수형태",   ""),
    "PCP":  ("강수량",     "mm"),
    "WSD":  ("풍속",       "m/s"),
    "SKY":  ("하늘상태",   ""),
    "TMX":  ("최고기온",   "°C"),
    "TMN":  ("최저기온",   "°C"),
}

PTY_LABEL = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}
SKY_LABEL = {"1": "☀️ 맑음", "3": "⛅ 구름많음", "4": "☁️ 흐림"}


@st.cache_data
def load_grid():
    df = pd.read_excel(XLSX_PATH)
    df.columns = ["국가", "코드", "시도", "시군구", "읍면동",
                  "nx", "ny", "격x도", "격x분", "격x초",
                  "격y도", "격y분", "격y초", "경도", "위도", "비고"]
    df = df.dropna(subset=["nx", "ny"])
    df["nx"] = df["nx"].astype(int)
    df["ny"] = df["ny"].astype(int)
    return df


def get_base_time():
    """가장 최근 발표 시각 반환 (발표 후 10분 이상 지난 것)"""
    now = datetime.now() - timedelta(minutes=10)
    hours = [2, 5, 8, 11, 14, 17, 20, 23]
    # 현재 시각보다 작거나 같은 발표 시각 중 가장 큰 것
    valid = [h for h in hours if now.hour >= h]
    if valid:
        return now.strftime("%Y%m%d"), f"{max(valid):02d}00"
    # 자정 이전 (0~1시): 전날 23시 발표본 사용
    return (now - timedelta(days=1)).strftime("%Y%m%d"), "2300"


@st.cache_data(ttl=600)
def fetch_forecast(nx, ny, base_date, base_time):
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    params = {
        "serviceKey": API_KEY,
        "numOfRows": 300,
        "pageNo": 1,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny,
    }
    r = requests.get(url, params=params, timeout=10)
    items = r.json()["response"]["body"]["items"]["item"]
    df = pd.DataFrame(items)
    df["datetime"] = pd.to_datetime(df["fcstDate"] + df["fcstTime"], format="%Y%m%d%H%M")
    return df


# ─── 사이드바: 지역 선택 ─────────────────────────────
grid_df = load_grid()

with st.sidebar:
    st.header("📍 지역 선택")
    sido_list = sorted(grid_df["시도"].dropna().unique())
    sido = st.selectbox("시/도", sido_list, index=sido_list.index("서울특별시") if "서울특별시" in sido_list else 0)

    sigungu_list = sorted(grid_df[grid_df["시도"] == sido]["시군구"].dropna().unique())
    sigungu = st.selectbox("시/군/구", ["전체"] + sigungu_list)

    if sigungu == "전체":
        row = grid_df[grid_df["시도"] == sido].iloc[0]
    else:
        row = grid_df[(grid_df["시도"] == sido) & (grid_df["시군구"] == sigungu)].iloc[0]

    nx, ny = int(row["nx"]), int(row["ny"])
    st.caption(f"격자좌표: nx={nx}, ny={ny}")

# ─── 데이터 호출 ─────────────────────────────────────
base_date, base_time = get_base_time()
st.caption(f"발표기준: {base_date} {base_time} | 지역: {sido} {sigungu}")

with st.spinner("기상청 API 호출 중..."):
    df = fetch_forecast(nx, ny, base_date, base_time)

# ─── 현재 시각 기준 가장 가까운 예보 ─────────────────
now_str = datetime.now().strftime("%Y%m%d%H%M")
nearest = df[df["fcstDate"] + df["fcstTime"] >= now_str]

def get_val(df_near, cat):
    row = df_near[df_near["category"] == cat]
    return row["fcstValue"].values[0] if not row.empty else "-"

st.subheader("📊 현재 날씨")
cols = st.columns(5)
tmp  = get_val(nearest, "TMP")
reh  = get_val(nearest, "REH")
pop  = get_val(nearest, "POP")
pty  = PTY_LABEL.get(get_val(nearest, "PTY"), "-")
sky  = SKY_LABEL.get(get_val(nearest, "SKY"), "-")
wsd  = get_val(nearest, "WSD")

cols[0].metric("🌡️ 기온",     f"{tmp} °C")
cols[1].metric("💧 습도",     f"{reh} %")
cols[2].metric("☔ 강수확률", f"{pop} %")
cols[3].metric("🌂 강수형태", pty)
cols[4].metric("💨 풍속",     f"{wsd} m/s")
st.info(f"하늘 상태: {sky}")

# ─── 시간대별 기온 변화 ───────────────────────────────
st.subheader("📈 시간대별 기온 예보")
tmp_df = df[df["category"] == "TMP"].copy()
tmp_df["기온(°C)"] = pd.to_numeric(tmp_df["fcstValue"])
tmp_df = tmp_df.sort_values("datetime").head(24)

import plotly.express as px
fig = px.line(tmp_df, x="datetime", y="기온(°C)", markers=True)
fig.update_layout(xaxis_title="시각", yaxis_title="기온 (°C)")
st.plotly_chart(fig, width='stretch')

# ─── 시간대별 강수확률 ────────────────────────────────
st.subheader("☔ 시간대별 강수확률")
pop_df = df[df["category"] == "POP"].copy()
pop_df["강수확률(%)"] = pd.to_numeric(pop_df["fcstValue"])
pop_df = pop_df.sort_values("datetime").head(24)

fig2 = px.bar(pop_df, x="datetime", y="강수확률(%)", color_discrete_sequence=["#4a9edd"])
fig2.update_layout(xaxis_title="시각", yaxis_title="강수확률 (%)", yaxis_range=[0, 100])
st.plotly_chart(fig2, width='stretch')

# ─── 전체 예보 원본 ───────────────────────────────────
with st.expander("📋 전체 예보 데이터 보기"):
    pivot = df.pivot_table(index="datetime", columns="category", values="fcstValue", aggfunc="first")
    pivot = pivot.rename(columns={k: f"{k}({v[0]})" for k, v in CATEGORY_INFO.items() if k in pivot.columns})
    st.dataframe(pivot.sort_index(), width='stretch')
