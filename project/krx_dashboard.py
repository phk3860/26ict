import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정 및 테마 적용
st.set_page_config(
    page_title="KRX 주식 시세 분석 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS로 디자인 강화
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1 {
        color: #1e3a8a;
        font-weight: 800;
    }
    h2, h3 {
        color: #334155;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 KRX 전종목 시세 분석 대시보드")
st.markdown("KRX(한국거래소)에서 다운로드한 CSV 파일을 업로드하여 시장 현황을 한눈에 파악하세요.")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    uploaded_file = st.file_uploader("KRX CSV 파일 업로드", type=["csv"], help="전종목 시세 CSV 파일을 선택하세요.")
    
    st.info("""
    **사용 방법:**
    1. [KRX 정보데이터시스템](http://data.krx.co.kr/) 접속
    2. [전종목 시세] 데이터 다운로드 (CSV)
    3. 다운로드한 파일을 위 업로드 영역에 끌어다 놓으세요.
    """)

# 데이터 로드 로직
@st.cache_data
def load_data(file):
    try:
        # KRX CSV는 보통 cp949 인코딩을 사용함
        df = pd.read_csv(file, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding="utf-8")
    
    # 숫자형 데이터 변환 (콤마 제거 등)
    cols_to_fix = ["종가", "등락률", "거래량", "거래대금", "대비"]
    for col in cols_to_fix:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace(',', '').astype(float)
    return df

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # 필터링 섹션
    st.divider()
    
    # 시장구분 필터
    if "시장구분" in df.columns:
        markets = ["전체"] + sorted(df["시장구분"].unique().tolist())
        selected_market = st.selectbox("📊 시장 선택", markets)
        
        if selected_market != "전체":
            plot_df = df[df["시장구분"] == selected_market]
        else:
            plot_df = df
    else:
        plot_df = df
        st.warning("데이터에 '시장구분' 컬럼이 없습니다.")

    # 대시보드 레이아웃
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚀 오늘 가장 많이 오른 종목 (TOP 10)")
        if "등락률" in plot_df.columns:
            top_gainers = plot_df.nlargest(10, "등락률")
            fig = px.bar(
                top_gainers, 
                x="등락률", 
                y="종목명", 
                orientation="h",
                color="등락률",
                color_continuous_scale="Reds",
                text_auto='.2f',
                title="종목별 등락률 (%)"
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("'등락률' 컬럼을 찾을 수 없습니다.")

    with col2:
        st.subheader("🔥 거래가 가장 많았던 종목 (TOP 10)")
        if "거래량" in plot_df.columns:
            top_volume = plot_df.nlargest(10, "거래량")[["종목명", "종가", "거래량", "등락률"]]
            st.dataframe(
                top_volume.style.format({
                    "종가": "{:,.0f}원",
                    "거래량": "{:,.0f}주",
                    "등락률": "{:+.2f}%"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.error("'거래량' 컬럼을 찾을 수 없습니다.")

    # 전체 데이터 테이블
    st.divider()
    st.subheader("🔍 전체 시세 데이터")
    st.dataframe(
        plot_df,
        use_container_width=True,
        height=500
    )

    # 간단한 통계 요약
    st.sidebar.divider()
    st.sidebar.subheader("📋 요약 통계")
    st.sidebar.metric("총 종목 수", f"{len(plot_df):,}개")
    if "등락률" in plot_df.columns:
        avg_rate = plot_df["등락률"].mean()
        st.sidebar.metric("평균 등락률", f"{avg_rate:+.2f}%")

else:
    # 파일 미업로드 시 초기 화면
    st.info("사이드바에서 KRX CSV 파일을 업로드하여 분석을 시작하세요.")
    
    # 샘플 디자인 미리보기 (플레이스홀더)
    st.image("https://images.unsplash.com/photo-1611974717482-962553041c9a?auto=format&fit=crop&q=80&w=1000", caption="시장 데이터 분석 예시")
