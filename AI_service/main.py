import asyncio
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from agents.strategy_generator import StrategyGeneratorAgent
from agents.backtest_agent import BacktestAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.risk_manager import RiskManagerAgent
from services.strategy_service import StrategyService

# Load environment variables
load_dotenv()

app = FastAPI(title="TiDB Agentx AI Service", version="1.0.0")

# Initialize agents
strategy_generator = StrategyGeneratorAgent()
backtest_agent = BacktestAgent()
evaluator_agent = EvaluatorAgent()
risk_manager = RiskManagerAgent()
strategy_service = StrategyService()

class StrategyRequest(BaseModel):
    symbol: str
    indicators: list[str]
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

@app.post("/generate-strategy")
async def generate_strategy(request: StrategyRequest) -> Dict[str, Any]:
    """Generate a trading strategy using AI agents"""
    try:
        # Generate strategy using StrategyGeneratorAgent
        strategy_code = await strategy_generator.generate_strategy(
            symbol=request.symbol,
            indicators=request.indicators,
            timeframe=request.timeframe,
            risk_level=request.risk_level,
            capital=request.capital
        )
        
        return {
            "status": "success",
            "strategy_code": strategy_code,
            "message": "Strategy generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest-strategy")
async def backtest_strategy(request: BacktestRequest) -> Dict[str, Any]:
    """Run backtest on a strategy"""
    try:
        # Run backtest using BacktestAgent
        backtest_results = await backtest_agent.run_backtest(
            strategy_code=request.strategy_code,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital
        )
        
        return {
            "status": "success",
            "backtest_results": backtest_results,
            "message": "Backtest completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate-strategy")
async def evaluate_strategy(backtest_results: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate strategy performance using EvaluatorAgent"""
    try:
        evaluation = await evaluator_agent.evaluate_strategy(backtest_results)
        
        return {
            "status": "success",
            "evaluation": evaluation,
            "message": "Strategy evaluation completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute-trade")
async def execute_trade(request: TradingRequest) -> Dict[str, Any]:
    """Execute a trade with risk management"""
    try:
        # Check risk management rules
        risk_check = await risk_manager.check_risk(
            strategy_id=request.strategy_id,
            symbol=request.symbol,
            quantity=request.quantity
        )
        
        if not risk_check["approved"]:
            return {
                "status": "rejected",
                "reason": risk_check["reason"],
                "message": "Trade rejected by risk manager"
            }
        
        # Execute trade
        trade_result = await strategy_service.execute_trade(
            strategy_id=request.strategy_id,
            symbol=request.symbol,
            quantity=request.quantity,
            order_type=request.order_type
        )
        
        return {
            "status": "success",
            "trade_result": trade_result,
            "message": "Trade executed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 