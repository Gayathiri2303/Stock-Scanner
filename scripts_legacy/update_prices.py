import requests
import sqlite3
import time
from datetime import datetime

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

def get_price_yahoo(ticker):
    """Get stock price from Yahoo Finance"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        result = data['chart']['result'][0]
        meta = result['meta']
        return {
            'price': meta.get('regularMarketPrice', 0),
            'change': meta.get('regularMarketChangePercent', 0),
            'volume': meta.get('regularMarketVolume', 0),
        }
    except:
        return None

def update_missing_prices():
    """Update stocks with 0 price or 0 change"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get stocks with 0 price or 0 change
    c.execute("SELECT ticker FROM stocks WHERE price = 0 OR change = 0")
    stocks = c.fetchall()
    
    print(f"📊 Found {len(stocks)} stocks with missing data")
    
    updated = 0
    for (ticker,) in stocks:
        print(f"  Updating {ticker}...", end=" ")
        data = get_price_yahoo(ticker)
        if data and data['price'] > 0:
            c.execute('''
                UPDATE stocks 
                SET price = ?, change = ?, volume = ?, updated_at = ?
                WHERE ticker = ?
            ''', (data['price'], data['change'], data['volume'], datetime.now().isoformat(), ticker))
            updated += 1
            print(f"✅ ${data['price']} ({data['change']}%)")
        else:
            print("❌ No data")
        time.sleep(0.5)
    
    conn.commit()
    conn.close()
    print(f"\n✅ Updated {updated} stocks")

if __name__ == '__main__':
    update_missing_prices()
