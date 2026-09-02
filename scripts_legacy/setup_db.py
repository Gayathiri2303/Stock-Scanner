import sqlite3
import json
import random
from datetime import datetime

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Drop existing table if it exists
    c.execute("DROP TABLE IF EXISTS stocks")
    
    # Create the stocks table with all columns
    c.execute('''
        CREATE TABLE stocks (
            ticker TEXT PRIMARY KEY,
            name TEXT,
            price REAL,
            change REAL,
            volume INTEGER,
            market_cap REAL,
            pe_ratio REAL,
            high_52w REAL,
            low_52w REAL,
            dividend_yield REAL,
            sector TEXT,
            analyst_rating TEXT,
            avg_target REAL,
            revenue_10yr TEXT,
            profit_margin REAL,
            debt_equity REAL,
            earnings_date TEXT,
            news TEXT,
            prediction_score INTEGER,
            updated_at DATETIME,
            usd_inr REAL,
            best_month TEXT,
            best_return REAL,
            worst_month TEXT,
            worst_return REAL,
            seasonal_strength INTEGER,
            volatility REAL
        )
    ''')
    
    print("✅ Table 'stocks' created successfully!")
    
    # Insert some sample stocks
    sample_stocks = [
        {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "price": 316.85, "change": -0.89, "analyst_rating": "Buy", "avg_target": 340, "prediction_score": 40},
        {"ticker": "MSFT", "name": "Microsoft Corp.", "sector": "Technology", "price": 507.29, "change": -1.22, "analyst_rating": "Buy", "avg_target": 550, "prediction_score": 40},
        {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "price": 339.35, "change": -2.09, "analyst_rating": "Buy", "avg_target": 380, "prediction_score": 50},
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer", "price": 259.77, "change": -2.50, "analyst_rating": "Buy", "avg_target": 280, "prediction_score": 40},
        {"ticker": "NVDA", "name": "NVIDIA Corp.", "sector": "Technology", "price": 220.78, "change": 1.49, "analyst_rating": "Hold", "avg_target": 230, "prediction_score": 35},
        {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Consumer", "price": 367.95, "change": 5.51, "analyst_rating": "Overweight", "avg_target": 380, "prediction_score": 55},
        {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "Financial", "price": 356.02, "change": -0.45, "analyst_rating": "Buy", "avg_target": 380, "prediction_score": 40},
        {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer", "price": 103.09, "change": 0.45, "analyst_rating": "Buy", "avg_target": 110, "prediction_score": 50},
        {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "price": 265.85, "change": -0.82, "analyst_rating": "Buy", "avg_target": 285, "prediction_score": 40},
        {"ticker": "CRWD", "name": "CrowdStrike Holdings", "sector": "Technology", "price": 231.00, "change": 5.77, "analyst_rating": "Buy", "avg_target": 250, "prediction_score": 70},
    ]
    
    for stock in sample_stocks:
        c.execute('''
            INSERT OR REPLACE INTO stocks (
                ticker, name, sector, price, change, analyst_rating, avg_target, prediction_score, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stock['ticker'],
            stock['name'],
            stock['sector'],
            stock['price'],
            stock['change'],
            stock['analyst_rating'],
            stock['avg_target'],
            stock['prediction_score'],
            datetime.now().isoformat()
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Inserted {len(sample_stocks)} sample stocks!")
    print("✅ Database setup complete!")

if __name__ == '__main__':
    setup_database()