"""
[4] 크롤링 — 네이버 금융 종목 뉴스

⚠️ 학습 목적. 과도한 요청 금지, 상업적 이용 금지.
robots.txt 와 이용약관 확인 필수.(https://finance.naver.com/robots.txt)

삼성전자 여기 가져올 거임
https://finance.naver.com/item/news.naver?code=005930
"""

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(page_title="종목 뉴스 크롤링", layout="wide")
st.title("🕷️ 크롤링 — 네이버 금융 종목 뉴스")

st.caption("학습 목적의 예제입니다. User-Agent / Referer 설정 등 매너를 지키세요.")

code = st.text_input("종목코드", value="005930", help="예: 삼성전자 005930")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
}


@st.cache_data(ttl=300)
def fetch_news(code: str, limit: int = 10) -> pd.DataFrame:
    # 종목 뉴스는 news.naver 페이지의 iframe(news_news.naver)에 실제로 들어있다.
    url = f"https://finance.naver.com/item/news_news.naver?code={code}&page=&clusterId="
    headers = {**HEADERS, "Referer": f"https://finance.naver.com/item/news.naver?code={code}"}
    r = requests.get(url, headers=headers, timeout=10)
    r.encoding = "euc-kr"
    soup = BeautifulSoup(r.text, "html.parser")

    rows = []
    for tr in soup.select("table.type5 tr"):
        title_a = tr.select_one("td.title a")
        info = tr.select_one("td.info")
        dt = tr.select_one("td.date")
        if not (title_a and info and dt):
            continue
        href = title_a.get("href", "")
        link = f"https://finance.naver.com{href}" if href.startswith("/") else href
        rows.append({
            "제목": title_a.get_text(strip=True),
            "정보제공": info.get_text(strip=True),
            "날짜": dt.get_text(strip=True),
            "링크": link,
        })

    df = pd.DataFrame(rows).drop_duplicates(subset=["제목"]).reset_index(drop=True)
    return df.head(limit)


if st.button("최신 뉴스 10개 가져오기"):
    with st.spinner("크롤링 중..."):
        df = fetch_news(code, limit=10)
    if df.empty:
        st.warning("뉴스를 찾지 못했습니다. 종목코드를 확인하세요.")
    else:
        st.success(f"{len(df)}건 수집")
        st.dataframe(
            df,
            column_config={"링크": st.column_config.LinkColumn("원문")},
            hide_index=True,
            width='stretch',
        )
