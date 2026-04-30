"""
[8] DB/시스템 연동 — Supabase

Supabase는 PostgreSQL 기반 클라우드 DB.
anon 키로 공개 테이블 조회 가능.

대시보드: https://supabase.com/dashboard
"""

import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Supabase 연동", layout="wide")
st.title("☁️ DB 연동 — Supabase (links 테이블)")

# ─── 연결 설정 ────────────────────────────────────────
SUPABASE_URL = "https://srmoliyhigxamvuntzxz.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNybW9saXloaWd4YW12dW50"
    "enh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4OTEyNzEsImV4cCI6"
    "MjA5MjQ2NzI3MX0.Ymz7zdjItDjjkAp1nlKPZbs1eqG_RlTcqcn0i0nxauM"
)


@st.cache_resource
def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


@st.cache_data(ttl=60)
def fetch_links():
    client = get_client()
    res = client.table("links").select("*").execute()
    return res.data


# ─── 데이터 조회 ──────────────────────────────────────
with st.spinner("Supabase에서 links 테이블 조회 중..."):
    try:
        data = fetch_links()
    except Exception as e:
        st.error(f"조회 실패: {e}")
        st.stop()

if not data:
    st.warning("데이터가 없거나 접근 권한이 없습니다.")
    st.stop()

import pandas as pd
df = pd.DataFrame(data)

st.success(f"✅ {len(df)}건 조회")
st.caption("Supabase URL: " + SUPABASE_URL)

# ─── 컬럼 정보 ────────────────────────────────────────
with st.expander("📋 컬럼 목록"):
    st.write(df.dtypes.reset_index().rename(columns={"index": "컬럼", 0: "타입"}))

# ─── 전체 데이터 ──────────────────────────────────────
st.subheader("📊 전체 데이터")
st.dataframe(df, hide_index=True, width="stretch")

# ─── 필터 ─────────────────────────────────────────────
text_cols = df.select_dtypes(include="object").columns.tolist()
if text_cols:
    st.subheader("🔍 검색")
    col_filter = st.selectbox("검색할 컬럼", text_cols)
    keyword = st.text_input("키워드")
    if keyword:
        filtered = df[df[col_filter].astype(str).str.contains(keyword, case=False, na=False)]
        st.dataframe(filtered, hide_index=True, width="stretch")
        st.caption(f"{len(filtered)}건 검색됨")
