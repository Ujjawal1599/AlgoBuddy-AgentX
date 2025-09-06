from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from config.database import Base

class NewsData(Base):
    __tablename__ = "news_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    sector = Column(String(100), nullable=True, index=True)
    
    # News content
    headline = Column(Text, nullable=False)
    article_text = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    source = Column(String(100), nullable=False)  # moneycontrol, economic_times, etc.
    
    # Sentiment analysis
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    sentiment_label = Column(String(20), nullable=True)  # positive, negative, neutral
    confidence_score = Column(Float, nullable=True)  # 0 to 1
    
    # News metadata
    published_date = Column(DateTime(timezone=True), nullable=True)
    scraped_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relevance scoring
    relevance_score = Column(Float, default=0.0)  # 0 to 1
    is_breaking_news = Column(Boolean, default=False)
    impact_score = Column(Float, default=0.0)  # 0 to 1
    
    # Raw data for debugging
    raw_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<NewsData(symbol='{self.symbol}', headline='{self.headline[:50]}...', sentiment='{self.sentiment_label}')>"

