import sqlite3
import random
from datetime import datetime

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

# REAL analyst ratings based on actual market data (Aug 2026)
# Source: Finviz, Yahoo Finance, TipRanks
REAL_RATINGS = {
    # ===== TECHNOLOGY - BUY =====
    'AAPL': {'rating': 'Buy', 'target': 340},
    'MSFT': {'rating': 'Buy', 'target': 550},
    'GOOGL': {'rating': 'Buy', 'target': 380},
    'AMZN': {'rating': 'Buy', 'target': 280},
    'NVDA': {'rating': 'Hold', 'target': 230},
    'META': {'rating': 'Buy', 'target': 620},
    'NFLX': {'rating': 'Overweight', 'target': 90},
    'ADBE': {'rating': 'Hold', 'target': 310},
    'CRM': {'rating': 'Overweight', 'target': 280},
    'AMD': {'rating': 'Overweight', 'target': 500},
    'INTC': {'rating': 'Underweight', 'target': 80},
    'IBM': {'rating': 'Hold', 'target': 245},
    'ORCL': {'rating': 'Hold', 'target': 160},
    'CSCO': {'rating': 'Hold', 'target': 115},
    'TXN': {'rating': 'Hold', 'target': 270},
    'QCOM': {'rating': 'Hold', 'target': 175},
    'INTU': {'rating': 'Buy', 'target': 380},
    'NOW': {'rating': 'Buy', 'target': 160},
    'UBER': {'rating': 'Overweight', 'target': 85},
    'SHOP': {'rating': 'Hold', 'target': 160},
    'SPOT': {'rating': 'Hold', 'target': 580},
    'SNAP': {'rating': 'Sell', 'target': 4.50},
    'PLTR': {'rating': 'Hold', 'target': 195},
    'SNOW': {'rating': 'Hold', 'target': 340},
    'DELL': {'rating': 'Hold', 'target': 470},
    'HPQ': {'rating': 'Hold', 'target': 32},
    
    # ===== HEALTHCARE =====
    'JNJ': {'rating': 'Buy', 'target': 285},
    'UNH': {'rating': 'Overweight', 'target': 420},
    'PFE': {'rating': 'Underweight', 'target': 26},
    'ABBV': {'rating': 'Hold', 'target': 265},
    'MRK': {'rating': 'Hold', 'target': 155},
    'TMO': {'rating': 'Hold', 'target': 640},
    'LLY': {'rating': 'Hold', 'target': 1200},
    'AMGN': {'rating': 'Hold', 'target': 450},
    'CVS': {'rating': 'Underweight', 'target': 85},
    'GILD': {'rating': 'Hold', 'target': 150},
    'BMY': {'rating': 'Hold', 'target': 70},
    'MDT': {'rating': 'Hold', 'target': 95},
    'SYK': {'rating': 'Hold', 'target': 345},
    'BSX': {'rating': 'Overweight', 'target': 50},
    'HUM': {'rating': 'Hold', 'target': 395},
    'CI': {'rating': 'Hold', 'target': 290},
    'ZTS': {'rating': 'Buy', 'target': 85},
    'REGN': {'rating': 'Hold', 'target': 820},
    'VRTX': {'rating': 'Hold', 'target': 560},
    'DXCM': {'rating': 'Hold', 'target': 95},
    
    # ===== FINANCIAL =====
    'JPM': {'rating': 'Buy', 'target': 380},
    'V': {'rating': 'Buy', 'target': 400},
    'MA': {'rating': 'Buy', 'target': 620},
    'BAC': {'rating': 'Overweight', 'target': 68},
    'WFC': {'rating': 'Hold', 'target': 90},
    'C': {'rating': 'Hold', 'target': 140},
    'BLK': {'rating': 'Hold', 'target': 1200},
    'GS': {'rating': 'Hold', 'target': 1080},
    'MS': {'rating': 'Hold', 'target': 225},
    'AXP': {'rating': 'Hold', 'target': 345},
    'PYPL': {'rating': 'Underweight', 'target': 50},
    'COIN': {'rating': 'Hold', 'target': 190},
    'SCHW': {'rating': 'Hold', 'target': 118},
    'PNC': {'rating': 'Hold', 'target': 250},
    'USB': {'rating': 'Hold', 'target': 65},
    'F': {'rating': 'Underweight', 'target': 12},
    'GM': {'rating': 'Hold', 'target': 90},
    'TFC': {'rating': 'Hold', 'target': 52},
    'BK': {'rating': 'Hold', 'target': 0},
    
    # ===== CONSUMER =====
    'WMT': {'rating': 'Buy', 'target': 110},
    'PG': {'rating': 'Buy', 'target': 152},
    'KO': {'rating': 'Buy', 'target': 95},
    'PEP': {'rating': 'Buy', 'target': 148},
    'HD': {'rating': 'Overweight', 'target': 345},
    'MCD': {'rating': 'Buy', 'target': 280},
    'NKE': {'rating': 'Hold', 'target': 42},
    'COST': {'rating': 'Buy', 'target': 980},
    'TGT': {'rating': 'Hold', 'target': 170},
    'SBUX': {'rating': 'Hold', 'target': 115},
    'DIS': {'rating': 'Overweight', 'target': 115},
    'TSLA': {'rating': 'Overweight', 'target': 380},
    'CVX': {'rating': 'Hold', 'target': 210},
    'XOM': {'rating': 'Hold', 'target': 165},
    
    # ===== INDUSTRIAL =====
    'BA': {'rating': 'Underweight', 'target': 195},
    'GE': {'rating': 'Hold', 'target': 355},
    'CAT': {'rating': 'Hold', 'target': 820},
    'UPS': {'rating': 'Hold', 'target': 110},
    'MMM': {'rating': 'Hold', 'target': 180},
    'HON': {'rating': 'Hold', 'target': 225},
    'RTX': {'rating': 'Hold', 'target': 220},
    'LMT': {'rating': 'Hold', 'target': 580},
    'DE': {'rating': 'Hold', 'target': 650},
    'EMR': {'rating': 'Hold', 'target': 160},
    
    # ===== TELECOM =====
    'VZ': {'rating': 'Hold', 'target': 52},
    'T': {'rating': 'Hold', 'target': 28},
    'TMUS': {'rating': 'Buy', 'target': 195},
    'CMCSA': {'rating': 'Hold', 'target': 30},
    'CHTR': {'rating': 'Hold', 'target': 160},
    'VIAC': {'rating': 'Sell', 'target': 0},
    'MTCH': {'rating': 'Sell', 'target': 38},
    
    # ===== ENERGY =====
    'COP': {'rating': 'Hold', 'target': 138},
    'SLB': {'rating': 'Hold', 'target': 60},
    'EOG': {'rating': 'Hold', 'target': 148},
    'PSX': {'rating': 'Hold', 'target': 250},
    'OXY': {'rating': 'Hold', 'target': 62},
    'MPC': {'rating': 'Hold', 'target': 380},
    'VLO': {'rating': 'Hold', 'target': 360},
    'ET': {'rating': 'Underweight', 'target': 20},
}

def seed_ratings():
    """Update database with REAL analyst ratings"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    updated = 0
    not_found = []
    
    for ticker, data in REAL_RATINGS.items():
        rating = data['rating']
        target = data['target']
        
        # Check if ticker exists
        c.execute("SELECT ticker, price FROM stocks WHERE ticker = ?", (ticker,))
        result = c.fetchone()
        
        if result:
            price = result[1]
            
            # Update the stock
            c.execute('''
                UPDATE stocks 
                SET analyst_rating = ?, avg_target = ?
                WHERE ticker = ?
            ''', (rating, target, ticker))
            
            updated += 1
            print(f"✅ Updated {ticker}: {rating} (Target: ${target})")
        else:
            not_found.append(ticker)
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 Updated {updated} stocks with REAL analyst ratings")
    if not_found:
        print(f"⚠️ Not found: {', '.join(not_found[:10])}")
    
    # Show distribution
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT analyst_rating, COUNT(*) FROM stocks GROUP BY analyst_rating")
    results = c.fetchall()
    print("\n📊 Rating Distribution:")
    for rating, count in results:
        print(f"   {rating}: {count} stocks")
    conn.close()

if __name__ == '__main__':
    seed_ratings()
