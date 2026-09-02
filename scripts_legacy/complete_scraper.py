import requests
from bs4 import BeautifulSoup
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

# ============================================================
# 1. YAHOO FINANCE - Prices, Changes, Volume, Market Cap
# ============================================================
def scrape_yahoo_finance(ticker):
    """Get real-time data from Yahoo Finance"""
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
            'market_cap': meta.get('marketCap', 0),
            'high_52w': meta.get('fiftyTwoWeekHigh', 0),
            'low_52w': meta.get('fiftyTwoWeekLow', 0),
        }
    except:
        return {}

# ============================================================
# 2. FINVIZ - Screener, Fundamentals, Analyst Ratings
# ============================================================
def scrape_finviz(ticker):
    """Get fundamentals and analyst ratings from Finviz"""
    try:
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {}
        tables = soup.find_all('table', class_='snapshot-table2')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].text.strip()
                    value = cells[1].text.strip()
                    if 'P/E' in label:
                        try:
                            data['pe_ratio'] = float(value.replace('x', '').replace(',', '')) if value != '-' else 0
                        except:
                            data['pe_ratio'] = 0
                    elif 'Dividend' in label and 'Yield' in label:
                        try:
                            data['dividend_yield'] = float(value.replace('%', '')) if value != '-' else 0
                        except:
                            data['dividend_yield'] = 0
                    elif 'Analyst' in label and 'Recom' in label:
                        rating_map = {'1.0': 'Buy', '1.5': 'Buy', '2.0': 'Overweight', '2.5': 'Hold', '3.0': 'Hold', '3.5': 'Underweight', '4.0': 'Sell', '4.5': 'Sell', '5.0': 'Sell'}
                        rating_match = re.search(r'(\d+\.\d+)', value)
                        if rating_match:
                            data['analyst_rating'] = rating_map.get(rating_match.group(1), 'Hold')
                        else:
                            data['analyst_rating'] = 'Hold'
                    elif 'Profit Margin' in label:
                        try:
                            data['profit_margin'] = float(value.replace('%', '')) if value != '-' else 0
                        except:
                            data['profit_margin'] = 0
        return data
    except:
        return {}

# ============================================================
# 3. TIPRANKS - Analyst Forecasts & Price Targets
# ============================================================
def scrape_tipranks(ticker):
    """Get analyst forecasts from TipRanks"""
    try:
        url = f"https://www.tipranks.com/stocks/{ticker}/forecast"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        avg_target = 0
        target_texts = soup.find_all(string=re.compile(r'Average.*Target|Target.*Price'))
        for text in target_texts:
            numbers = re.findall(r'\$?(\d+\.?\d*)', text)
            if numbers and float(numbers[0]) > 10:
                avg_target = float(numbers[0])
                break
        return {'avg_target': avg_target}
    except:
        return {'avg_target': 0}

# ============================================================
# 4. INVESTING.COM - Earnings Dates
# ============================================================
def scrape_investing(ticker):
    """Get earnings date from Investing.com"""
    try:
        url = f"https://www.investing.com/equities/{ticker}-earnings"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        earnings_date = "Unknown"
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                if 'Earnings' in cells[0].text:
                    earnings_date = cells[1].text.strip()
                    break
        return {'earnings_date': earnings_date}
    except:
        return {'earnings_date': 'Unknown'}

# ============================================================
# 5. BENZINGA - News Headlines
# ============================================================
def scrape_benzinga(ticker):
    """Get news from Benzinga"""
    try:
        url = f"https://www.benzinga.com/search/?q={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        headlines = []
        for item in soup.find_all(class_='article-title')[:3]:
            text = item.text.strip()
            if text:
                headlines.append(text[:100])
        return ' | '.join(headlines) if headlines else 'No recent news'
    except:
        return 'News unavailable'

# ============================================================
# 6. MACROTRENDS - 10-Year Revenue History
# ============================================================
def scrape_macrotrends(ticker):
    """Get 10-year revenue from Macrotrends"""
    try:
        url = f"https://www.macrotrends.net/stocks/charts/{ticker}/revenue"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = []
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                year = cells[0].text.strip()
                value = cells[1].text.strip()
                if year and value and 'M' in value:
                    data.append(value)
        return {'revenue_10yr': ' | '.join(data[:10]) if data else 'No data'}
    except:
        return {'revenue_10yr': 'No data'}

# ============================================================
# 7. STOCKANALYSIS - Company Fundamentals
# ============================================================
def scrape_stockanalysis(ticker):
    """Get fundamentals from StockAnalysis"""
    try:
        url = f"https://stockanalysis.com/stocks/{ticker}/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {}
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                label = cells[0].text.strip()
                value = cells[1].text.strip()
                if 'Debt' in label and 'Equity' in label:
                    try:
                        data['debt_equity'] = float(value) if value != '-' else 0
                    except:
                        data['debt_equity'] = 0
        return data
    except:
        return {}

# ============================================================
# 8. SIMPLYWALL.ST - Company Health Snapshot
# ============================================================
def scrape_simplywallst(ticker):
    """Get company health from SimplyWall.St"""
    try:
        url = f"https://simplywall.st/stocks/us/technology/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        health = "Unknown"
        health_elements = soup.find_all(string=re.compile(r'Health|Rating'))
        for elem in health_elements:
            if 'Health' in elem:
                health = elem.strip()
                break
        return {'company_health': health}
    except:
        return {'company_health': 'Unknown'}

