from sentence_transformers import SentenceTransformer
import chromadb
import os

MODEL_NAME = "intfloat/multilingual-e5-base"
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma_db")


class Retriever:
    """검색 전용 클래스. 모델을 한 번만 로드해서 재사용."""

    def __init__(self):
        print("검색용 임베딩 모델 로딩 중...")
        self.model = SentenceTransformer(MODEL_NAME)
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.client.get_collection(name="tech_blog_chunks")
        print("로딩 완료")

    def search(self, query, top_k=5, company_filter=None, distance_threshold=None):
        """
        query: 검색할 질문
        top_k: 반환할 결과 개수
        company_filter: 특정 회사로 필터링 (예: "카카오")
        distance_threshold: 이 값보다 거리가 크면(=유사도가 낮으면) 결과에서 제외. None이면 필터링 안 함
        """
        query_embedding = self.model.encode(f"query: {query}")
        where_filter = {"company": company_filter} if company_filter else None

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where_filter
        )

        formatted = []
        for doc, meta, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            if distance_threshold is not None and distance > distance_threshold:
                continue  # 너무 관련 없는 결과는 제외
            formatted.append({
                "text": doc,
                "title": meta.get("title", ""),
                "company": meta.get("company", ""),
                "url": meta.get("url", ""),
                "distance": distance
            })
        return formatted


if __name__ == "__main__":
    retriever = Retriever()

    # 테스트 질문 여러 개로 품질 확인
    test_queries = [
        "RAG 시스템은 어떻게 구축하나요?",
        "장애 대응은 어떻게 하나요?",
        "AI 모델 서빙 최적화 방법",
    ]

    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"질문: {q}")
        print('='*60)
        results = retriever.search(q, top_k=3, distance_threshold=0.35)
        if not results:
            print("→ 관련 문서를 찾지 못했습니다 (임계값 초과)")
        for r in results:
            print(f"\n[{r['company']}] {r['title']} (거리: {r['distance']:.3f})")
            print(r['text'][:100] + "...")