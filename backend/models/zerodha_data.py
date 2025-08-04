from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from config.database import Base

class ZerodhaData(Base):
    __tablename__ = "zerodha_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # OHLCV data
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    
    # Additional data
    data_type = Column(String(20), default="historical")  # historical, realtime
    timeframe = Column(String(20), default="1d")  # 1m, 5m, 15m, 1h, 1d
    
    # Raw API response (for debugging)
    raw_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ZerodhaData(symbol='{self.symbol}', timestamp={self.timestamp}, close={self.close_price})>" 