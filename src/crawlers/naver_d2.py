import feedparser
from bs4 import BeautifulSoup

def get_naver_d2_articles():
    feed = feedparser.parse("https://d2.naver.com/d2.atom")
    articles = []
    for entry in feed.entries:
        raw_html = entry.content[0].value if 'content' in entry else entry.get('summary', '')
        soup = BeautifulSoup(raw_html, 'html.parser')
        content = soup.get_text(separator='\n').strip()
        articles.append({
            "title": entry.title,
            "url": entry.link,
            "date": entry.get('published', entry.get('updated', '')),
            "content": content,
            "company": "네이버 D2"
        })
    return articles