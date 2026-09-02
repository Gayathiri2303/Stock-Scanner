import sqlite3
from datetime import datetime
from sp500_complete import SP500_STOCKS

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

# Connect to database
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Get existing tickers
existing = set()
c.execute("SELECT ticker FROM stocks")
for row in c.fetchall():
    existing.add(row[0])

print(f"📊 Existing stocks: {len(existing)}")
print(f"📊 New stocks to add: {len(SP500_STOCKS)}")

# Add new stocks
added = 0
skipped = 0
for stock in SP500_STOCKS:
    ticker = stock['ticker']
    if ticker not in existing:
        try:
            c.execute('''
                INSERT INTO stocks (ticker, name, sector, price, change, analyst_rating, avg_target, prediction_score, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticker,
                stock['name'],
                stock['sector'],
                0,  # price placeholder
                0,  # change placeholder
                'Hold',  # default rating
                0,  # target
                50,  # prediction score
                datetime.now().isoformat()
            ))
            added += 1
        except:
            skipped += 1

conn.commit()
conn.close()

print(f"✅ Added {added} new stocks!")
print(f"⚠️ Skipped {skipped} stocks (duplicates or errors)")

# Verify total
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM stocks")
total = c.fetchone()[0]
conn.close()
print(f"📊 Total stocks now: {total}")
