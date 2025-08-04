from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from config.database import Base

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    symbol = Column(String(50), nullable=False)
    strategy_code = Column(Text, nullable=False)
    indicators = Column(JSON, nullable=True)
    timeframe = Column(String(20), default="1d")
    risk_level = Column(String(20), default="medium")
    capital = Column(Float, default=100000)
    
    # Performance metrics
    total_return = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    
    # Status
    status = Column(String(20), default="draft")  # draft, active, inactive, archived
    evaluation_score = Column(Float, default=0.0)
    evaluation_decision = Column(String(50), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, name='{self.name}', symbol='{self.symbol}')>" 