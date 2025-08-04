import asyncio
from typing import Dict, Any, List
from datetime import datetime
import uuid

class StrategyService:
    def __init__(self):
        self.active_strategies = {}
        self.trade_history = []
        self.portfolio = {
            "cash": 100000,
            "positions": {},
            "total_value": 100000
        }
    
    async def execute_trade(
        self,
        strategy_id: str,
        symbol: str,
        quantity: int,
        order_type: str = "MARKET"
    ) -> Dict[str, Any]:
        """
        Execute a trade through the strategy service
        """
        try:
            # Get current market price
            current_price = await self._get_market_price(symbol)
            
            # Calculate trade details
            trade_value = quantity * current_price
            trade_id = str(uuid.uuid4())
            
            # Check if we have sufficient cash
            if order_type == "BUY" and trade_value > self.portfolio["cash"]:
                return {
                    "status": "failed",
                    "reason": "Insufficient cash",
                    "required": trade_value,
                    "available": self.portfolio["cash"]
                }
            
            # Execute the trade
            if order_type == "BUY":
                # Buy order
                if symbol not in self.portfolio["positions"]:
                    self.portfolio["positions"][symbol] = {
                        "quantity": 0,
                        "avg_price": 0,
                        "total_cost": 0
                    }
                
                position = self.portfolio["positions"][symbol]
                old_quantity = position["quantity"]
                old_avg_price = position["avg_price"]
                
                new_quantity = old_quantity + quantity
                new_avg_price = ((old_quantity * old_avg_price) + (quantity * current_price)) / new_quantity
                
                position["quantity"] = new_quantity
                position["avg_price"] = new_avg_price
                position["total_cost"] = new_quantity * new_avg_price
                
                self.portfolio["cash"] -= trade_value
                
            elif order_type == "SELL":
                # Sell order
                if symbol not in self.portfolio["positions"] or self.portfolio["positions"][symbol]["quantity"] < quantity:
                    return {
                        "status": "failed",
                        "reason": "Insufficient shares to sell",
                        "requested": quantity,
                        "available": self.portfolio["positions"].get(symbol, {}).get("quantity", 0)
                    }
                
                position = self.portfolio["positions"][symbol]
                position["quantity"] -= quantity
                
                if position["quantity"] == 0:
                    del self.portfolio["positions"][symbol]
                
                self.portfolio["cash"] += trade_value
            
            # Record the trade
            trade_record = {
                "trade_id": trade_id,
                "strategy_id": strategy_id,
                "symbol": symbol,
                "quantity": quantity,
                "price": current_price,
                "order_type": order_type,
                "trade_value": trade_value,
                "timestamp": datetime.now().isoformat(),
                "status": "executed"
            }
            
            self.trade_history.append(trade_record)
            
            # Update portfolio total value
            await self._update_portfolio_value()
            
            return {
                "status": "success",
                "trade_id": trade_id,
                "trade_details": trade_record,
                "portfolio_summary": self._get_portfolio_summary()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "trade_id": None
            }
    
    async def _get_market_price(self, symbol: str) -> float:
        """Get current market price for a symbol"""
        # Mock prices - in production, this would use Zerodha API
        mock_prices = {
            "AAPL": 150.0,
            "GOOGL": 2800.0,
            "MSFT": 300.0,
            "TSLA": 250.0,
            "AMZN": 3300.0,
            "NFLX": 500.0,
            "META": 350.0,
            "NVDA": 800.0
        }
        return mock_prices.get(symbol, 100.0)
    
    async def _update_portfolio_value(self):
        """Update total portfolio value"""
        total_value = self.portfolio["cash"]
        
        for symbol, position in self.portfolio["positions"].items():
            if position["quantity"] > 0:
                current_price = await self._get_market_price(symbol)
                position_value = position["quantity"] * current_price
                total_value += position_value
        
        self.portfolio["total_value"] = total_value
    
    def _get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio summary"""
        return {
            "cash": self.portfolio["cash"],
            "total_value": self.portfolio["total_value"],
            "positions": len([p for p in self.portfolio["positions"].values() if p["quantity"] > 0]),
            "total_trades": len(self.trade_history)
        }
    
    async def get_strategy_performance(self, strategy_id: str) -> Dict[str, Any]:
        """Get performance metrics for a specific strategy"""
        strategy_trades = [t for t in self.trade_history if t["strategy_id"] == strategy_id]
        
        if not strategy_trades:
            return {
                "status": "no_trades",
                "message": "No trades found for this strategy"
            }
        
        # Calculate performance metrics
        total_buy_value = sum(t["trade_value"] for t in strategy_trades if t["order_type"] == "BUY")
        total_sell_value = sum(t["trade_value"] for t in strategy_trades if t["order_type"] == "SELL")
        
        net_pnl = total_sell_value - total_buy_value
        total_trades = len(strategy_trades)
        
        return {
            "strategy_id": strategy_id,
            "total_trades": total_trades,
            "buy_trades": len([t for t in strategy_trades if t["order_type"] == "BUY"]),
            "sell_trades": len([t for t in strategy_trades if t["order_type"] == "SELL"]),
            "total_buy_value": total_buy_value,
            "total_sell_value": total_sell_value,
            "net_pnl": net_pnl,
            "return_pct": (net_pnl / total_buy_value * 100) if total_buy_value > 0 else 0,
            "trades": strategy_trades
        }
    
    async def get_portfolio_status(self) -> Dict[str, Any]:
        """Get current portfolio status"""
        await self._update_portfolio_value()
        
        positions_summary = []
        for symbol, position in self.portfolio["positions"].items():
            if position["quantity"] > 0:
                current_price = await self._get_market_price(symbol)
                position_value = position["quantity"] * current_price
                unrealized_pnl = position_value - position["total_cost"]
                unrealized_pnl_pct = (unrealized_pnl / position["total_cost"] * 100) if position["total_cost"] > 0 else 0
                
                positions_summary.append({
                    "symbol": symbol,
                    "quantity": position["quantity"],
                    "avg_price": position["avg_price"],
                    "current_price": current_price,
                    "position_value": position_value,
                    "unrealized_pnl": unrealized_pnl,
                    "unrealized_pnl_pct": unrealized_pnl_pct
                })
        
        return {
            "cash": self.portfolio["cash"],
            "total_value": self.portfolio["total_value"],
            "positions": positions_summary,
            "total_positions": len(positions_summary),
            "total_trades": len(self.trade_history)
        }
    
    async def register_strategy(self, strategy_id: str, strategy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new trading strategy"""
        self.active_strategies[strategy_id] = {
            "config": strategy_config,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "trades": []
        }
        
        return {
            "status": "success",
            "strategy_id": strategy_id,
            "message": "Strategy registered successfully"
        }
    
    async def deactivate_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Deactivate a trading strategy"""
        if strategy_id in self.active_strategies:
            self.active_strategies[strategy_id]["status"] = "inactive"
            return {
                "status": "success",
                "message": "Strategy deactivated successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Strategy not found"
            }
    
    def get_trade_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trade history"""
        return self.trade_history[-limit:] if self.trade_history else []
    
    async def calculate_position_size(self, symbol: str, confidence: float, available_cash: float) -> int:
        """Calculate optimal position size based on confidence and available cash"""
        current_price = await self._get_market_price(symbol)
        
        # Base position size on confidence (0-1)
        max_position_value = available_cash * confidence * 0.1  # Use 10% of available cash * confidence
        
        # Ensure we don't exceed available cash
        max_position_value = min(max_position_value, available_cash * 0.2)  # Max 20% of cash
        
        quantity = int(max_position_value / current_price)
        
        return max(1, quantity)  # Minimum 1 share 