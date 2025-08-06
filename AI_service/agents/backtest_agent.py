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
    
    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to lowercase for consistency"""
        if df.empty:
            return df
        
        # Create a copy to avoid modifying original
        df_std = df.copy()
        
        # Standardize column names to lowercase
        column_mapping = {
            'Date': 'date',
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Adj Close': 'adj_close'
        }
        
        # Rename columns that exist
        for old_name, new_name in column_mapping.items():
            if old_name in df_std.columns:
                df_std = df_std.rename(columns={old_name: new_name})
        
        # Ensure required columns exist
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df_std.columns]
        
        if missing_columns:
            print(f"⚠️  Missing columns: {missing_columns}")
            # Try to map from existing columns
            if 'Close' in df_std.columns and 'close' not in df_std.columns:
                df_std['close'] = df_std['Close']
            if 'Open' in df_std.columns and 'open' not in df_std.columns:
                df_std['open'] = df_std['Open']
            if 'High' in df_std.columns and 'high' not in df_std.columns:
                df_std['high'] = df_std['High']
            if 'Low' in df_std.columns and 'low' not in df_std.columns:
                df_std['low'] = df_std['Low']
            if 'Volume' in df_std.columns and 'volume' not in df_std.columns:
                df_std['volume'] = df_std['Volume']
        
        # Final check for required columns
        final_missing = [col for col in required_columns if col not in df_std.columns]
        if final_missing:
            raise ValueError(f"Missing required columns after standardization: {final_missing}")
        
        print(f"✅ Standardized columns: {list(df_std.columns)}")
        return df_std

    async def _get_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Download historical data from multiple sources"""
        try:
            # Prioritize data sources by reliability
            data_sources = [
                ("Yahoo Finance", self._get_yahoo_data),  # Most reliable for most symbols
                # ("CSV Data", self._get_csv_data),        # Good fallback with mock data
                ("Alpha Vantage", self._get_alpha_vantage_data)  # Requires API key, rate limited
                # ("Quandl", self._get_quandl_data),  # Temporarily disabled
            ]
            
            errors = []
            for source_name, data_func in data_sources:
                try:
                    print(f"🔄 Trying {source_name} for {symbol}...")
                    data = await data_func(symbol, start_date, end_date)
                    if not data.empty and len(data) > 0:
                        # Standardize column names
                        data = self._standardize_column_names(data)
                        print(f"✅ Successfully got {len(data)} data points from {source_name}")
                        return data
                    else:
                        print(f"⚠️  {source_name} returned empty data")
                        errors.append(f"{source_name}: Empty data")
                except Exception as e:
                    error_msg = f"{source_name}: {str(e)}"
                    print(f"❌ {error_msg}")
                    errors.append(error_msg)
                    continue
            
            # If all sources failed, provide helpful error message
            error_summary = "\n".join(errors)
            raise ValueError(f"No data found for {symbol} from any data source.\nErrors:\n{error_summary}")
            
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
        """Get data from CSV files or generate mock data as fallback"""
        try:
            import os
            import numpy as np
            from datetime import datetime, timedelta
            
            csv_path = f"data/{symbol}.csv"
            if os.path.exists(csv_path):
                print(f"📁 Found CSV file: {csv_path}")
                data = pd.read_csv(csv_path)
                data['Date'] = pd.to_datetime(data['Date'])
                data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
                if len(data) > 0:
                    return data
                else:
                    print(f"⚠️  CSV file exists but no data in date range {start_date} to {end_date}")
            
            # Generate mock data as reliable fallback
            print(f"🔄 Generating mock data for {symbol} from {start_date} to {end_date}")
            
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Generate daily data points
            dates = []
            current_date = start_dt
            while current_date <= end_dt:
                if current_date.weekday() < 5:  # Monday to Friday only
                    dates.append(current_date)
                current_date += timedelta(days=1)
            
            if not dates:
                raise ValueError("No trading days in date range")
            
            # Generate realistic price data
            np.random.seed(hash(symbol) % 1000)  # Consistent seed for same symbol
            
            # Base price varies by symbol
            base_prices = {
                "AAPL": 150, "GOOGL": 2800, "MSFT": 300, "TSLA": 250,
                "AMZN": 3300, "META": 350, "NVDA": 800, "NFLX": 500,
                "TCS": 3500, "INFY": 1500, "RELIANCE": 2500, "HDFCBANK": 1600
            }
            base_price = base_prices.get(symbol, 100)
            
            # Generate price series with realistic volatility
            prices = [base_price]
            for i in range(1, len(dates)):
                # Daily return with some volatility
                daily_return = np.random.normal(0.001, 0.02)  # 0.1% mean, 2% std
                new_price = prices[-1] * (1 + daily_return)
                prices.append(max(new_price, base_price * 0.5))  # Prevent negative prices
            
            # Generate OHLCV data
            data_points = []
            for i, (date, close_price) in enumerate(zip(dates, prices)):
                # Generate realistic OHLC from close price
                volatility = np.random.uniform(0.01, 0.03)
                high = close_price * (1 + np.random.uniform(0, volatility))
                low = close_price * (1 - np.random.uniform(0, volatility))
                open_price = prices[i-1] if i > 0 else close_price
                volume = np.random.randint(1000000, 10000000)
                
                data_points.append({
                    'Date': date,
                    'Open': round(open_price, 2),
                    'High': round(high, 2),
                    'Low': round(low, 2),
                    'Close': round(close_price, 2),
                    'Volume': volume
                })
            
            df = pd.DataFrame(data_points)
            print(f"✅ Generated {len(df)} mock data points for {symbol}")
            return df
            
        except Exception as e:
            raise Exception(f"CSV data failed: {e}")
    
    async def _get_alpha_vantage_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get data from Alpha Vantage API using TIME_SERIES_DAILY"""
        try:
            import requests
            import os
            
            api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
            print('Alpha Vantage API key found:', bool(api_key))
            if not api_key:
                print("Alpha Vantage API key not found. Skipping Alpha Vantage.")
                raise ValueError("Alpha Vantage API key not found")
            
            # Alpha Vantage symbol mapping for stocks
            alpha_vantage_symbols = {
                # Indian stocks
                "TCS": "TCS.BSE",  # Add exchange suffix for Indian stocks
                "INFY": "INFY.BSE",
                "WIPRO": "WIPRO.BSE",
                "HCLTECH": "HCLTECH.BSE",
                "SUNPHARMA": "SUNPHARMA.BSE",
                "TITAN": "TITAN.BSE",
                "NESTLEIND": "NESTLEIND.BSE",
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
            
            alpha_symbol = alpha_vantage_symbols.get(symbol, symbol)
            print(f"Trying Alpha Vantage DAILY with symbol: {alpha_symbol}")
            
            # Use TIME_SERIES_DAILY instead of INTRADAY to avoid rate limits
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": alpha_symbol,
                "outputsize": "full",  # Get full history
                "apikey": api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            print('response',response)
            if response.status_code != 200:
                raise ValueError(f"Alpha Vantage API returned status code: {response.status_code}")
            
            data = response.json()
            print('dataaaaaaaaaaa',data)
            print('Alpha Vantage response keys:', list(data.keys()))
            
            # Check for API errors
            if "Error Message" in data:
                error_msg = data["Error Message"]
                print(f"Alpha Vantage API error: {error_msg}")
                raise ValueError(f"Alpha Vantage API error: {error_msg}")
            
            if "Note" in data:
                # Rate limit exceeded
                note = data["Note"]
                print(f"Alpha Vantage rate limit: {note}")
                raise ValueError(f"Alpha Vantage rate limit: {note}")
            
            # Check for daily time series
            if "Time Series (Daily)" in data:
                time_series = data["Time Series (Daily)"]
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
                    print(f"Successfully got {len(df)} daily data points from Alpha Vantage")
                    return df
                else:
                    raise ValueError("No data found in specified date range")
            else:
                # Try alternative data structure
                if "Time Series (1min)" in data:
                    print("Found intraday data, but daily data preferred")
                    raise ValueError("Intraday data not suitable for daily backtesting")
                else:
                    available_keys = list(data.keys())
                    print(f"Unexpected Alpha Vantage response structure. Available keys: {available_keys}")
                    raise ValueError(f"Unexpected Alpha Vantage response structure: {available_keys}")
                
        except Exception as e:
            print(f"Alpha Vantage failed: {e}")
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
                
                # Use standardized column names
                current_price = current_data.iloc[-1]['close']
                current_date = current_data.iloc[-1]['date']
                
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
                
            except KeyError as e:
                print(f"Column name error in strategy execution: {e}")
                print(f"Available columns: {list(current_data.columns)}")
                print(f"Data shape: {current_data.shape}")
                continue
            except Exception as e:
                print(f"Error in strategy execution: {e}")
                print(f"Available columns: {list(current_data.columns)}")
                continue
        
        # Close any remaining position
        if position > 0:
            final_price = data.iloc[-1]['close']
            final_revenue = position * final_price
            capital += final_revenue
            
            trades.append({
                'date': data.iloc[-1]['date'],
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