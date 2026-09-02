import requests
import sqlite3
import time
from datetime import datetime

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

def get_price(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        result = data['chart']['result'][0]
        meta = result['meta']
        return {
            'price': round(meta.get('regularMarketPrice', 0), 2),
            'change': round(meta.get('regularMarketChangePercent', 0), 2),
            'volume': meta.get('regularMarketVolume', 0),
        }
    except Exception as e:
        print(f"  ❌ Error getting {ticker}: {e}")
        return None

def update_prices():
    # Use a timeout and retry for database lock
    retry_count = 5
    for attempt in range(retry_count):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30)
            c = conn.cursor()
            c.execute("SELECT ticker, price, name FROM stocks")
            tickers = c.fetchall()
            
            print(f"🔄 Updating {len(tickers)} stocks...")
            print("-" * 40)
            
            updated = 0
            for (ticker, old_price, name) in tickers:
                print(f"  📊 {ticker} ({name})...", end=" ")
                data = get_price(ticker)
                if data and data['price'] > 0:
                    now = datetime.now().isoformat()
                    c.execute('''
                        UPDATE stocks 
                        SET price = ?, change = ?, volume = ?, updated_at = ?
                        WHERE ticker = ?
                    ''', (
                        data['price'],
                        data['change'],
                        data['volume'],
                        now,
                        ticker
                    ))
                    updated += 1
                    print(f"✅ ${data['price']}")
                else:
                    print(f"❌ Failed")
                time.sleep(0.3)
            
            conn.commit()
            conn.close()
            
            print("-" * 40)
            print(f"✅ Updated {updated} stocks!")
            
            # Verify the update
            conn2 = sqlite3.connect(DB_PATH)
            c2 = conn2.cursor()
            c2.execute("SELECT ticker, price, updated_at FROM stocks ORDER BY updated_at DESC LIMIT 3")
            print("\n📊 Latest updates:")
            for row in c2.fetchall():
                print(f"  {row[0]}: ${row[1]} (Updated: {row[2]})")
            conn2.close()
            
            return  # Success, exit function
            
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print(f"⚠️ Database locked, attempt {attempt + 1}/{retry_count}. Waiting...")
                time.sleep(5)
            else:
                print(f"❌ Error: {e}")
                break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            break
    
    print("❌ Failed to update after retries.")

if __name__ == '__main__':
    print("🚀 Stock Price Updater Started")
    print("=" * 40)
    update_prices()
    print("=" * 40)
    print("✅ Done!")