from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from config.database import get_db
from models.strategy import Strategy
from models.trade import Trade

router = APIRouter()

# Pydantic models
class StrategyCreate(BaseModel):
    name: str
    symbol: str
    strategy_code: str
    indicators: List[str] = []
    timeframe: str = "1d"
    risk_level: str = "medium"
    capital: float = 100000

class StrategyUpdate(BaseModel):
    name: str = None
    status: str = None
    evaluation_score: float = None
    evaluation_decision: str = None

class StrategyResponse(BaseModel):
    id: int
    name: str
    symbol: str
    status: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    evaluation_score: float
    evaluation_decision: str = None
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=Dict[str, Any])
async def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """Create a new trading strategy"""
    try:
        db_strategy = Strategy(
            name=strategy.name,
            symbol=strategy.symbol,
            strategy_code=strategy.strategy_code,
            indicators=strategy.indicators,
            timeframe=strategy.timeframe,
            risk_level=strategy.risk_level,
            capital=strategy.capital
        )
        
        db.add(db_strategy)
        db.commit()
        db.refresh(db_strategy)
        
        return {
            "status": "success",
            "strategy_id": db_strategy.id,
            "message": "Strategy created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get all strategies with optional filtering"""
    try:
        query = db.query(Strategy)
        
        if status:
            query = query.filter(Strategy.status == status)
        
        strategies = query.offset(skip).limit(limit).all()
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Get a specific strategy by ID"""
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        return strategy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{strategy_id}")
async def update_strategy(
    strategy_id: int,
    strategy_update: StrategyUpdate,
    db: Session = Depends(get_db)
):
    """Update a strategy"""
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Update fields
        update_data = strategy_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(strategy, field, value)
        
        db.commit()
        db.refresh(strategy)
        
        return {
            "status": "success",
            "message": "Strategy updated successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Delete a strategy"""
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        db.delete(strategy)
        db.commit()
        
        return {
            "status": "success",
            "message": "Strategy deleted successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{strategy_id}/trades")
async def get_strategy_trades(
    strategy_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get trades for a specific strategy"""
    try:
        trades = db.query(Trade).filter(
            Trade.strategy_id == strategy_id
        ).offset(skip).limit(limit).all()
        
        return {
            "strategy_id": strategy_id,
            "trades": [
                {
                    "id": trade.id,
                    "trade_id": trade.trade_id,
                    "symbol": trade.symbol,
                    "quantity": trade.quantity,
                    "price": trade.price,
                    "order_type": trade.order_type,
                    "trade_value": trade.trade_value,
                    "status": trade.status,
                    "execution_time": trade.execution_time
                }
                for trade in trades
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{strategy_id}/activate")
async def activate_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Activate a strategy"""
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        strategy.status = "active"
        db.commit()
        
        return {
            "status": "success",
            "message": "Strategy activated successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{strategy_id}/deactivate")
async def deactivate_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Deactivate a strategy"""
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        strategy.status = "inactive"
        db.commit()
        
        return {
            "status": "success",
            "message": "Strategy deactivated successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 