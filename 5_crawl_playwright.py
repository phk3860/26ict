"""
[5] 크롤링 — Playwright (브라우저 기반)

requests+BeautifulSoup과의 차이:
- 실제 브라우저(Chromium)를 띄워 JS 렌더링된 페이지도 긁을 수 있음
- 로그인, 클릭, 스크롤 등 사용자 동작을 코드로 재현 가능
- 속도는 느리지만 막혀있는 사이트도 대부분 통과

설치:
  pip install playwright
  playwright install chromium

⚠️ 학습 목적. 이용약관 및 robots.txt 확인 필수.
"""

import concurrent.futures
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Playwright 크롤링", layout="wide")
st.title("🎭 크롤링 (Playwright) — 네이버 금융 뉴스")

st.caption("실제 브라우저(Chromium)로 페이지를 열어 크롤링합니다.")

with st.expander("📌 requests vs Playwright 차이점"):
    st.markdown("""
    | | requests + BeautifulSoup | Playwright |
    |---|---|---|
    | 방식 | HTML만 가져옴 | 실제 브라우저 실행 |
    | JS 렌더링 | ❌ 안됨 | ✅ 됨 |
    | 속도 | 빠름 | 느림 (브라우저 구동) |
    | 로그인/클릭 | 어려움 | 쉬움 |
    | 사용 난이도 | 쉬움 | 중간 |
    """)

# playwright 설치 확인
try:
    from playwright.sync_api import sync_playwright
    _playwright_ok = True
except ImportError:
    _playwright_ok = False

if not _playwright_ok:
    st.error(
        "playwright 패키지가 설치되지 않았습니다.\n\n"
        "터미널에서 아래 두 명령을 순서대로 실행하세요:\n"
        "```\npip install playwright\nplaywright install chromium\n```"
    )
    st.stop()

code = st.text_input("종목코드", value="005930", help="예: 삼성전자 005930")

col1, col2 = st.columns([1, 2])
headless = col1.toggle("브라우저 숨기기 (headless)", value=False,
                       help="끄면 실제 브라우저 창이 열려서 동작을 볼 수 있음")
slow_mo = col2.slider(
    "동작 속도 (slow_mo ms)",
    min_value=0, max_value=2000, value=700, step=100,
    disabled=headless,
    help="브라우저가 보일 때만 적용. 값이 클수록 각 동작 사이 딜레이가 길어져 천천히 움직입니다.",
)


def _crawl(code: str, headless: bool, slow_mo: int):
    """별도 스레드에서 실행 — Streamlit 이벤트 루프와 충돌 방지."""
    import asyncio
    # Windows: 스레드 내 subprocess 지원을 위해 ProactorEventLoop 필요
    if hasattr(asyncio, "WindowsProactorEventLoopPolicy"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    from playwright.sync_api import sync_playwright

    # 숨기기 모드에서는 slow_mo 의미 없으므로 0으로 고정
    effective_slow_mo = 0 if headless else slow_mo

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=effective_slow_mo)
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                "Referer": f"https://finance.naver.com/item/news.naver?code={code}",
            })

            url = f"https://finance.naver.com/item/news_news.naver?code={code}&page=&clusterId="
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_selector("table.type5", timeout=10_000)

            # 브라우저가 보일 때: 스크롤로 데이터 수집 동작을 시각적으로 보여줌
            if not headless:
                page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
                page.wait_for_timeout(400)
                page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })")
                page.wait_for_timeout(600)
                page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
                page.wait_for_timeout(400)

            rows = []
            for tr in page.locator("table.type5 tr").all():
                title_el = tr.locator("td.title a")
                if title_el.count() == 0:
                    continue
                info_el = tr.locator("td.info")
                date_el = tr.locator("td.date")
                href = title_el.first.get_attribute("href") or ""
                rows.append({
                    "제목": title_el.first.inner_text().strip(),
                    "정보제공": info_el.first.inner_text().strip() if info_el.count() > 0 else "",
                    "날짜": date_el.first.inner_text().strip() if date_el.count() > 0 else "",
                    "링크": f"https://finance.naver.com{href}" if href.startswith("/") else href,
                })

            # 브라우저가 보일 때: 수집 완료 후 잠깐 멈춰서 결과를 볼 수 있게
            if not headless:
                page.wait_for_timeout(1500)

        finally:
            browser.close()

    df = pd.DataFrame(rows).drop_duplicates(subset=["제목"]).reset_index(drop=True)
    return df.head(10)


if st.button("🎭 Playwright로 뉴스 가져오기"):
    timeout = 60 if not headless else 30
    with st.spinner("브라우저 실행 중... (최초 실행은 5~10초 소요)"):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(_crawl, code, headless, slow_mo)
                df = future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            st.error("시간 초과입니다. 네트워크 상태를 확인하세요.")
            st.stop()
        except Exception as e:
            if "Executable doesn't exist" in str(e) or "chromium" in str(e).lower():
                st.error(
                    "Chromium 브라우저가 설치되지 않았습니다.\n\n"
                    "터미널에서 실행하세요:\n```\nplaywright install chromium\n```"
                )
            else:
                st.error(f"오류: {e}")
            st.stop()

    if df.empty:
        st.warning("뉴스를 찾지 못했습니다. 종목코드를 확인하세요.")
    else:
        st.success(f"{len(df)}건 수집")
        st.dataframe(
            df,
            column_config={"링크": st.column_config.LinkColumn("원문")},
            hide_index=True,
            width="stretch",
        )
