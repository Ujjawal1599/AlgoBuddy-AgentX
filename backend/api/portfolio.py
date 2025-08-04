from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from config.database import get_db
from models.portfolio import Portfolio
from models.trade import Trade

router = APIRouter()

# Pydantic models
class PortfolioCreate(BaseModel):
    name: str
    cash: float = 100000

class PortfolioResponse(BaseModel):
    id: int
    name: str
    cash: float
    total_value: float
    max_value: float
    current_drawdown: float
    daily_pnl: float
    total_positions: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=Dict[str, Any])
async def create_portfolio(portfolio: PortfolioCreate, db: Session = Depends(get_db)):
    """Create a new portfolio"""
    try:
        db_portfolio = Portfolio(
            name=portfolio.name,
            cash=portfolio.cash,
            total_value=portfolio.cash,
            max_value=portfolio.cash
        )
        
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        
        return {
            "status": "success",
            "portfolio_id": db_portfolio.id,
            "message": "Portfolio created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[PortfolioResponse])
async def get_portfolios(db: Session = Depends(get_db)):
    """Get all portfolios"""
    try:
        portfolios = db.query(Portfolio).all()
        return portfolios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Get a specific portfolio by ID"""
    try:
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{portfolio_id}/status")
async def get_portfolio_status(portfolio_id: int, db: Session = Depends(get_db)):
    """Get detailed portfolio status"""
    try:
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Get recent trades for this portfolio
        recent_trades = db.query(Trade).limit(10).all()
        
        # Calculate positions (mock data for now)
        positions = [
            {
                "symbol": "AAPL",
                "quantity": 100,
                "avg_price": 150.0,
                "current_price": 155.0,
                "position_value": 15500.0,
                "unrealized_pnl": 500.0,
                "unrealized_pnl_pct": 3.33
            },
            {
                "symbol": "GOOGL",
                "quantity": 5,
                "avg_price": 2800.0,
                "current_price": 2850.0,
                "position_value": 14250.0,
                "unrealized_pnl": 250.0,
                "unrealized_pnl_pct": 1.79
            }
        ]
        
        return {
            "portfolio_id": portfolio.id,
            "name": portfolio.name,
            "cash": portfolio.cash,
            "total_value": portfolio.total_value,
            "max_value": portfolio.max_value,
            "current_drawdown": portfolio.current_drawdown,
            "daily_pnl": portfolio.daily_pnl,
            "total_positions": len(positions),
            "positions": positions,
            "recent_trades": [
                {
                    "id": trade.id,
                    "symbol": trade.symbol,
                    "quantity": trade.quantity,
                    "price": trade.price,
                    "order_type": trade.order_type,
                    "execution_time": trade.execution_time
                }
                for trade in recent_trades
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{portfolio_id}/performance")
async def get_portfolio_performance(portfolio_id: int, db: Session = Depends(get_db)):
    """Get portfolio performance metrics"""
    try:
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Calculate performance metrics
        total_return = ((portfolio.total_value - portfolio.max_value) / portfolio.max_value) * 100
        
        return {
            "portfolio_id": portfolio.id,
            "total_value": portfolio.total_value,
            "max_value": portfolio.max_value,
            "total_return": total_return,
            "current_drawdown": portfolio.current_drawdown,
            "daily_pnl": portfolio.daily_pnl,
            "total_positions": portfolio.total_positions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{portfolio_id}/update")
async def update_portfolio_value(
    portfolio_id: int,
    new_value: float,
    db: Session = Depends(get_db)
):
    """Update portfolio value"""
    try:
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Update portfolio value
        old_value = portfolio.total_value
        portfolio.total_value = new_value
        portfolio.max_value = max(portfolio.max_value, new_value)
        
        # Calculate drawdown
        portfolio.current_drawdown = ((portfolio.max_value - new_value) / portfolio.max_value) * 100
        
        # Calculate daily P&L (simplified)
        portfolio.daily_pnl = new_value - old_value
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Portfolio value updated successfully",
            "new_value": new_value,
            "drawdown": portfolio.current_drawdown,
            "daily_pnl": portfolio.daily_pnl
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 