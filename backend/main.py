from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import os
from dotenv import load_dotenv
import httpx
import asyncio

from api.strategies import router as strategies_router
from api.trading import router as trading_router
from api.portfolio import router as portfolio_router
from api.zerodha import router as zerodha_router
from config.database import init_db

# Load environment variables
load_dotenv()

app = FastAPI(
    title="TiDB Agentx Trading Platform",
    description="Algorithmic trading platform with agentic AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(strategies_router, prefix="/api/strategies", tags=["strategies"])
app.include_router(trading_router, prefix="/api/trading", tags=["trading"])
app.include_router(portfolio_router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(zerodha_router, prefix="/api/zerodha", tags=["zerodha"])

# AI Service client
class AIServiceClient:
    def __init__(self):
        self.base_url = os.getenv("AI_SERVICE_URL", "http://localhost:8001")
    
    async def generate_strategy(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/generate-strategy", json=request_data)
            return response.json()
    
    async def backtest_strategy(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/backtest-strategy", json=request_data)
            return response.json()
    
    async def evaluate_strategy(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/evaluate-strategy", json=backtest_results)
            return response.json()

ai_client = AIServiceClient()

# Pydantic models
class StrategyRequest(BaseModel):
    symbol: str
    indicators: List[str]
    timeframe: str = "1d"
    risk_level: str = "medium"
    capital: float = 100000

class BacktestRequest(BaseModel):
    strategy_code: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float = 100000

class TradingRequest(BaseModel):
    strategy_id: str
    symbol: str
    quantity: int
    order_type: str = "MARKET"

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "TiDB Agentx Backend",
        "version": "1.0.0"
    }

# Strategy generation endpoint
@app.post("/api/strategies/generate")
async def generate_strategy(request: StrategyRequest):
    """Generate a trading strategy using AI"""
    try:
        request_data = {
            "symbol": request.symbol,
            "indicators": request.indicators,
            "timeframe": request.timeframe,
            "risk_level": request.risk_level,
            "capital": request.capital
        }
        
        result = await ai_client.generate_strategy(request_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Backtest endpoint
@app.post("/api/strategies/backtest")
async def backtest_strategy(request: BacktestRequest):
    """Run backtest on a strategy"""
    try:
        request_data = {
            "strategy_code": request.strategy_code,
            "symbol": request.symbol,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "initial_capital": request.initial_capital
        }
        
        result = await ai_client.backtest_strategy(request_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Strategy evaluation endpoint
@app.post("/api/strategies/evaluate")
async def evaluate_strategy(backtest_results: Dict[str, Any]):
    """Evaluate strategy performance"""
    try:
        result = await ai_client.evaluate_strategy(backtest_results)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Database initialization
@app.on_event("startup")
async def startup_event():
    await init_db()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 