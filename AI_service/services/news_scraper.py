import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
import time
import random
from urllib.parse import urljoin, urlparse
import logging
from services.selenium_moneycontrol import fetch_moneycontrol_html, parse_moneycontrol_news

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraperService:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        self.last_request_time = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            await asyncio.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()
    
    async def scrape_stock_news(self, symbol: str, sector: str = None, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Scrape news for a specific stock and its sector
        """
        all_news = []
        
        # Get stock-specific news
        stock_news = await self._scrape_moneycontrol_news(symbol)
        print('stock newsssssss', stock_news)
        all_news.extend(stock_news)

        print(f"Scraped {len(stock_news)} articles from MoneyControl for {symbol}")
        
        # Get sector news if provided
        if sector:
            sector_news = await self._scrape_economic_times_sector(sector)
            all_news.extend(sector_news)
        
        # # Get general market news
        # market_news = await self._scrape_yahoo_finance_news(symbol)
        # all_news.extend(market_news)
        
        # Filter by date and remove duplicates
        cutoff_date = datetime.now() - timedelta(days=days_back)
        filtered_news = []
        seen_headlines = set()
        
        for news in all_news:
            if news['headline'] not in seen_headlines:
                seen_headlines.add(news['headline'])
                # Ensure published_date is a datetime object
                published_date = news.get('published_date', datetime.now())
                if isinstance(published_date, str):
                    try:
                        published_date = self._parse_date(published_date)
                    except Exception:
                        published_date = datetime.now()
                if published_date >= cutoff_date:
                    filtered_news.append(news)
        
        logger.info(f"Scraped {len(filtered_news)} unique news articles for {symbol}")
        return filtered_news
    
    async def _scrape_moneycontrol_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Scrape news from MoneyControl using Selenium service"""
        try:
            # Use Selenium to fetch and parse news
            html = fetch_moneycontrol_html(symbol)
            news_list = parse_moneycontrol_news(html, symbol)
            print('moneycontrol news', news_list)
            return news_list
        except Exception as e:
            logger.error(f"Error scraping MoneyControl for {symbol} with Selenium: {e}")
            return []
    
    async def _scrape_economic_times_sector(self, sector: str) -> List[Dict[str, Any]]:
        """Scrape sector news from Economic Times"""
        news_list = []
        
        try:
            await self._rate_limit()
            
            # Economic Times markets section
            url = "https://economictimes.indiatimes.com/markets"
            
            if self.session:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find news articles
                        articles = soup.find_all('div', class_='eachStory')
                        
                        for article in articles[:15]:  # Limit to 15 articles
                            try:
                                headline_elem = article.find('a')
                                if headline_elem:
                                    headline = headline_elem.get_text(strip=True)
                                    link = headline_elem.get('href', '')
                                    
                                    # Check if headline is relevant to the sector
                                    if self._is_sector_relevant(headline, sector):
                                        news_list.append({
                                            'symbol': None,
                                            'sector': sector,
                                            'headline': headline,
                                            'url': urljoin(url, link),
                                            'source': 'economic_times',
                                            'published_date': datetime.now(),
                                            'article_text': None
                                        })
                            except Exception as e:
                                logger.warning(f"Error parsing Economic Times article: {e}")
                                continue
                                
        except Exception as e:
            logger.error(f"Error scraping Economic Times for sector {sector}: {e}")
        
        return news_list
    
    async def _scrape_yahoo_finance_news(self, symbol: str) -> List[Dict[str, Any]]:
        """Scrape news from Yahoo Finance"""
        news_list = []
        
        try:
            await self._rate_limit()
            
            # Yahoo Finance news URL
            url = f"https://finance.yahoo.com/quote/{symbol}/news"
            
            if self.session:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find news articles
                        articles = soup.find_all('h3', class_='Mb(5px)')
                        
                        for article in articles[:10]:  # Limit to 10 articles
                            try:
                                headline_elem = article.find('a')
                                if headline_elem:
                                    headline = headline_elem.get_text(strip=True)
                                    link = headline_elem.get('href', '')
                                    
                                    news_list.append({
                                        'symbol': symbol.upper(),
                                        'headline': headline,
                                        'url': urljoin(url, link),
                                        'source': 'yahoo_finance',
                                        'published_date': datetime.now(),
                                        'article_text': None
                                    })
                            except Exception as e:
                                logger.warning(f"Error parsing Yahoo Finance article: {e}")
                                continue
                                
        except Exception as e:
            logger.error(f"Error scraping Yahoo Finance for {symbol}: {e}")
        
        return news_list
    
    def _parse_date(self, date_text: str) -> datetime:
        """Parse various date formats"""
        if not date_text:
            return datetime.now()
        
        # Common date patterns
        patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_text)
            if match:
                try:
                    if pattern == patterns[2]:  # YYYY-MM-DD
                        year, month, day = match.groups()
                    else:  # MM/DD/YYYY or MM-DD-YYYY
                        month, day, year = match.groups()
                    
                    return datetime(int(year), int(month), int(day))
                except ValueError:
                    continue
        
        # If no pattern matches, return current date
        return datetime.now()
    
    def _is_sector_relevant(self, headline: str, sector: str) -> bool:
        """Check if headline is relevant to the sector"""
        if not sector:
            return True
        
        sector_keywords = {
            'technology': ['tech', 'software', 'IT', 'digital', 'AI', 'cloud', 'cyber'],
            'banking': ['bank', 'financial', 'credit', 'loan', 'finance'],
            'pharmaceuticals': ['pharma', 'drug', 'medicine', 'healthcare', 'biotech'],
            'automobile': ['auto', 'car', 'vehicle', 'automotive', 'motor'],
            'energy': ['oil', 'gas', 'energy', 'power', 'renewable', 'solar', 'wind'],
            'telecom': ['telecom', 'mobile', '5G', 'network', 'communication'],
            'retail': ['retail', 'consumer', 'shopping', 'e-commerce', 'commerce'],
            'steel': ['steel', 'metal', 'iron', 'mining', 'metals'],
            'cement': ['cement', 'construction', 'infrastructure', 'building'],
            'textiles': ['textile', 'fabric', 'garment', 'clothing', 'apparel']
        }
        
        keywords = sector_keywords.get(sector.lower(), [sector.lower()])
        headline_lower = headline.lower()
        
        return any(keyword in headline_lower for keyword in keywords)
    
    async def get_article_content(self, url: str) -> str:
        """Scrape full article content from URL"""
        try:
            await self._rate_limit()
            
            if self.session:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Try to find article content
                        content_selectors = [
                            'div.article-content',
                            'div.story-content',
                            'div.article-body',
                            'div.content',
                            'article',
                            'div.entry-content'
                        ]
                        
                        for selector in content_selectors:
                            content_elem = soup.select_one(selector)
                            if content_elem:
                                return content_elem.get_text(strip=True)
                        
                        # Fallback: get all paragraph text
                        paragraphs = soup.find_all('p')
                        return ' '.join([p.get_text(strip=True) for p in paragraphs])
                        
        except Exception as e:
            logger.error(f"Error scraping article content from {url}: {e}")
        
        return ""

