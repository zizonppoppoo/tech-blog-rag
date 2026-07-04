def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def chunk_articles(articles):
    all_chunks = []
    for article in articles:
        text_chunks = chunk_text(article["content"])
        for i, chunk in enumerate(text_chunks):
            all_chunks.append({
                "chunk_id": f"{article['company']}_{article['url'].split('/')[-1]}_{i}",
                "text": chunk,
                "title": article["title"],
                "url": article["url"],
                "date": article["date"],
                "company": article["company"]
            })
    return all_chunks