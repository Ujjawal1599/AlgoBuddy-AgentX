from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup, Comment
import time
import re

def fetch_moneycontrol_html(symbol: str) -> str:
    """
    Use Selenium to fetch the rendered HTML for a MoneyControl company news page.
    Returns the page HTML as a string.
    """
    url = f"https://www.moneycontrol.com/news/tags/{symbol}.html"
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(3)  # Wait for JS to load
        html = driver.page_source
        return html
    finally:
        driver.quit()

def parse_moneycontrol_news(html: str, symbol: str):
    news_list = []
    soup = BeautifulSoup(html, 'html.parser')

    ul = soup.find('ul', id='cagetory')
    if not ul:
        print("No <ul id='cagetory'> found.")
        return news_list

    for li in ul.find_all('li', class_='clearfix', recursive=False):
        try:
            # Skip ads or hidden items
            if 'Advertisement' in li.text or li.get('style') == 'display: none;':
                continue

            # Headline and link
            h2 = li.find('h2')
            if not h2:
                continue
            a = h2.find('a')
            if not a or not a.get('href'):
                continue
            headline = a.get_text(strip=True)
            link = a['href']

            # Summary
            p = h2.find_next_sibling('p')
            summary = p.get_text(strip=True) if p else ''

            # Date extraction from comment
            published_date = ''
            for c in li.children:
                if isinstance(c, Comment):
                    m = re.search(r'<span>(.*?)</span>', c)
                    if m:
                        published_date = m.group(1).strip()
                        break

            news_list.append({
                'symbol': symbol.upper(),
                'headline': headline,
                'url': link,
                'source': 'moneycontrol',
                'published_date': published_date,
                'article_text': summary
            })
        except Exception as e:
            print(f"Error parsing li: {e}")
            continue
    print(f"Parsed {len(news_list)} news articles from MoneyControl.")
    return news_list

if __name__ == "__main__":
    symbol = "TCS"  # Example
    html = fetch_moneycontrol_html(symbol)
    news = parse_moneycontrol_news(html, symbol)
    for n in news:
        print(n)
