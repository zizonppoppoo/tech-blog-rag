import json
import os
from crawlers.toss import get_toss_articles
from crawlers.naver_d2 import get_naver_d2_articles
from crawlers.kakao import get_kakao_articles
from preprocessing.chunker import chunk_articles

def main():
    all_articles = []
    all_articles += get_toss_articles()
    all_articles += get_naver_d2_articles()
    all_articles += get_kakao_articles()

    os.makedirs("../data/raw", exist_ok=True)
    with open("../data/raw/articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"{len(all_articles)}개 글 수집 완료")

    all_chunks = chunk_articles(all_articles)
    os.makedirs("../data/processed", exist_ok=True)
    with open("../data/processed/chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    print(f"{len(all_chunks)}개 청크 생성 완료")

if __name__ == "__main__":
    main()