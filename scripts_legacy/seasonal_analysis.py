import sqlite3
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

def init_seasonal_columns():
    """Add seasonal columns to database if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    columns = ['best_month', 'best_return', 'worst_month', 'worst_return', 'seasonal_strength']
    for col in columns:
        try:
            c.execute(f"ALTER TABLE stocks ADD COLUMN {col} TEXT")
        except:
            pass
    
    conn.commit()
    conn.close()
    print("✅ Seasonal columns ready")

def get_seasonal_data(ticker):
    """Get monthly performance for a stock over past 10 years"""
    try:
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*5)  # 5 years of data
        data = stock.history(start=start_date, end=end_date)
        
        if len(data) < 50:
            return None
        
        # Calculate monthly returns
        monthly = data['Close'].resample('M').last().pct_change()
        monthly_returns = monthly.groupby(monthly.index.month).mean()
        
        # Find best and worst months
        month_names = {
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        }
        
        best_month = monthly_returns.idxmax()
        worst_month = monthly_returns.idxmin()
        
        # Calculate seasonal strength (1-100)
        avg_return = monthly_returns.mean()
        seasonal_strength = 50 + (avg_return * 400)
        
        return {
            'ticker': ticker,
            'best_month': f"{month_names.get(best_month, '')} ({best_month})",
            'best_return': round(monthly_returns[best_month] * 100, 2),
            'worst_month': f"{month_names.get(worst_month, '')} ({worst_month})",
            'worst_return': round(monthly_returns[worst_month] * 100, 2),
            'seasonal_strength': min(100, max(0, round(seasonal_strength))),
            'data_points': len(data)
        }
    except Exception as e:
        return None

def analyze_all_stocks():
    """Analyze all stocks in database"""
    print("📊 Starting Seasonal Stock Analysis...")
    print("⏳ This will take 2-3 minutes...")
    print("-" * 60)
    
    init_seasonal_columns()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ticker FROM stocks")
    tickers = c.fetchall()
    conn.close()
    
    print(f"📊 Found {len(tickers)} stocks to analyze\n")
    
    updated = 0
    for i, (ticker,) in enumerate(tickers, 1):
        if i % 20 == 0:
            print(f"  Progress: {i}/{len(tickers)}")
        
        data = get_seasonal_data(ticker)
        
        if data and data['data_points'] > 50:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''
                UPDATE stocks 
                SET best_month = ?, best_return = ?, 
                    worst_month = ?, worst_return = ?, 
                    seasonal_strength = ?
                WHERE ticker = ?
            ''', (
                data['best_month'],
                data['best_return'],
                data['worst_month'],
                data['worst_return'],
                data['seasonal_strength'],
                ticker
            ))
            conn.commit()
            conn.close()
            updated += 1
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"\n✅ Updated {updated} stocks with seasonal data!")
    
    # Show top seasonal stocks
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT ticker, best_month, best_return, seasonal_strength 
        FROM stocks 
        WHERE seasonal_strength IS NOT NULL 
        ORDER BY seasonal_strength DESC 
        LIMIT 10
    ''')
    results = c.fetchall()
    conn.close()
    
    print("\n📈 TOP SEASONAL STOCKS:")
    print("-" * 40)
    for ticker, month, return_pct, strength in results:
        print(f"  {ticker}: Best in {month} (+{return_pct}%) | Strength: {strength}/100")

if __name__ == '__main__':
    analyze_all_stocks()
