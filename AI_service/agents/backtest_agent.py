import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, List
import asyncio
import exec
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

class BacktestAgent:
    def __init__(self):
        self.results = {}
        
    async def run_backtest(
        self,
        strategy_code: str,
        symbol: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 100000
    ) -> Dict[str, Any]:
        """
        Run backtest on a trading strategy
        """
        try:
            # Download historical data
            data = await self._get_historical_data(symbol, start_date, end_date)
            
            # Execute strategy code
            strategy_func = await self._compile_strategy(strategy_code)
            
            # Run backtest
            backtest_results = await self._execute_backtest(
                data, strategy_func, initial_capital
            )
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(backtest_results)
            
            return {
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "initial_capital": initial_capital,
                "final_capital": backtest_results["final_capital"],
                "total_return": backtest_results["total_return"],
                "performance_metrics": performance_metrics,
                "trades": backtest_results["trades"],
                "equity_curve": backtest_results["equity_curve"]
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def _get_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Download historical data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            # Ensure we have the required columns
            if data.empty:
                raise ValueError(f"No data found for {symbol}")
            
            # Reset index to make date a column
            data = data.reset_index()
            
            return data
            
        except Exception as e:
            raise Exception(f"Failed to download data for {symbol}: {str(e)}")
    
    async def _compile_strategy(self, strategy_code: str):
        """Compile and return the strategy function"""
        try:
            # Create a namespace for the strategy
            namespace = {}
            
            # Execute the strategy code
            exec(strategy_code, namespace)
            
            # Get the trading strategy function
            if 'trading_strategy' not in namespace:
                raise ValueError("Strategy code must define a 'trading_strategy' function")
            
            return namespace['trading_strategy']
            
        except Exception as e:
            raise Exception(f"Failed to compile strategy: {str(e)}")
    
    async def _execute_backtest(
        self,
        data: pd.DataFrame,
        strategy_func,
        initial_capital: float
    ) -> Dict[str, Any]:
        """Execute the backtest"""
        
        capital = initial_capital
        position = 0
        trades = []
        equity_curve = []
        
        for i in range(len(data)):
            current_data = data.iloc[:i+1]
            
            if len(current_data) < 20:  # Need minimum data for indicators
                continue
            
            try:
                # Get strategy signal
                strategy_result = strategy_func(current_data, capital, "medium")
                
                signal = strategy_result.get('signal', 'HOLD')
                confidence = strategy_result.get('confidence', 0.5)
                position_size = strategy_result.get('position_size', capital * 0.1)
                
                current_price = current_data.iloc[-1]['Close']
                current_date = current_data.iloc[-1]['Date']
                
                # Execute trades based on signal
                if signal == 'BUY' and position == 0 and confidence > 0.6:
                    shares = int(position_size / current_price)
                    if shares > 0:
                        position = shares
                        cost = shares * current_price
                        capital -= cost
                        
                        trades.append({
                            'date': current_date,
                            'action': 'BUY',
                            'shares': shares,
                            'price': current_price,
                            'cost': cost,
                            'confidence': confidence
                        })
                
                elif signal == 'SELL' and position > 0 and confidence > 0.6:
                    revenue = position * current_price
                    capital += revenue
                    
                    trades.append({
                        'date': current_date,
                        'action': 'SELL',
                        'shares': position,
                        'price': current_price,
                        'revenue': revenue,
                        'confidence': confidence
                    })
                    
                    position = 0
                
                # Calculate current portfolio value
                portfolio_value = capital + (position * current_price)
                equity_curve.append({
                    'date': current_date,
                    'portfolio_value': portfolio_value,
                    'capital': capital,
                    'position': position,
                    'price': current_price
                })
                
            except Exception as e:
                print(f"Error in strategy execution: {e}")
                continue
        
        # Close any remaining position
        if position > 0:
            final_price = data.iloc[-1]['Close']
            final_revenue = position * final_price
            capital += final_revenue
            
            trades.append({
                'date': data.iloc[-1]['Date'],
                'action': 'SELL',
                'shares': position,
                'price': final_price,
                'revenue': final_revenue,
                'confidence': 1.0
            })
        
        final_capital = capital
        total_return = ((final_capital - initial_capital) / initial_capital) * 100
        
        return {
            "final_capital": final_capital,
            "total_return": total_return,
            "trades": trades,
            "equity_curve": equity_curve,
            "initial_capital": initial_capital
        }
    
    def _calculate_performance_metrics(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        
        equity_curve = backtest_results["equity_curve"]
        trades = backtest_results["trades"]
        total_return = backtest_results["total_return"]
        
        if not equity_curve:
            return {"error": "No equity curve data"}
        
        # Convert to DataFrame for easier calculations
        equity_df = pd.DataFrame(equity_curve)
        equity_df['returns'] = equity_df['portfolio_value'].pct_change()
        
        # Calculate metrics
        metrics = {}
        
        # Basic metrics
        metrics['total_return'] = total_return
        metrics['final_value'] = backtest_results["final_capital"]
        metrics['total_trades'] = len(trades)
        
        # Risk metrics
        if len(equity_df) > 1:
            returns = equity_df['returns'].dropna()
            
            # Volatility
            metrics['volatility'] = returns.std() * np.sqrt(252) * 100  # Annualized
            
            # Sharpe Ratio (assuming risk-free rate of 2%)
            risk_free_rate = 0.02
            excess_returns = returns - (risk_free_rate / 252)
            if excess_returns.std() > 0:
                metrics['sharpe_ratio'] = (excess_returns.mean() * 252) / (excess_returns.std() * np.sqrt(252))
            else:
                metrics['sharpe_ratio'] = 0
            
            # Maximum Drawdown
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            metrics['max_drawdown'] = drawdown.min() * 100
            
            # Win rate
            if trades:
                profitable_trades = [t for t in trades if t.get('revenue', 0) > t.get('cost', 0)]
                metrics['win_rate'] = (len(profitable_trades) / len(trades)) * 100
            else:
                metrics['win_rate'] = 0
        
        return metrics 