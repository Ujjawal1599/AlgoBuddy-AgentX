import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from .news_scraper import NewsScraperService
from .sentiment_analyzer import SentimentAnalyzerService
from .sector_mapper import SectorMapperService

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.scraper = NewsScraperService()
        self.sentiment_analyzer = SentimentAnalyzerService()
        self.sector_mapper = SectorMapperService()
    
    async def get_news_for_stock(self, symbol: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Get comprehensive news data for a stock including sentiment analysis
        """
        try:
            # Get sector for the stock
            sector = self.sector_mapper.get_sector(symbol)
            if not sector:
                logger.warning(f"No sector found for {symbol}")
                sector = "General"
            
            # Scrape news
            async with self.scraper as scraper:
                news_articles = await scraper.scrape_stock_news(symbol, sector, days_back)
            
            # Analyze sentiment for each article
            processed_news = []
            for article in news_articles:
                try:
                    # Analyze sentiment
                    sentiment_data = await self.sentiment_analyzer.analyze_sentiment(
                        article['headline'], 
                        context="financial"
                    )
                    
                    # Calculate impact score
                    impact_score = self.sentiment_analyzer.calculate_news_impact_score(
                        sentiment_data, 
                        article['headline']
                    )
                    
                    # Add sentiment data to article
                    article.update({
                        'sentiment_score': sentiment_data.get('sentiment_score', 0.0),
                        'sentiment_label': sentiment_data.get('sentiment_label', 'neutral'),
                        'confidence_score': sentiment_data.get('confidence_score', 0.0),
                        'impact_score': impact_score,
                        'financial_sentiment': sentiment_data.get('financial_sentiment', 'neutral'),
                        'sector': sector,
                        'processed_at': datetime.now().isoformat()
                    })
                    
                    processed_news.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing sentiment for article: {e}")
                    # Add article without sentiment data
                    article.update({
                        'sentiment_score': 0.0,
                        'sentiment_label': 'neutral',
                        'confidence_score': 0.0,
                        'impact_score': 0.0,
                        'sector': sector,
                        'processed_at': datetime.now().isoformat()
                    })
                    processed_news.append(article)
            
            # Sort by impact score and date
            processed_news.sort(key=lambda x: (x.get('impact_score', 0), x.get('published_date', datetime.min)), reverse=True)
            
            logger.info(f"Processed {len(processed_news)} news articles for {symbol}")
            return processed_news
            
        except Exception as e:
            logger.error(f"Error getting news for {symbol}: {e}")
            return []
    
    async def get_sector_news(self, sector: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Get news for an entire sector
        """
        try:
            # Get all stocks in the sector
            stocks = self.sector_mapper.get_stocks_in_sector(sector)
            
            if not stocks:
                logger.warning(f"No stocks found for sector {sector}")
                return []
            
            # Get news for each stock (limit to top 5 stocks to avoid rate limiting)
            all_news = []
            for stock in stocks[:5]:
                stock_news = await self.get_news_for_stock(stock, days_back)
                all_news.extend(stock_news)
            
            # Remove duplicates and sort
            unique_news = self._remove_duplicate_news(all_news)
            unique_news.sort(key=lambda x: (x.get('impact_score', 0), x.get('published_date', datetime.min)), reverse=True)
            
            logger.info(f"Found {len(unique_news)} unique news articles for sector {sector}")
            return unique_news
            
        except Exception as e:
            logger.error(f"Error getting sector news for {sector}: {e}")
            return []
    
    def _remove_duplicate_news(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate news articles based on headline similarity"""
        unique_news = []
        seen_headlines = set()
        
        for article in news_list:
            headline = article.get('headline', '').lower().strip()
            if headline and headline not in seen_headlines:
                seen_headlines.add(headline)
                unique_news.append(article)
        
        return unique_news
    
    def generate_news_summary(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of news sentiment and key insights
        """
        if not news_list:
            return {
                'total_articles': 0,
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'key_insights': [],
                'top_news': []
            }
        
        # Calculate overall sentiment
        sentiment_scores = [article.get('sentiment_score', 0.0) for article in news_list]
        confidence_scores = [article.get('confidence_score', 0.0) for article in news_list]
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Determine overall sentiment label
        if avg_sentiment > 0.1:
            overall_sentiment = 'positive'
        elif avg_sentiment < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # Get top news by impact score
        top_news = sorted(news_list, key=lambda x: x.get('impact_score', 0), reverse=True)[:5]
        
        # Generate key insights
        key_insights = self._generate_key_insights(news_list, overall_sentiment)
        
        return {
            'total_articles': len(news_list),
            'overall_sentiment': overall_sentiment,
            'sentiment_score': avg_sentiment,
            'confidence': avg_confidence,
            'key_insights': key_insights,
            'top_news': top_news,
            'sector_breakdown': self._get_sector_breakdown(news_list)
        }
    
    def _generate_key_insights(self, news_list: List[Dict[str, Any]], overall_sentiment: str) -> List[str]:
        """Generate key insights from news data"""
        insights = []
        
        # Sentiment distribution
        positive_count = sum(1 for article in news_list if article.get('sentiment_label') == 'positive')
        negative_count = sum(1 for article in news_list if article.get('sentiment_label') == 'negative')
        neutral_count = sum(1 for article in news_list if article.get('sentiment_label') == 'neutral')
        
        total = len(news_list)
        if total > 0:
            insights.append(f"Sentiment distribution: {positive_count/total*100:.1f}% positive, {negative_count/total*100:.1f}% negative, {neutral_count/total*100:.1f}% neutral")
        
        # High impact news
        high_impact = [article for article in news_list if article.get('impact_score', 0) > 0.7]
        if high_impact:
            insights.append(f"{len(high_impact)} high-impact news articles identified")
        
        # Breaking news
        breaking_news = [article for article in news_list if 'breaking' in article.get('headline', '').lower()]
        if breaking_news:
            insights.append(f"{len(breaking_news)} breaking news articles found")
        
        # Source diversity
        sources = set(article.get('source', 'unknown') for article in news_list)
        insights.append(f"News from {len(sources)} different sources: {', '.join(sources)}")
        
        return insights
    
    def _get_sector_breakdown(self, news_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get breakdown of news by sector"""
        sector_count = {}
        for article in news_list:
            sector = article.get('sector', 'Unknown')
            sector_count[sector] = sector_count.get(sector, 0) + 1
        return sector_count
    
    async def get_news_for_algo_generation(self, symbol: str, days_back: int = 7) -> str:
        """
        Get formatted news data for algorithm generation
        """
        news_data = await self.get_news_for_stock(symbol, days_back)
        summary = self.generate_news_summary(news_data)
        
        # Format for AI prompt
        news_context = f"""
Recent News Analysis for {symbol}:
- Overall Sentiment: {summary['overall_sentiment']} (Score: {summary['sentiment_score']:.2f})
- Confidence: {summary['confidence']:.2f}
- Total Articles: {summary['total_articles']}

Key Insights:
{chr(10).join(f"- {insight}" for insight in summary['key_insights'])}

Top News Headlines:
"""
        
        for i, article in enumerate(summary['top_news'][:5], 1):
            news_context += f"{i}. {article['headline']} (Sentiment: {article['sentiment_label']}, Impact: {article['impact_score']:.2f})\n"
        
        return news_context.strip()
