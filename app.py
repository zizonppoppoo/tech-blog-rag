import streamlit as st
import sys
import os

# src 폴더를 파이썬 경로에 추가 (generator.py를 불러오기 위해)
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from generation.generator import Generator

# 페이지 기본 설정
st.set_page_config(page_title="기술 블로그 RAG 챗봇", page_icon="🔍")
st.title("🔍 국내 기업 기술 블로그 RAG 챗봇")
st.caption("토스 · 카카오 · 네이버 D2 기술 블로그 내용을 기반으로 답변합니다")

# Generator는 한 번만 로드되도록 캐싱 (안 하면 질문할 때마다 모델 다시 로드됨)
@st.cache_resource
def load_generator():
    return Generator()

generator = load_generator()

# 질문 입력
query = st.text_input("질문을 입력하세요", placeholder="예: AI 모델 서빙 최적화는 어떻게 하나요?")

if st.button("질문하기") and query:
    with st.spinner("답변 생성 중..."):
        result = generator.answer(query)

    st.markdown("### 답변")
    st.markdown(result["answer"])

    if result["sources"]:
        st.markdown("### 참고 출처")
        for s in result["sources"]:
            st.markdown(f"- **[{s['company']}]** [{s['title']}]({s['url']})")