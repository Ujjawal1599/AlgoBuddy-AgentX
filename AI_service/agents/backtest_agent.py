import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, List
import asyncio
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
import warnings
import quandl

# Disable pandas SettingWithCopyWarning
pd.options.mode.chained_assignment = None
# Alternative: warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
# For specific functions, use: with warnings.catch_warnings(): warnings.simplefilter("ignore")

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
        """Download historical data from multiple sources"""
        try:
            # Try multiple data sources (Quandl temporarily disabled due to 403 errors)
            data_sources = [
                ("Yahoo Finance", self._get_yahoo_data),
                ("Alpha Vantage", self._get_alpha_vantage_data),
                ("CSV Data", self._get_csv_data)
                # ("Quandl", self._get_quandl_data),  # Temporarily disabled
            ]
            
            for source_name, data_func in data_sources:
                try:
                    print(f"Trying {source_name} for {symbol}...")
                    data = await data_func(symbol, start_date, end_date)
                    if not data.empty:
                        print(f"✓ Successfully got data from {source_name}")
                        return data
                except Exception as e:
                    print(f"✗ {source_name} failed: {e}")
                    continue
            
            raise ValueError(f"No data found for {symbol} from any data source")
            
        except Exception as e:
            print(f"Error in _get_historical_data: {e}")
            raise Exception(f"Failed to download data for {symbol}: {str(e)}")
    
    async def _get_yahoo_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get data from Yahoo Finance with robust error handling"""
        try:
            import yfinance as yf
            
            # Map Indian stock symbols to Yahoo Finance format
            indian_symbol_mapping = {
                "RELIANCE": "RELIANCE.NS",
                "TCS": "TCS.NS", 
                "HDFCBANK": "HDFCBANK.NS",
                "INFY": "INFY.NS",
                "ICICIBANK": "ICICIBANK.NS",
                "HINDUNILVR": "HINDUNILVR.NS",
                "ITC": "ITC.NS",
                "SBIN": "SBIN.NS",
                "BHARTIARTL": "BHARTIARTL.NS",
                "AXISBANK": "AXISBANK.NS",
                "ASIANPAINT": "ASIANPAINT.NS",
                "MARUTI": "MARUTI.NS",
                "HCLTECH": "HCLTECH.NS",
                "SUNPHARMA": "SUNPHARMA.NS",
                "WIPRO": "WIPRO.NS",
                "ULTRACEMCO": "ULTRACEMCO.NS",
                "TITAN": "TITAN.NS",
                "BAJFINANCE": "BAJFINANCE.NS",
                "NESTLEIND": "NESTLEIND.NS",
                "POWERGRID": "POWERGRID.NS"
            }
            
            # US stock symbols (no suffix needed)
            us_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]
            
            # Determine the correct symbol format
            if symbol in indian_symbol_mapping:
                yahoo_symbol = indian_symbol_mapping[symbol]
            elif symbol in us_symbols or symbol.endswith(('.US', '.O', '.N')):
                # US stocks - use symbol as is
                yahoo_symbol = symbol
            else:
                # Try as US stock first, then as Indian stock
                yahoo_symbol = symbol
            
            print(f"Trying Yahoo Finance with symbol: {yahoo_symbol}")
            
            # Try multiple symbol variations for US stocks
            symbols_to_try = [yahoo_symbol]
            if symbol in us_symbols:
                symbols_to_try.extend([f"{symbol}.US", f"{symbol}.O"])
            
            for try_symbol in symbols_to_try:
                try:
                    print(f"  Attempting with symbol: {try_symbol}")
                    
                    # Add delay to avoid rate limiting
                    import time
                    time.sleep(1.0)
                    
                    ticker = yf.Ticker(try_symbol)
                    
                    # Try to get basic info first (with timeout)
                    try:
                        info = ticker.info
                        if info and 'regularMarketPrice' in info and info['regularMarketPrice']:
                            print(f"  ✓ Symbol {try_symbol} is valid")
                        else:
                            print(f"  ✗ Invalid symbol: {try_symbol}")
                            continue
                    except Exception as e:
                        print(f"  ⚠️  Could not validate {try_symbol}: {e}")
                        # Continue anyway, sometimes info fails but history works
                    
                    # Get historical data with error handling
                    data = ticker.history(start=start_date, end=end_date)
                    
                    if not data.empty:
                        print(f"  ✓ Successfully got {len(data)} data points from Yahoo Finance")
                        return data.reset_index()
                    else:
                        print(f"  ✗ No historical data for {try_symbol}")
                        
                except Exception as e:
                    print(f"  ✗ Failed for {try_symbol}: {e}")
                    continue
            
            # If all symbols failed, try one more time with basic approach
            try:
                print("  🔄 Trying basic approach...")
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date, progress=False)
                
                if not data.empty:
                    print(f"  ✓ Basic approach worked: {len(data)} data points")
                    return data.reset_index()
                else:
                    raise ValueError(f"No data from Yahoo Finance for {symbol}")
                    
            except Exception as e:
                raise Exception(f"All Yahoo Finance attempts failed for {symbol}: {e}")
                
        except Exception as e:
            raise Exception(f"Yahoo Finance failed: {e}")
    
    async def _get_csv_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get data from CSV files (if available)"""
        try:
            import os
            csv_path = f"data/{symbol}.csv"
            if os.path.exists(csv_path):
                data = pd.read_csv(csv_path)
                data['Date'] = pd.to_datetime(data['Date'])
                data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
                return data
            else:
                raise ValueError("CSV file not found")
        except Exception as e:
            raise Exception(f"CSV data failed: {e}")
    
    async def _get_alpha_vantage_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get data from Alpha Vantage API using TIME_SERIES_INTRADAY"""
        try:
            import requests
            import os
            
            api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
            print('api_key',api_key)
            if not api_key:
                print("Alpha Vantage API key not found. Skipping Alpha Vantage.")
                raise ValueError("Alpha Vantage API key not found")
            
            # Alpha Vantage symbol mapping for stocks
            alpha_vantage_symbols = {
                # Indian stocks
                "TCS": "TCS",  # This one works
                "INFY": "INFY",  # Try without prefix
                "WIPRO": "WIPRO",
                "HCLTECH": "HCLTECH",
                "SUNPHARMA": "SUNPHARMA",
                "TITAN": "TITAN",
                "NESTLEIND": "NESTLEIND",
                "RELIANCE": "RELIANCE.BSE",
                # US stocks
                "AAPL": "AAPL",
                "MSFT": "MSFT",
                "GOOGL": "GOOGL",
                "AMZN": "AMZN",
                "TSLA": "TSLA",
                "META": "META",
                "NVDA": "NVDA",
                "NFLX": "NFLX",
                "AMD": "AMD",
                "INTC": "INTC"
            }
            
            alpha_symbol = alpha_vantage_symbols.get(symbol, symbol)  # Try without prefix first
            print(f"Trying Alpha Vantage INTRADAY with symbol: {alpha_symbol}")
            
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": alpha_symbol,
                "interval": "5min",  # 5-minute intervals
                "apikey": api_key,
                "outputsize": "full",  # Get full data
                "adjusted": "true",  # Get adjusted data
                "extended_hours": "false"  # Regular trading hours only
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            print('data',data)
            if "Time Series (5min)" in data:
                time_series = data["Time Series (5min)"]
                df_data = []
                
                for timestamp, values in time_series.items():
                    # Convert timestamp to datetime
                    dt = pd.to_datetime(timestamp)
                    date_str = dt.strftime('%Y-%m-%d')
                    
                    # Check if date is within range
                    if start_date <= date_str <= end_date:
                        df_data.append({
                            'Date': dt,
                            'Open': float(values['1. open']),
                            'High': float(values['2. high']),
                            'Low': float(values['3. low']),
                            'Close': float(values['4. close']),
                            'Volume': int(values['5. volume'])
                        })
                
                if df_data:
                    df = pd.DataFrame(df_data)
                    # Sort by date
                    df = df.sort_values('Date')
                    print(f"Successfully got {len(df)} intraday data points from Alpha Vantage")
                    return df
                else:
                    raise ValueError("No data found in specified date range")
            else:
                error_msg = data.get("Error Message", "Unknown error")
                print(f"Alpha Vantage returned error: {error_msg}")
                raise ValueError(f"Alpha Vantage error: {error_msg}")
                
        except Exception as e:
            raise Exception(f"Alpha Vantage failed: {e}")

    
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