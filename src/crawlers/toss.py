import feedparser
from bs4 import BeautifulSoup

def get_toss_articles():
    feed = feedparser.parse("https://toss.tech/rss.xml")
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
            "company": "토스"
        })
    return articles