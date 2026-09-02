import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def get_technical_data(ticker):
    """Get technical indicators for a stock"""
    try:
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=100)
        data = stock.history(start=start_date, end=end_date)
        
        if len(data) < 30:
            return None
        
        close = data['Close']
        
        # 1. Simple Moving Averages
        sma_20 = close.rolling(20).mean().iloc[-1]
        sma_50 = close.rolling(50).mean().iloc[-1]
        sma_200 = close.rolling(200).mean().iloc[-1] if len(close) > 200 else close.mean()
        
        # 2. RSI (Relative Strength Index)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1] if not rsi.empty else 50
        
        # 3. MACD
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        current_macd = macd.iloc[-1] if not macd.empty else 0
        current_signal = signal.iloc[-1] if not signal.empty else 0
        
        # 4. Bollinger Bands
        sma = close.rolling(20).mean()
        std = close.rolling(20).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        
        # 5. Volume Trend
        avg_volume = data['Volume'].mean()
        current_volume = data['Volume'].iloc[-1]
        
        # 6. Support & Resistance
        recent_lows = close.tail(20).min()
        recent_highs = close.tail(20).max()
        
        return {
            'ticker': ticker,
            'current_price': close.iloc[-1],
            'sma_20': round(sma_20, 2),
            'sma_50': round(sma_50, 2),
            'sma_200': round(sma_200, 2),
            'rsi': round(current_rsi, 2),
            'macd': round(current_macd, 3),
            'signal': round(current_signal, 3),
            'upper_band': round(upper_band.iloc[-1], 2) if not upper_band.empty else 0,
            'lower_band': round(lower_band.iloc[-1], 2) if not lower_band.empty else 0,
            'avg_volume': int(avg_volume) if not pd.isna(avg_volume) else 0,
            'current_volume': int(current_volume) if not pd.isna(current_volume) else 0,
            'support': round(recent_lows, 2),
            'resistance': round(recent_highs, 2),
            'data_points': len(data)
        }
    except Exception as e:
        return None

def get_technical_signal(data):
    """Generate buy/sell signal based on technicals"""
    signals = []
    score = 0
    
    # RSI
    if data['rsi'] < 30:
        signals.append("RSI: Oversold (Buy Signal)")
        score += 20
    elif data['rsi'] > 70:
        signals.append("RSI: Overbought (Sell Signal)")
        score -= 20
    else:
        signals.append("RSI: Neutral")
    
    # MACD
    if data['macd'] > data['signal']:
        signals.append("MACD: Bullish Crossover")
        score += 15
    else:
        signals.append("MACD: Bearish Crossover")
        score -= 10
    
    # Price vs SMA
    if data['current_price'] > data['sma_50']:
        signals.append("Price above 50-day SMA (Bullish)")
        score += 10
    else:
        signals.append("Price below 50-day SMA (Bearish)")
        score -= 10
    
    # Volume
    if data['current_volume'] > data['avg_volume'] * 1.5:
        signals.append("High Volume: Strong Interest")
        score += 10
    
    # Overall
    if score >= 30:
        signal = "STRONG BUY"
    elif score >= 15:
        signal = "BUY"
    elif score >= -15:
        signal = "HOLD"
    elif score >= -30:
        signal = "SELL"
    else:
        signal = "STRONG SELL"
    
    return {
        'signal': signal,
        'score': score,
        'details': signals
    }
