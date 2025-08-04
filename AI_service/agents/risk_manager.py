import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio

class RiskManagerAgent:
    def __init__(self):
        # Risk management parameters
        self.max_position_size = 0.1  # Maximum 10% of portfolio per position
        self.max_portfolio_risk = 0.02  # Maximum 2% portfolio risk per trade
        self.max_daily_loss = 0.05  # Maximum 5% daily loss
        self.max_drawdown = 0.15  # Maximum 15% drawdown
        self.stop_loss_pct = 0.02  # 2% stop loss
        self.take_profit_pct = 0.06  # 6% take profit
        
        # Portfolio tracking
        self.portfolio_value = 100000
        self.positions = {}
        self.daily_pnl = 0
        self.max_portfolio_value = 100000
        
    async def check_risk(
        self,
        strategy_id: str,
        symbol: str,
        quantity: int,
        price: float = None
    ) -> Dict[str, Any]:
        """
        Check if a trade meets risk management criteria
        """
        try:
            # Get current market price if not provided
            if price is None:
                price = await self._get_current_price(symbol)
            
            trade_value = quantity * price
            position_risk = trade_value / self.portfolio_value
            
            # Check various risk criteria
            checks = {
                "position_size": self._check_position_size(position_risk),
                "portfolio_risk": self._check_portfolio_risk(trade_value),
                "daily_loss": self._check_daily_loss_limit(),
                "drawdown": self._check_drawdown_limit(),
                "exposure": self._check_total_exposure(symbol, trade_value)
            }
            
            # Determine if trade is approved
            all_checks_passed = all(check["approved"] for check in checks.values())
            
            if all_checks_passed:
                # Update portfolio tracking
                await self._update_position(symbol, quantity, price, strategy_id)
                
                return {
                    "approved": True,
                    "reason": "All risk checks passed",
                    "checks": checks,
                    "position_risk": position_risk,
                    "trade_value": trade_value
                }
            else:
                failed_checks = [name for name, check in checks.items() if not check["approved"]]
                return {
                    "approved": False,
                    "reason": f"Failed risk checks: {', '.join(failed_checks)}",
                    "checks": checks,
                    "position_risk": position_risk,
                    "trade_value": trade_value
                }
                
        except Exception as e:
            return {
                "approved": False,
                "reason": f"Risk check error: {str(e)}",
                "error": str(e)
            }
    
    def _check_position_size(self, position_risk: float) -> Dict[str, Any]:
        """Check if position size is within limits"""
        if position_risk <= self.max_position_size:
            return {
                "approved": True,
                "message": f"Position size {position_risk:.2%} within limit {self.max_position_size:.1%}"
            }
        else:
            return {
                "approved": False,
                "message": f"Position size {position_risk:.2%} exceeds limit {self.max_position_size:.1%}"
            }
    
    def _check_portfolio_risk(self, trade_value: float) -> Dict[str, Any]:
        """Check if trade risk is within portfolio limits"""
        portfolio_risk = trade_value * self.stop_loss_pct / self.portfolio_value
        
        if portfolio_risk <= self.max_portfolio_risk:
            return {
                "approved": True,
                "message": f"Portfolio risk {portfolio_risk:.2%} within limit {self.max_portfolio_risk:.1%}"
            }
        else:
            return {
                "approved": False,
                "message": f"Portfolio risk {portfolio_risk:.2%} exceeds limit {self.max_portfolio_risk:.1%}"
            }
    
    def _check_daily_loss_limit(self) -> Dict[str, Any]:
        """Check if daily loss limit is exceeded"""
        daily_loss_pct = self.daily_pnl / self.portfolio_value
        
        if daily_loss_pct >= -self.max_daily_loss:
            return {
                "approved": True,
                "message": f"Daily loss {daily_loss_pct:.2%} within limit {-self.max_daily_loss:.1%}"
            }
        else:
            return {
                "approved": False,
                "message": f"Daily loss {daily_loss_pct:.2%} exceeds limit {-self.max_daily_loss:.1%}"
            }
    
    def _check_drawdown_limit(self) -> Dict[str, Any]:
        """Check if drawdown limit is exceeded"""
        current_drawdown = (self.max_portfolio_value - self.portfolio_value) / self.max_portfolio_value
        
        if current_drawdown <= self.max_drawdown:
            return {
                "approved": True,
                "message": f"Drawdown {current_drawdown:.2%} within limit {self.max_drawdown:.1%}"
            }
        else:
            return {
                "approved": False,
                "message": f"Drawdown {current_drawdown:.2%} exceeds limit {self.max_drawdown:.1%}"
            }
    
    def _check_total_exposure(self, symbol: str, trade_value: float) -> Dict[str, Any]:
        """Check total exposure to a symbol"""
        current_exposure = self.positions.get(symbol, {}).get("value", 0)
        total_exposure = current_exposure + trade_value
        exposure_pct = total_exposure / self.portfolio_value
        
        max_exposure = self.max_position_size * 2  # Allow up to 2x position size for same symbol
        
        if exposure_pct <= max_exposure:
            return {
                "approved": True,
                "message": f"Total exposure {exposure_pct:.2%} within limit {max_exposure:.1%}"
            }
        else:
            return {
                "approved": False,
                "message": f"Total exposure {exposure_pct:.2%} exceeds limit {max_exposure:.1%}"
            }
    
    async def _get_current_price(self, symbol: str) -> float:
        """Get current market price for a symbol"""
        # This would integrate with Zerodha API in production
        # For now, return a mock price
        mock_prices = {
            "AAPL": 150.0,
            "GOOGL": 2800.0,
            "MSFT": 300.0,
            "TSLA": 250.0,
            "AMZN": 3300.0
        }
        return mock_prices.get(symbol, 100.0)
    
    async def _update_position(self, symbol: str, quantity: int, price: float, strategy_id: str):
        """Update position tracking"""
        if symbol not in self.positions:
            self.positions[symbol] = {
                "quantity": 0,
                "avg_price": 0,
                "value": 0,
                "strategies": []
            }
        
        position = self.positions[symbol]
        
        # Update position
        old_quantity = position["quantity"]
        old_avg_price = position["avg_price"]
        
        new_quantity = old_quantity + quantity
        new_avg_price = ((old_quantity * old_avg_price) + (quantity * price)) / new_quantity if new_quantity != 0 else 0
        
        position["quantity"] = new_quantity
        position["avg_price"] = new_avg_price
        position["value"] = new_quantity * price
        position["strategies"].append(strategy_id)
    
    async def monitor_positions(self) -> Dict[str, Any]:
        """Monitor all open positions for risk management"""
        alerts = []
        
        for symbol, position in self.positions.items():
            if position["quantity"] == 0:
                continue
            
            current_price = await self._get_current_price(symbol)
            position_value = position["quantity"] * current_price
            unrealized_pnl = position_value - (position["quantity"] * position["avg_price"])
            unrealized_pnl_pct = unrealized_pnl / (position["quantity"] * position["avg_price"])
            
            # Check stop loss
            if unrealized_pnl_pct <= -self.stop_loss_pct:
                alerts.append({
                    "symbol": symbol,
                    "type": "STOP_LOSS",
                    "message": f"Stop loss triggered for {symbol} at {unrealized_pnl_pct:.2%}",
                    "action": "SELL",
                    "quantity": position["quantity"]
                })
            
            # Check take profit
            elif unrealized_pnl_pct >= self.take_profit_pct:
                alerts.append({
                    "symbol": symbol,
                    "type": "TAKE_PROFIT",
                    "message": f"Take profit triggered for {symbol} at {unrealized_pnl_pct:.2%}",
                    "action": "SELL",
                    "quantity": position["quantity"]
                })
        
        return {
            "alerts": alerts,
            "total_positions": len([p for p in self.positions.values() if p["quantity"] != 0]),
            "portfolio_value": self.portfolio_value,
            "daily_pnl": self.daily_pnl
        }
    
    async def calculate_position_size(self, symbol: str, price: float, confidence: float) -> int:
        """Calculate optimal position size based on risk parameters"""
        # Base position size on confidence and risk limits
        base_risk = self.max_portfolio_risk * confidence
        max_position_value = self.portfolio_value * base_risk / self.stop_loss_pct
        
        # Ensure position size doesn't exceed limits
        max_position_value = min(max_position_value, self.portfolio_value * self.max_position_size)
        
        # Calculate quantity
        quantity = int(max_position_value / price)
        
        return max(1, quantity)  # Minimum 1 share
    
    async def update_portfolio_value(self, new_value: float):
        """Update portfolio value and track drawdown"""
        self.portfolio_value = new_value
        self.max_portfolio_value = max(self.max_portfolio_value, new_value)
    
    async def update_daily_pnl(self, pnl: float):
        """Update daily P&L"""
        self.daily_pnl = pnl
    
    async def reset_daily_limits(self):
        """Reset daily limits (call at start of trading day)"""
        self.daily_pnl = 0
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get current risk summary"""
        current_drawdown = (self.max_portfolio_value - self.portfolio_value) / self.max_portfolio_value
        daily_loss_pct = self.daily_pnl / self.portfolio_value
        
        return {
            "portfolio_value": self.portfolio_value,
            "max_portfolio_value": self.max_portfolio_value,
            "current_drawdown": current_drawdown,
            "daily_pnl": self.daily_pnl,
            "daily_loss_pct": daily_loss_pct,
            "total_positions": len([p for p in self.positions.values() if p["quantity"] != 0]),
            "risk_limits": {
                "max_position_size": self.max_position_size,
                "max_portfolio_risk": self.max_portfolio_risk,
                "max_daily_loss": self.max_daily_loss,
                "max_drawdown": self.max_drawdown,
                "stop_loss_pct": self.stop_loss_pct,
                "take_profit_pct": self.take_profit_pct
            }
        } 