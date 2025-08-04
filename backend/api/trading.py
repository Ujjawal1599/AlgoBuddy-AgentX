from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid

from config.database import get_db
from models.trade import Trade
from models.strategy import Strategy

router = APIRouter()

# Pydantic models
class TradeCreate(BaseModel):
    strategy_id: int
    symbol: str
    quantity: int
    order_type: str = "MARKET"
    price: float = None
    stop_loss: float = None
    take_profit: float = None

class TradeResponse(BaseModel):
    id: int
    trade_id: str
    strategy_id: int
    symbol: str
    quantity: int
    price: float
    order_type: str
    trade_value: float
    status: str
    execution_time: datetime
    
    class Config:
        from_attributes = True

@router.post("/execute", response_model=Dict[str, Any])
async def execute_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    """Execute a trade"""
    try:
        # Validate strategy exists
        strategy = db.query(Strategy).filter(Strategy.id == trade.strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Generate trade ID
        trade_id = str(uuid.uuid4())
        
        # Get current market price if not provided
        if trade.price is None:
            # This would integrate with Zerodha API in production
            mock_prices = {
                "AAPL": 150.0,
                "GOOGL": 2800.0,
                "MSFT": 300.0,
                "TSLA": 250.0,
                "AMZN": 3300.0
            }
            price = mock_prices.get(trade.symbol, 100.0)
        else:
            price = trade.price
        
        # Calculate trade value
        trade_value = trade.quantity * price
        
        # Create trade record
        db_trade = Trade(
            trade_id=trade_id,
            strategy_id=trade.strategy_id,
            symbol=trade.symbol,
            quantity=trade.quantity,
            price=price,
            order_type=trade.order_type,
            trade_value=trade_value,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit
        )
        
        db.add(db_trade)
        db.commit()
        db.refresh(db_trade)
        
        return {
            "status": "success",
            "trade_id": trade_id,
            "trade_details": {
                "id": db_trade.id,
                "symbol": db_trade.symbol,
                "quantity": db_trade.quantity,
                "price": db_trade.price,
                "trade_value": db_trade.trade_value,
                "order_type": db_trade.order_type,
                "status": db_trade.status,
                "execution_time": db_trade.execution_time
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[TradeResponse])
async def get_trades(
    skip: int = 0,
    limit: int = 100,
    strategy_id: int = None,
    symbol: str = None,
    db: Session = Depends(get_db)
):
    """Get all trades with optional filtering"""
    try:
        query = db.query(Trade)
        
        if strategy_id:
            query = query.filter(Trade.strategy_id == strategy_id)
        
        if symbol:
            query = query.filter(Trade.symbol == symbol)
        
        trades = query.offset(skip).limit(limit).all()
        return trades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(trade_id: str, db: Session = Depends(get_db)):
    """Get a specific trade by ID"""
    try:
        trade = db.query(Trade).filter(Trade.trade_id == trade_id).first()
        
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        return trade
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/statistics")
async def get_trading_statistics(db: Session = Depends(get_db)):
    """Get trading statistics"""
    try:
        # Total trades
        total_trades = db.query(Trade).count()
        
        # Buy vs Sell trades
        buy_trades = db.query(Trade).filter(Trade.order_type == "BUY").count()
        sell_trades = db.query(Trade).filter(Trade.order_type == "SELL").count()
        
        # Total trade value
        total_value = db.query(Trade.trade_value).all()
        total_value = sum([t[0] for t in total_value])
        
        # Unique symbols traded
        unique_symbols = db.query(Trade.symbol).distinct().count()
        
        # Recent trades (last 7 days)
        from datetime import timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_trades = db.query(Trade).filter(Trade.execution_time >= week_ago).count()
        
        return {
            "total_trades": total_trades,
            "buy_trades": buy_trades,
            "sell_trades": sell_trades,
            "total_value": total_value,
            "unique_symbols": unique_symbols,
            "recent_trades": recent_trades
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols/{symbol}/statistics")
async def get_symbol_statistics(symbol: str, db: Session = Depends(get_db)):
    """Get trading statistics for a specific symbol"""
    try:
        # Get all trades for the symbol
        trades = db.query(Trade).filter(Trade.symbol == symbol).all()
        
        if not trades:
            return {
                "symbol": symbol,
                "message": "No trades found for this symbol"
            }
        
        # Calculate statistics
        total_trades = len(trades)
        buy_trades = len([t for t in trades if t.order_type == "BUY"])
        sell_trades = len([t for t in trades if t.order_type == "SELL"])
        
        total_buy_value = sum([t.trade_value for t in trades if t.order_type == "BUY"])
        total_sell_value = sum([t.trade_value for t in trades if t.order_type == "SELL"])
        
        avg_price = sum([t.price for t in trades]) / len(trades)
        
        return {
            "symbol": symbol,
            "total_trades": total_trades,
            "buy_trades": buy_trades,
            "sell_trades": sell_trades,
            "total_buy_value": total_buy_value,
            "total_sell_value": total_sell_value,
            "net_pnl": total_sell_value - total_buy_value,
            "avg_price": avg_price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 