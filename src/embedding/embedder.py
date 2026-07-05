from sentence_transformers import SentenceTransformer
import chromadb
import json
import os

print("테스트")
# 다국어 임베딩 모델 (한국어 지원)
MODEL_NAME = "intfloat/multilingual-e5-base"

# Chroma DB 저장 경로 (프로젝트 루트 기준 data/chroma_db)
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma_db")


def load_chunks(chunks_path):
    """1주차에서 만든 chunks.json 불러오기"""
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return chunks


def embed_and_store(chunks_path):
    """청크를 임베딩해서 Chroma DB에 저장"""

    # 1. 모델 로드
    print("임베딩 모델 로딩 중...")
    model = SentenceTransformer(MODEL_NAME)

    # 2. 청크 데이터 로드
    chunks = load_chunks(chunks_path)
    print(f"총 {len(chunks)}개 청크 로드 완료")

    # 3. Chroma 클라이언트 생성 (로컬 디스크에 영구 저장)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name="tech_blog_chunks")

    # 4. 임베딩할 텍스트, id, metadata 준비
    texts = []
    ids = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        # e5 모델은 문서 임베딩 시 "passage: " 접두어를 붙이는 게 권장됨
        texts.append(f"passage: {chunk['text']}")
        ids.append(f"chunk_{i}")
        metadatas.append({
            "title": chunk.get("title", ""),
            "url": chunk.get("url", ""),
            "company": chunk.get("company", ""),
            "date": chunk.get("date", "")
        })

    # 5. 배치로 임베딩 생성 (한 번에 다 넣으면 느릴 수 있어서 배치 처리)
    print("임베딩 생성 중... (청크 수에 따라 몇 분 걸릴 수 있어요)")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

    # 6. Chroma에 저장
    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=[chunk["text"] for chunk in chunks],  # 원본 텍스트(접두어 없이) 저장
        metadatas=metadatas
    )

    print(f"Chroma DB 저장 완료! (경로: {CHROMA_DB_PATH})")
    return collection


def search(query, top_k=5):
    """저장된 벡터DB에서 유사 청크 검색 (테스트용)"""
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(name="tech_blog_chunks")

    # e5 모델은 질문 임베딩 시 "query: " 접두어 권장
    query_embedding = model.encode(f"query: {query}")

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )
    return results


if __name__ == "__main__":
    chunks_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "chunks.json")
    embed_and_store(chunks_path)

    # 테스트 검색
    print("\n=== 테스트 검색 ===")
    test_results = search("MLOps 파이프라인 구축 경험", top_k=3)
    for doc, meta in zip(test_results["documents"][0], test_results["metadatas"][0]):
        print(f"\n[{meta['company']}] {meta['title']}")
        print(doc[:100] + "...")