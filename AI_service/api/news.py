from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging

from services.news_service import NewsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/news", tags=["news"])

# Initialize news service
news_service = NewsService()

class NewsRequest(BaseModel):
    symbol: str
    days_back: int = 7
    include_sentiment: bool = True

class SectorNewsRequest(BaseModel):
    sector: str
    days_back: int = 7
    include_sentiment: bool = True

@router.get("/stock/{symbol}")
async def get_stock_news(
    symbol: str,
    days_back: int = Query(7, ge=1, le=30),
    include_sentiment: bool = Query(True)
) -> Dict[str, Any]:
    """
    Get news for a specific stock with sentiment analysis
    """
    try:
        news_data = await news_service.get_news_for_stock(symbol, days_back)
        
        if not news_data:
            return {
                "status": "success",
                "symbol": symbol,
                "message": "No news found for this symbol",
                "data": [],
                "summary": {
                    "total_articles": 0,
                    "overall_sentiment": "neutral",
                    "sentiment_score": 0.0
                }
            }
        
        # Generate summary
        summary = news_service.generate_news_summary(news_data)
        
        return {
            "status": "success",
            "symbol": symbol,
            "data": news_data,
            "summary": summary,
            "message": f"Found {len(news_data)} news articles"
        }
        
    except Exception as e:
        logger.error(f"Error getting news for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sector/{sector}")
async def get_sector_news(
    sector: str,
    days_back: int = Query(7, ge=1, le=30),
    include_sentiment: bool = Query(True)
) -> Dict[str, Any]:
    """
    Get news for a specific sector with sentiment analysis
    """
    try:
        news_data = await news_service.get_sector_news(sector, days_back)
        
        if not news_data:
            return {
                "status": "success",
                "sector": sector,
                "message": "No news found for this sector",
                "data": [],
                "summary": {
                    "total_articles": 0,
                    "overall_sentiment": "neutral",
                    "sentiment_score": 0.0
                }
            }
        
        # Generate summary
        summary = news_service.generate_news_summary(news_data)
        
        return {
            "status": "success",
            "sector": sector,
            "data": news_data,
            "summary": summary,
            "message": f"Found {len(news_data)} news articles"
        }
        
    except Exception as e:
        logger.error(f"Error getting news for sector {sector}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sectors")
async def get_available_sectors() -> Dict[str, Any]:
    """
    Get list of available sectors
    """
    try:
        sectors = news_service.sector_mapper.get_all_sectors()
        return {
            "status": "success",
            "sectors": sectors,
            "count": len(sectors)
        }
    except Exception as e:
        logger.error(f"Error getting sectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sector/{sector}/stocks")
async def get_stocks_in_sector(sector: str) -> Dict[str, Any]:
    """
    Get stocks in a specific sector
    """
    try:
        stocks = news_service.sector_mapper.get_stocks_in_sector(sector)
        return {
            "status": "success",
            "sector": sector,
            "stocks": stocks,
            "count": len(stocks)
        }
    except Exception as e:
        logger.error(f"Error getting stocks for sector {sector}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment/{symbol}")
async def get_sentiment_analysis(
    symbol: str,
    days_back: int = Query(7, ge=1, le=30)
) -> Dict[str, Any]:
    """
    Get sentiment analysis for a stock
    """
    try:
        news_data = await news_service.get_news_for_stock(symbol, days_back)
        summary = news_service.generate_news_summary(news_data)
        
        return {
            "status": "success",
            "symbol": symbol,
            "sentiment_analysis": {
                "overall_sentiment": summary["overall_sentiment"],
                "sentiment_score": summary["sentiment_score"],
                "confidence": summary["confidence"],
                "total_articles": summary["total_articles"],
                "key_insights": summary["key_insights"]
            },
            "top_news": summary["top_news"][:5]
        }
        
    except Exception as e:
        logger.error(f"Error getting sentiment for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrape")
async def scrape_news(request: NewsRequest) -> Dict[str, Any]:
    """
    Manually trigger news scraping for a stock
    """
    try:
        news_data = await news_service.get_news_for_stock(
            request.symbol, 
            request.days_back
        )
        
        summary = news_service.generate_news_summary(news_data)
        
        return {
            "status": "success",
            "symbol": request.symbol,
            "scraped_at": datetime.now().isoformat(),
            "data": news_data,
            "summary": summary,
            "message": f"Scraped {len(news_data)} news articles"
        }
        
    except Exception as e:
        logger.error(f"Error scraping news for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check for news service
    """
    try:
        # Test basic functionality
        test_news = await news_service.get_news_for_stock("TCS", 1)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "news_scraper": "operational",
                "sentiment_analyzer": "operational",
                "sector_mapper": "operational"
            },
            "test_results": {
                "test_symbol": "TCS",
                "articles_found": len(test_news)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

