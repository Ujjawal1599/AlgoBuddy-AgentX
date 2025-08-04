from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from config.database import Base

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    cash = Column(Float, default=100000)
    total_value = Column(Float, default=100000)
    max_value = Column(Float, default=100000)
    
    # Risk metrics
    current_drawdown = Column(Float, default=0.0)
    daily_pnl = Column(Float, default=0.0)
    total_positions = Column(Integer, default=0)
    
    # Positions (stored as JSON for flexibility)
    positions = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(20), default="active")  # active, suspended, closed
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}', total_value={self.total_value})>" 