# ============================================================
# 9. EARNINGSWHISPERS - Earnings Surprises
# ============================================================
def scrape_earningswhispers(ticker):
    """Get earnings surprise from EarningsWhispers"""
    try:
        url = f"https://www.earningswhispers.com/stocks/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        surprise = "Unknown"
        for text in soup.find_all('div'):
            if 'Surprise' in text.text:
                surprise = text.text.replace('Surprise', '').strip()
                break
        return {'earnings_surprise': surprise}
    except:
        return {'earnings_surprise': 'Unknown'}

# ============================================================
# 10. MARKETBEAT - Analyst Forecasts (Backup)
# ============================================================
def scrape_marketbeat(ticker):
    """Get analyst forecasts from MarketBeat"""
    try:
        url = f"https://www.marketbeat.com/stocks/{ticker}/forecast"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rating = "Hold"
        rating_elements = soup.find_all(string=re.compile(r'Buy|Hold|Sell'))
        for elem in rating_elements:
            if 'Buy' in elem and 'Hold' not in elem:
                rating = 'Buy'
                break
            elif 'Sell' in elem:
                rating = 'Sell'
                break
        return {'marketbeat_rating': rating}
    except:
        return {'marketbeat_rating': 'Hold'}

# ============================================================
# MASTER SCRAPER - All Websites
# ============================================================
def scrape_all_sources(ticker):
    """Scrape from ALL 10 websites"""
    print(f"  📊 Scraping {ticker} from all sources...")
    
    data = {}
    
    # 1. Yahoo Finance
    data.update(scrape_yahoo_finance(ticker))
    time.sleep(0.2)
    
    # 2. Finviz
    data.update(scrape_finviz(ticker))
    time.sleep(0.2)
    
    # 3. TipRanks
    data.update(scrape_tipranks(ticker))
    time.sleep(0.2)
    
    # 4. Investing.com
    data.update(scrape_investing(ticker))
    time.sleep(0.2)
    
    # 5. Benzinga
    data['news'] = scrape_benzinga(ticker)
    time.sleep(0.2)
    
    # 6. Macrotrends
    data.update(scrape_macrotrends(ticker))
    time.sleep(0.2)
    
    # 7. StockAnalysis
    data.update(scrape_stockanalysis(ticker))
    time.sleep(0.2)
    
    # 8. SimplyWall.St
    data.update(scrape_simplywallst(ticker))
    time.sleep(0.2)
    
    # 9. EarningsWhispers
    data.update(scrape_earningswhispers(ticker))
    time.sleep(0.2)
    
    # 10. MarketBeat
    data.update(scrape_marketbeat(ticker))
    time.sleep(0.2)
    
    return data

def calculate_prediction_score(data):
    """Calculate prediction score based on all data"""
    score = 0
    
    # Price momentum (30 points)
    change = data.get('change', 0)
    if change > 3:
        score += 30
    elif change > 1:
        score += 20
    elif change > 0:
        score += 10
    
    # Analyst rating (30 points)
    rating = data.get('analyst_rating', 'Hold')
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
    
    # Price target upside (30 points)
    avg_target = data.get('avg_target', 0)
    price = data.get('price', 1)
    if avg_target and price:
        upside = (avg_target / price - 1) * 100
        if upside > 20:
            score += 30
        elif upside > 10:
            score += 20
        elif upside > 5:
            score += 10
    
    # Volume (10 points)
    volume = data.get('volume', 0)
    if volume > 10000000:
        score += 10
    elif volume > 5000000:
        score += 5
    
    return max(0, min(score, 100))

def get_usd_inr():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data['rates'].get('INR', 83.5)
    except:
        return 83.5

def save_to_db(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE stocks SET
            price = ?, change = ?, volume = ?, market_cap = ?,
            pe_ratio = ?, dividend_yield = ?, analyst_rating = ?,
            avg_target = ?, revenue_10yr = ?, profit_margin = ?,
            debt_equity = ?, earnings_date = ?, news = ?,
            prediction_score = ?, updated_at = ?, usd_inr = ?
        WHERE ticker = ?
    ''', (
        data.get('price', 0),
        data.get('change', 0),
        data.get('volume', 0),
        data.get('market_cap', 0),
        data.get('pe_ratio', 0),
        data.get('dividend_yield', 0),
        data.get('analyst_rating', 'Hold'),
        data.get('avg_target', 0),
        data.get('revenue_10yr', 'No data'),
        data.get('profit_margin', 0),
        data.get('debt_equity', 0),
        data.get('earnings_date', 'Unknown'),
        data.get('news', 'No news'),
        data.get('prediction_score', 50),
        datetime.now().isoformat(),
        data.get('usd_inr', 83.5),
        data.get('ticker', '')
    ))
    conn.commit()
    conn.close()

def main():
    print("=" * 60)
    print("📊 COMPLETE STOCK SCRAPER - ALL 10 WEBSITES")
    print("=" * 60)
    
    init_db()
    usd_inr = get_usd_inr()
    print(f"💵 USD/INR: {usd_inr}\n")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ticker FROM stocks")
    tickers = c.fetchall()
    conn.close()
    
    print(f"📊 Total stocks to update: {len(tickers)}\n")
    
    for i, (ticker,) in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}]", end=" ")
        data = scrape_all_sources(ticker)
        data['ticker'] = ticker
        data['usd_inr'] = usd_inr
        data['prediction_score'] = calculate_prediction_score(data)
        
        save_to_db(data)
        print(f"    ✅ {ticker} - Score: {data['prediction_score']}")
    
    print("\n✅ ALL DONE!")
    print("📊 Data updated from all 10 websites!")

if __name__ == '__main__':
    main()
