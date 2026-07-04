import feedparser
from playwright.sync_api import sync_playwright

def get_kakao_articles():
    feed = feedparser.parse("https://tech.kakao.com/feed")
    articles = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for entry in feed.entries:
            try:
                page.goto(entry.link, timeout=15000)
                page.wait_for_timeout(2000)
                content = page.locator('.inner_content').inner_text()
            except Exception as e:
                print(f"실패: {entry.title} - {e}")
                content = ""
            articles.append({
                "title": entry.title,
                "url": entry.link,
                "date": entry.get('published', entry.get('updated', '')),
                "content": content,
                "company": "카카오"
            })
        browser.close()
    return articles