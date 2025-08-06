import os
import asyncio
from typing import List, Dict, Any

# Try to import OpenAI, but don't fail if not available
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class StrategyGeneratorAgent:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Only initialize OpenAI client if API key is available
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.client = AsyncOpenAI(api_key=self.openai_api_key)
                self.use_openai = True
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                self.use_openai = False
        else:
            self.use_openai = False
            print("Warning: OpenAI API key not found. Using fallback strategy generation.")
        
    async def generate_strategy(
        self,
        symbol: str,
        indicators: List[str],
        timeframe: str = "1d",
        risk_level: str = "medium",
        capital: float = 100000
    ) -> str:
        """
        Generate a trading strategy using AI or fallback
        """
        
        if self.use_openai:
            return await self._generate_ai_strategy(symbol, indicators, timeframe, risk_level, capital)
        else:
            print('GENERATING FALLBACK ALGOOOOOO')
            return self._generate_fallback_strategy(symbol, indicators, risk_level, capital)
    
    async def _generate_ai_strategy(
        self,
        symbol: str,
        indicators: List[str],
        timeframe: str = "1d",
        risk_level: str = "medium",
        capital: float = 100000
    ) -> str:
        """
        Generate a trading strategy using OpenAI
        """
        
        # Create system prompt
        system_prompt = f"""
        You are an expert algorithmic trading strategist. Generate a Python trading strategy for {symbol} using the following indicators: {', '.join(indicators)}.
        
        Requirements:
        - Timeframe: {timeframe}
        - Risk Level: {risk_level}
        - Capital: ${capital:,.2f}
        - Use technical analysis indicators: {', '.join(indicators)}
        
        The strategy should:
        1. Calculate technical indicators
        2. Generate buy/sell signals
        3. Include position sizing based on risk level
        4. Include stop-loss and take-profit logic
        5. Return a dictionary with 'signal' (BUY/SELL/HOLD) and 'confidence' (0-1)
        
        Return ONLY the Python function code, no explanations.
        """
        
        # Create user prompt
        user_prompt = f"""
        Generate a trading strategy for {symbol} with these specifications:
        - Indicators: {indicators}
        - Timeframe: {timeframe}
        - Risk Level: {risk_level}
        - Capital: ${capital:,.2f}
        
        The function should be named 'trading_strategy' and take parameters: (data, capital, risk_level)
        """
        
        try:
            # Generate strategy using OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            strategy_code = response.choices[0].message.content
            print('strategy_code',strategy_code)
            # Clean up the response to extract only the Python code
            if "```python" in strategy_code:
                strategy_code = strategy_code.split("```python")[1].split("```")[0]
            elif "```" in strategy_code:
                strategy_code = strategy_code.split("```")[1]
            
            return strategy_code.strip()
            
        except Exception as e:
            print(f"Error generating AI strategy: {e}")
            # Fallback to template strategy
            print('GENERATING FALLBACK ALGOOOO')
            return self._generate_fallback_strategy(symbol, indicators, risk_level, capital)
    
    def _generate_fallback_strategy(
        self,
        symbol: str,
        indicators: List[str],
        risk_level: str,
        capital: float
    ) -> str:
        """
        Generate a fallback strategy if AI generation fails
        """
        
        risk_multipliers = {
            "low": 0.5,
            "medium": 1.0,
            "high": 2.0
        }
        
        risk_mult = risk_multipliers.get(risk_level, 1.0)
        
        strategy_template = f"""
import pandas as pd
import numpy as np
import ta

def trading_strategy(data, capital, risk_level):
    \"\"\"
    Trading strategy for {symbol} using {', '.join(indicators)}
    \"\"\"
    
    # Use standardized lowercase column names
    close_col = 'close'
    open_col = 'open'
    high_col = 'high'
    low_col = 'low'
    volume_col = 'volume'
    
    # Ensure required columns exist
    required_columns = [close_col, open_col, high_col, low_col, volume_col]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        print(f"Missing columns: {{missing_columns}}")
        print(f"Available columns: {{list(data.columns)}}")
        return {{'signal': 'HOLD', 'confidence': 0.0, 'position_size': 0}}
    
    # Calculate technical indicators
    if 'RSI' in {indicators}:
        data['rsi'] = ta.momentum.RSIIndicator(data[close_col]).rsi()
    
    if 'MACD' in {indicators}:
        macd = ta.trend.MACD(data[close_col])
        data['macd'] = macd.macd()
        data['macd_signal'] = macd.macd_signal()
    
    if 'SMA' in {indicators}:
        data['sma_20'] = ta.trend.SMAIndicator(data[close_col], window=20).sma_indicator()
        data['sma_50'] = ta.trend.SMAIndicator(data[close_col], window=50).sma_indicator()
    
    if 'BB' in {indicators}:
        bb = ta.volatility.BollingerBands(data[close_col])
        data['bb_upper'] = bb.bollinger_hband()
        data['bb_lower'] = bb.bollinger_lband()
    
    # Generate signals
    signal = 'HOLD'
    confidence = 0.5
    
    # RSI strategy
    if 'RSI' in {indicators} and 'rsi' in data.columns:
        if data['rsi'].iloc[-1] < 30:
            signal = 'BUY'
            confidence = 0.8
        elif data['rsi'].iloc[-1] > 70:
            signal = 'SELL'
            confidence = 0.8
    
    # MACD strategy
    if 'MACD' in {indicators} and 'macd' in data.columns and 'macd_signal' in data.columns:
        if data['macd'].iloc[-1] > data['macd_signal'].iloc[-1]:
            if signal == 'HOLD':
                signal = 'BUY'
                confidence = 0.7
        elif data['macd'].iloc[-1] < data['macd_signal'].iloc[-1]:
            if signal == 'HOLD':
                signal = 'SELL'
                confidence = 0.7
    
    # SMA strategy
    if 'SMA' in {indicators} and 'sma_20' in data.columns and 'sma_50' in data.columns:
        if data['sma_20'].iloc[-1] > data['sma_50'].iloc[-1]:
            if signal == 'HOLD':
                signal = 'BUY'
                confidence = 0.6
        elif data['sma_20'].iloc[-1] < data['sma_50'].iloc[-1]:
            if signal == 'HOLD':
                signal = 'SELL'
                confidence = 0.6
    
    # Bollinger Bands strategy
    if 'BB' in {indicators} and 'bb_upper' in data.columns and 'bb_lower' in data.columns:
        current_price = data[close_col].iloc[-1]
        bb_upper = data['bb_upper'].iloc[-1]
        bb_lower = data['bb_lower'].iloc[-1]
        
        if current_price <= bb_lower:
            if signal == 'HOLD':
                signal = 'BUY'
                confidence = 0.7
        elif current_price >= bb_upper:
            if signal == 'HOLD':
                signal = 'SELL'
                confidence = 0.7
    
    # Position sizing based on risk level
    position_size = capital * 0.1 * {risk_mult}  # 10% of capital * risk multiplier
    
    return {{
        'signal': signal,
        'confidence': confidence,
        'position_size': position_size,
        'stop_loss': 0.02,  # 2% stop loss
        'take_profit': 0.06  # 6% take profit
    }}
"""
        
        return strategy_template 