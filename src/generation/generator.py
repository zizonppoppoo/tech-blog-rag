from anthropic import Anthropic
from dotenv import load_dotenv
import os
import sys

# 상위 폴더의 retriever 불러오기 위한 경로 설정
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from embedding.retriever import Retriever

env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=env_path)
print("API 키 로드 여부:", os.getenv("ANTHROPIC_API_KEY") is not None)

MODEL_NAME = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """당신은 국내 대기업(토스, 카카오, 네이버 D2) 기술 블로그 내용을 바탕으로 질문에 답하는 어시스턴트입니다.

규칙:
1. 반드시 주어진 [참고 문서] 내용만 근거로 답변하세요. 문서에 없는 내용은 지어내지 마세요.
2. 답변 마지막에 참고한 출처(회사명, 글 제목)를 반드시 표시하세요.
3. [참고 문서]에 질문과 관련된 내용이 없다면, "제공된 문서에서 관련 정보를 찾지 못했습니다"라고 솔직하게 답하세요.
4. 답변은 간결하고 명확하게, 한국어로 작성하세요."""

def deduplicate_sources(sources):
    """같은 글(url 기준)이 여러 번 나오면 하나로 합치기"""
    seen = set()
    unique_sources = []
    for s in sources:
        if s["url"] not in seen:
            seen.add(s["url"])
            unique_sources.append(s)
    return unique_sources

class Generator:
    def __init__(self):
        self.client = Anthropic()  # 환경변수 ANTHROPIC_API_KEY 자동으로 읽음
        self.retriever = Retriever()

    def build_context(self, search_results):
        """검색 결과를 프롬프트에 넣을 텍스트로 조합"""
        if not search_results:
            return None

        context_parts = []
        for i, r in enumerate(search_results, 1):
            context_parts.append(
                f"[문서 {i}] 회사: {r['company']} | 제목: {r['title']}\n내용: {r['text']}\n"
            )
        return "\n".join(context_parts)

    def answer(self, query, top_k=5, distance_threshold=0.4):
        # 1. 검색
        search_results = self.retriever.search(
            query, top_k=top_k, distance_threshold=distance_threshold
        )

        # 2. 검색 결과 없으면 LLM 호출 없이 바로 응답 (비용 절약)
        context = self.build_context(search_results)
        if context is None:
            return {
                "answer": "제공된 문서에서 관련 정보를 찾지 못했습니다.",
                "sources": []
            }

        # 3. 프롬프트 구성 및 LLM 호출
        user_message = f"""[참고 문서]
{context}

[질문]
{query}"""

        response = self.client.messages.create(
            model=MODEL_NAME,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )

        answer_text = response.content[0].text

        # 4. 출처 정보 별도로도 구조화해서 반환 (프론트/API 응답에 활용)
        sources = [
            {"company": r["company"], "title": r["title"], "url": r["url"]}
            for r in search_results
        ]

        sources = deduplicate_sources(sources)
        return {"answer": answer_text, "sources": sources}


if __name__ == "__main__":
    generator = Generator()

    test_queries = [
        "AI 모델 서빙 최적화는 어떻게 하나요?",
        "RAG 시스템은 어떻게 구축하나요?",
    ]

    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"질문: {q}")
        print('='*60)
        result = generator.answer(q)
        print(f"\n답변:\n{result['answer']}")
        print(f"\n출처: {result['sources']}")