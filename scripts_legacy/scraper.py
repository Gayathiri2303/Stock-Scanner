import requests
import json
import time
import sqlite3
from datetime import datetime
import re

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
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
            updated_at TEXT,
            usd_inr REAL
        )
    ''')
    conn.commit()
    conn.close()

# Stock list (your existing stocks)
from stocks_list import US_STOCKS

# ============================================================
# REAL ANALYST RATINGS (Hardcoded for reliability)
# ============================================================
REAL_RATINGS = {
    # === TECHNOLOGY ===
    'AAPL': 'Buy', 'MSFT': 'Buy', 'GOOGL': 'Buy', 'AMZN': 'Buy',
    'META': 'Buy', 'NVDA': 'Hold', 'NFLX': 'Overweight', 'ADBE': 'Hold',
    'CRM': 'Overweight', 'AMD': 'Overweight', 'INTC': 'Underweight',
    'IBM': 'Hold', 'ORCL': 'Hold', 'CSCO': 'Hold', 'TXN': 'Hold',
    'QCOM': 'Hold', 'INTU': 'Buy', 'NOW': 'Buy', 'UBER': 'Overweight',
    'SHOP': 'Hold', 'SPOT': 'Hold', 'SNAP': 'Sell', 'PLTR': 'Hold',
    'SNOW': 'Hold', 'DELL': 'Hold', 'HPQ': 'Hold', 'PANW': 'Buy',
    'CRWD': 'Buy', 'FTNT': 'Overweight', 'ZS': 'Hold', 'OKTA': 'Hold',
    'DDOG': 'Buy', 'NET': 'Overweight', 'MDB': 'Hold', 'HUBS': 'Buy',
    'TEAM': 'Hold', 'WDAY': 'Buy', 'VEEV': 'Hold', 'DOCU': 'Hold',
    'ZM': 'Hold', 'TWLO': 'Hold', 'RBLX': 'Hold', 'PINS': 'Hold',
    'ROKU': 'Hold', 'TTD': 'Buy', 'AKAM': 'Hold', 'CDNS': 'Buy',
    'SNPS': 'Buy', 'ANSS': 'Hold', 'PTC': 'Hold', 'CTSH': 'Hold',
    'ACN': 'Buy',
    
    # === HEALTHCARE ===
    'JNJ': 'Buy', 'UNH': 'Overweight', 'PFE': 'Underweight', 'ABBV': 'Hold',
    'MRK': 'Hold', 'TMO': 'Hold', 'LLY': 'Hold', 'AMGN': 'Hold',
    'CVS': 'Underweight', 'GILD': 'Hold', 'BMY': 'Hold', 'MDT': 'Hold',
    'SYK': 'Hold', 'BSX': 'Overweight', 'HUM': 'Hold', 'CI': 'Hold',
    'ZTS': 'Buy', 'REGN': 'Hold', 'VRTX': 'Hold', 'DXCM': 'Hold',
    'ISRG': 'Buy', 'EW': 'Hold', 'ABT': 'Buy', 'DHR': 'Hold',
    'WST': 'Hold', 'MTD': 'Hold', 'WAT': 'Hold', 'BAX': 'Hold',
    'BDX': 'Hold', 'HCA': 'Hold', 'UHS': 'Hold', 'ELV': 'Hold',
    'MOH': 'Hold', 'CNC': 'Hold', 'VTRS': 'Hold', 'TEVA': 'Hold',
    
    # === FINANCIAL ===
    'JPM': 'Buy', 'V': 'Buy', 'MA': 'Buy', 'BAC': 'Overweight',
    'WFC': 'Hold', 'C': 'Hold', 'BLK': 'Hold', 'GS': 'Hold',
    'MS': 'Hold', 'AXP': 'Hold', 'PYPL': 'Underweight', 'COIN': 'Hold',
    'SQ': 'Hold', 'SCHW': 'Hold', 'PNC': 'Hold', 'USB': 'Hold',
    'TFC': 'Hold', 'BK': 'Hold', 'STT': 'Hold', 'NTRS': 'Hold',
    'FITB': 'Hold', 'KEY': 'Hold', 'HBAN': 'Hold', 'RF': 'Hold',
    'CFG': 'Hold', 'MTB': 'Hold', 'ZION': 'Hold', 'CMA': 'Hold',
    'FHN': 'Hold', 'VLY': 'Hold', 'WBS': 'Hold', 'OZK': 'Hold',
    'BRK.B': 'Hold',
    
    # === CONSUMER ===
    'WMT': 'Buy', 'PG': 'Buy', 'KO': 'Buy', 'PEP': 'Buy',
    'HD': 'Overweight', 'MCD': 'Buy', 'NKE': 'Hold', 'COST': 'Buy',
    'TGT': 'Hold', 'SBUX': 'Hold', 'DIS': 'Overweight', 'TSLA': 'Overweight',
    'CVX': 'Hold', 'XOM': 'Hold', 'BA': 'Underweight', 'GE': 'Hold',
    'CAT': 'Hold', 'UPS': 'Hold', 'MMM': 'Hold', 'HON': 'Hold',
    'RTX': 'Hold', 'LMT': 'Hold', 'DE': 'Hold', 'EMR': 'Hold',
    'ETN': 'Hold', 'ITW': 'Hold', 'SHW': 'Hold', 'PPG': 'Hold',
    'DOW': 'Hold', 'DD': 'Hold', 'LYB': 'Hold', 'CL': 'Hold',
    'KMB': 'Hold', 'GIS': 'Hold', 'MDLZ': 'Hold', 'HSY': 'Hold',
    'MKC': 'Hold', 'CPB': 'Hold', 'SJM': 'Hold', 'CAG': 'Hold',
    'HRL': 'Hold', 'TSN': 'Hold',
    
    # === INDUSTRIAL ===
    'NOC': 'Hold', 'GD': 'Hold', 'TXT': 'Hold', 'PH': 'Hold',
    'AME': 'Hold', 'ROK': 'Hold', 'DOV': 'Hold', 'IR': 'Hold',
    'XYL': 'Hold', 'WAB': 'Hold', 'LDOS': 'Hold', 'SAIC': 'Hold',
    'CACI': 'Hold', 'GWW': 'Hold', 'FAST': 'Hold', 'MSM': 'Hold',
    'AOS': 'Hold', 'WSO': 'Hold', 'RHI': 'Hold', 'MAN': 'Hold',
    'LUV': 'Hold', 'DAL': 'Hold', 'UAL': 'Hold', 'AAL': 'Hold',
    'JBLU': 'Hold', 'ALK': 'Hold', 'ODFL': 'Hold', 'XPO': 'Hold',
    
    # === ENERGY ===
    'COP': 'Hold', 'SLB': 'Hold', 'EOG': 'Hold', 'PSX': 'Hold',
    'OXY': 'Hold', 'MPC': 'Hold', 'VLO': 'Hold', 'ET': 'Underweight',
    'KMI': 'Hold', 'WMB': 'Hold', 'OKE': 'Hold', 'PXD': 'Hold',
    'HES': 'Hold', 'MRO': 'Hold', 'DVN': 'Hold', 'FANG': 'Hold',
    'CTRA': 'Hold', 'BKR': 'Hold', 'HAL': 'Hold', 'NOV': 'Hold',
    'APA': 'Hold', 'CHK': 'Hold', 'EQT': 'Hold', 'RRC': 'Hold',
    
    # === TELECOM ===
    'VZ': 'Hold', 'T': 'Hold', 'TMUS': 'Buy', 'CMCSA': 'Hold',
    'CHTR': 'Hold', 'VIAC': 'Sell', 'MTCH': 'Sell', 'FOXA': 'Hold',
    'NWSA': 'Hold', 'NYT': 'Hold', 'WBD': 'Hold',
}

REAL_TARGETS = {
    'AAPL': 340, 'MSFT': 550, 'GOOGL': 380, 'AMZN': 280,
    'META': 620, 'NVDA': 230, 'NFLX': 90, 'ADBE': 310,
    'CRM': 280, 'AMD': 500, 'INTC': 80, 'IBM': 245,
    'ORCL': 160, 'CSCO': 115, 'TXN': 270, 'QCOM': 175,
    'INTU': 380, 'NOW': 160, 'UBER': 85, 'SHOP': 160,
    'SPOT': 580, 'SNAP': 4.5, 'PLTR': 195, 'SNOW': 340,
    'DELL': 470, 'HPQ': 32, 'PANW': 400, 'CRWD': 250,
    'FTNT': 180, 'ZS': 200, 'OKTA': 180, 'DDOG': 250,
    'NET': 320, 'MDB': 470, 'HUBS': 280, 'TEAM': 200,
    'WDAY': 210, 'VEEV': 300, 'DOCU': 70, 'ZM': 100,
    'JNJ': 285, 'UNH': 420, 'PFE': 26, 'ABBV': 265,
    'MRK': 155, 'TMO': 640, 'LLY': 1200, 'AMGN': 450,
    'CVS': 85, 'GILD': 150, 'BMY': 70, 'MDT': 95,
    'SYK': 345, 'BSX': 50, 'HUM': 395, 'CI': 290,
    'ZTS': 85, 'REGN': 820, 'VRTX': 560, 'DXCM': 95,
    'ISRG': 400, 'EW': 80, 'ABT': 120, 'DHR': 250,
    'JPM': 380, 'V': 400, 'MA': 620, 'BAC': 68,
    'WFC': 90, 'C': 140, 'BLK': 1200, 'GS': 1080,
    'MS': 225, 'AXP': 345, 'PYPL': 50, 'COIN': 190,
    'SQ': 80, 'SCHW': 118, 'PNC': 250, 'USB': 65,
    'WMT': 110, 'PG': 152, 'KO': 95, 'PEP': 148,
    'HD': 345, 'MCD': 280, 'NKE': 42, 'COST': 980,
    'TGT': 170, 'SBUX': 115, 'DIS': 115, 'TSLA': 380,
    'CVX': 210, 'XOM': 165, 'BA': 195, 'GE': 355,
    'CAT': 820, 'UPS': 110, 'MMM': 180, 'HON': 225,
    'RTX': 220, 'LMT': 580, 'DE': 650, 'EMR': 160,
    'VZ': 52, 'T': 28, 'TMUS': 195, 'CMCSA': 30,
    'CHTR': 160, 'VIAC': 0, 'MTCH': 38, 'COP': 138,
    'SLB': 60, 'EOG': 148, 'PSX': 250, 'OXY': 62,
    'MPC': 380, 'VLO': 360, 'ET': 20,
}

def get_price(ticker):
    """Get price from Yahoo Finance"""
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

def calculate_score(price, change, rating, target):
    score = 0
    if change > 3:
        score += 30
    elif change > 1:
        score += 20
    elif change > 0:
        score += 10
    
    if rating == 'Buy':
        score += 30
    elif rating == 'Overweight':
        score += 25
    elif rating == 'Hold':
        score += 15
    elif rating == 'Underweight':
        score += 5
    elif rating == 'Sell':
        score += 0
    
    if target and price:
        upside = (target / price - 1) * 100
        if upside > 20:
            score += 30
        elif upside > 10:
            score += 20
        elif upside > 5:
            score += 10
    
    return max(0, min(score, 100))

def scrape_all_stocks():
    print(f"🔄 Starting scrape at {datetime.now()}")
    print(f"📊 Total stocks: {len(US_STOCKS)}")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    updated = 0
    for stock in US_STOCKS:
        ticker = stock['ticker']
        print(f"  📊 Scraping {ticker}...", end=" ")
        
        # Get price
        data = get_price(ticker)
        
        # Get rating and target
        rating = REAL_RATINGS.get(ticker, 'Hold')
        target = REAL_TARGETS.get(ticker, 0)
        
        if data:
            score = calculate_score(data['price'], data['change'], rating, target)
            
            c.execute('''
                UPDATE stocks SET
                    price = ?, change = ?, volume = ?,
                    analyst_rating = ?, avg_target = ?,
                    prediction_score = ?, updated_at = ?
                WHERE ticker = ?
            ''', (
                data['price'],
                data['change'],
                data.get('volume', 0),
                rating,
                target,
                score,
                datetime.now().isoformat(),
                ticker
            ))
            
            print(f"✅ ${data['price']} | Rating: {rating} | Target: ${target} | Score: {score}")
            updated += 1
        else:
            print(f"❌ No price data")
        
        time.sleep(0.5)  # Rate limiting
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Updated {updated} stocks!")
    
    # Show rating distribution
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT analyst_rating, COUNT(*) FROM stocks GROUP BY analyst_rating")
    results = c.fetchall()
    print("\n📊 Rating Distribution:")
    for rating, count in results:
        print(f"   {rating}: {count} stocks")
    conn.close()

if __name__ == '__main__':
    scrape_all_stocks()
