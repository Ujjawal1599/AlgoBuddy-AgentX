from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import aiohttp
import os

from config.database import get_db
from models.zerodha_data import ZerodhaData

router = APIRouter()

# Pydantic models
class MarketDataRequest(BaseModel):
    symbol: str
    timeframe: str = "1d"
    start_date: str = None
    end_date: str = None

class MarketDataResponse(BaseModel):
    symbol: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    
    class Config:
        from_attributes = True

# Mock Zerodha API client (replace with actual Zerodha API integration)
class ZerodhaAPIClient:
    def __init__(self):
        self.api_key = os.getenv("ZERODHA_API_KEY")
        self.api_secret = os.getenv("ZERODHA_API_SECRET")
        self.base_url = "https://api.kite.trade"
        
        # Mock data for development
        self.mock_prices = {
            "AAPL": {"price": 150.0, "change": 2.5},
            "GOOGL": {"price": 2800.0, "change": 15.0},
            "MSFT": {"price": 300.0, "change": 5.0},
            "TSLA": {"price": 250.0, "change": -10.0},
            "AMZN": {"price": 3300.0, "change": 25.0},
            "NFLX": {"price": 500.0, "change": 8.0},
            "META": {"price": 350.0, "change": 12.0},
            "NVDA": {"price": 800.0, "change": 30.0}
        }
    
    async def get_historical_data(self, symbol: str, start_date: str, end_date: str, timeframe: str = "1d"):
        """Get historical market data"""
        # Mock historical data generation
        import random
        from datetime import datetime, timedelta
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        data = []
        current_date = start
        
        base_price = self.mock_prices.get(symbol, {"price": 100.0})["price"]
        
        while current_date <= end:
            # Generate mock OHLCV data
            open_price = base_price + random.uniform(-5, 5)
            high_price = open_price + random.uniform(0, 3)
            low_price = open_price - random.uniform(0, 3)
            close_price = open_price + random.uniform(-2, 2)
            volume = random.randint(1000000, 5000000)
            
            data.append({
                "symbol": symbol,
                "timestamp": current_date,
                "open_price": round(open_price, 2),
                "high_price": round(high_price, 2),
                "low_price": round(low_price, 2),
                "close_price": round(close_price, 2),
                "volume": volume
            })
            
            current_date += timedelta(days=1)
            base_price = close_price
        
        return data
    
    async def get_current_price(self, symbol: str):
        """Get current market price"""
        if symbol in self.mock_prices:
            return self.mock_prices[symbol]["price"]
        return 100.0
    
    async def get_market_status(self):
        """Get market status"""
        return {
            "market_open": True,
            "current_time": datetime.now().isoformat(),
            "next_market_open": "09:30:00",
            "next_market_close": "16:00:00"
        }

zerodha_client = ZerodhaAPIClient()

@router.get("/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    timeframe: str = "1d",
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Get market data for a symbol"""
    try:
        # Set default dates if not provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get data from database first
        db_data = db.query(ZerodhaData).filter(
            ZerodhaData.symbol == symbol,
            ZerodhaData.timestamp >= start_date,
            ZerodhaData.timestamp <= end_date
        ).all()
        
        if db_data:
            # Return data from database
            return {
                "symbol": symbol,
                "data": [
                    {
                        "timestamp": data.timestamp,
                        "open": data.open_price,
                        "high": data.high_price,
                        "low": data.low_price,
                        "close": data.close_price,
                        "volume": data.volume
                    }
                    for data in db_data
                ]
            }
        else:
            # Get data from Zerodha API and store in database
            api_data = await zerodha_client.get_historical_data(symbol, start_date, end_date, timeframe)
            
            # Store in database
            for item in api_data:
                db_item = ZerodhaData(
                    symbol=item["symbol"],
                    timestamp=item["timestamp"],
                    open_price=item["open_price"],
                    high_price=item["high_price"],
                    low_price=item["low_price"],
                    close_price=item["close_price"],
                    volume=item["volume"],
                    data_type="historical",
                    timeframe=timeframe
                )
                db.add(db_item)
            
            db.commit()
            
            return {
                "symbol": symbol,
                "data": [
                    {
                        "timestamp": item["timestamp"],
                        "open": item["open_price"],
                        "high": item["high_price"],
                        "low": item["low_price"],
                        "close": item["close_price"],
                        "volume": item["volume"]
                    }
                    for item in api_data
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current-price/{symbol}")
async def get_current_price(symbol: str):
    """Get current price for a symbol"""
    try:
        price = await zerodha_client.get_current_price(symbol)
        return {
            "symbol": symbol,
            "price": price,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-status")
async def get_market_status():
    """Get current market status"""
    try:
        status = await zerodha_client.get_market_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols")
async def get_available_symbols():
    """Get list of available symbols"""
    try:
        # Mock symbols - in production, this would come from Zerodha API
        symbols = [
            {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
            {"symbol": "NFLX", "name": "Netflix Inc.", "exchange": "NASDAQ"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"}
        ]
        
        return {
            "symbols": symbols,
            "total": len(symbols)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/place-order")
async def place_order(order_data: Dict[str, Any]):
    """Place a trading order (mock implementation)"""
    try:
        # Mock order placement
        order_id = f"ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "status": "success",
            "order_id": order_id,
            "message": "Order placed successfully",
            "order_details": {
                "symbol": order_data.get("symbol"),
                "quantity": order_data.get("quantity"),
                "order_type": order_data.get("order_type", "MARKET"),
                "status": "placed"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders")
async def get_orders():
    """Get order history (mock implementation)"""
    try:
        # Mock order history
        orders = [
            {
                "order_id": "ORDER_20231201120000",
                "symbol": "AAPL",
                "quantity": 100,
                "order_type": "BUY",
                "status": "executed",
                "timestamp": "2023-12-01T12:00:00"
            },
            {
                "order_id": "ORDER_20231201130000",
                "symbol": "GOOGL",
                "quantity": 5,
                "order_type": "BUY",
                "status": "executed",
                "timestamp": "2023-12-01T13:00:00"
            }
        ]
        
        return {
            "orders": orders,
            "total": len(orders)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 