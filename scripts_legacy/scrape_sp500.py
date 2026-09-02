import requests
from bs4 import BeautifulSoup
import json
import time
import re

def scrape_sp500_from_finviz():
    """Scrape S&P 500 stocks directly from Finviz"""
    try:
        print("🔍 Scraping S&P 500 from Finviz...")
        
        # Finviz S&P 500 screener
        url = "https://finviz.com/screener.ashx?v=111&f=idx_sp500"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        stocks = []
        
        # Find the table with stock data
        table = soup.find('table', {'class': 'screener-table'})
        if not table:
            print("❌ Could not find screener table")
            return None
        
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Skip header
            cols = row.find_all('td')
            if len(cols) >= 3:
                ticker = cols[0].text.strip()
                name = cols[1].text.strip()
                sector = cols[2].text.strip()
                
                if ticker and name:
                    stocks.append({
                        'ticker': ticker,
                        'name': name,
                        'sector': sector
                    })
        
        print(f"✅ Scraped {len(stocks)} stocks from Finviz")
        return stocks
    except Exception as e:
        print(f"❌ Finviz error: {e}")
        return None

def scrape_sp500_from_wikipedia():
    """Scrape S&P 500 from Wikipedia"""
    try:
        print("🔍 Scraping S&P 500 from Wikipedia...")
        
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table
        table = soup.find('table', {'id': 'constituents'})
        if not table:
            # Try alternative table class
            table = soup.find('table', {'class': 'wikitable'})
        
        if not table:
            print("❌ Could not find table")
            return None
        
        stocks = []
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Skip header
            cols = row.find_all('td')
            if len(cols) >= 4:
                ticker = cols[0].text.strip()
                name = cols[1].text.strip()
                sector = cols[3].text.strip()
                
                if ticker and name:
                    stocks.append({
                        'ticker': ticker,
                        'name': name,
                        'sector': sector
                    })
        
        print(f"✅ Scraped {len(stocks)} stocks from Wikipedia")
        return stocks
    except Exception as e:
        print(f"❌ Wikipedia error: {e}")
        return None

def scrape_sp500_from_marketwatch():
    """Scrape S&P 500 from MarketWatch"""
    try:
        print("🔍 Scraping S&P 500 from MarketWatch...")
        
        url = "https://www.marketwatch.com/investing/index/spx"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        stocks = []
        # Find components
        components = soup.find_all('div', {'class': 'component'})
        
        for comp in components[:50]:  # Get first 50
            ticker_elem = comp.find('span', {'class': 'symbol'})
            name_elem = comp.find('span', {'class': 'name'})
            
            if ticker_elem and name_elem:
                stocks.append({
                    'ticker': ticker_elem.text.strip(),
                    'name': name_elem.text.strip(),
                    'sector': 'Unknown'
                })
        
        print(f"✅ Scraped {len(stocks)} stocks from MarketWatch")
        return stocks
    except Exception as e:
        print(f"❌ MarketWatch error: {e}")
        return None

def save_stocks_to_file(stocks, filename='sp500_scraped.py'):
    """Save scraped stocks to Python file"""
    with open(filename, 'w') as f:
        f.write(f"# S&P 500 stocks scraped from online sources\n")
        f.write(f"# Total: {len(stocks)} stocks\n\n")
        f.write(f"SP500_STOCKS = {stocks}\n\n")
        f.write(f"print(f'✅ Loaded {{len(SP500_STOCKS)}} S&P 500 stocks from web scraper')\n")
    
    print(f"💾 Saved {len(stocks)} stocks to {filename}")

def main():
    print("=" * 60)
    print("📊 S&P 500 STOCK SCRAPER")
    print("=" * 60)
    
    stocks = None
    
    # Try multiple sources
    sources = [
        scrape_sp500_from_wikipedia,
        scrape_sp500_from_finviz,
        scrape_sp500_from_marketwatch
    ]
    
    for source in sources:
        stocks = source()
        if stocks and len(stocks) > 100:
            break
        time.sleep(1)
    
    if stocks and len(stocks) > 100:
        save_stocks_to_file(stocks)
        
        # Show sample
        print(f"\n📊 Sample stocks:")
        for stock in stocks[:10]:
            print(f"   {stock['ticker']} - {stock['name']} ({stock['sector']})")
        
        # Show sector distribution
        sectors = {}
        for stock in stocks:
            sector = stock.get('sector', 'Unknown')
            sectors[sector] = sectors.get(sector, 0) + 1
        
        print(f"\n📊 Sector Distribution:")
        for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
            print(f"   {sector}: {count} stocks")
    else:
        print("❌ Failed to scrape S&P 500 from all sources")
        print("Using fallback list...")
        from sp500_complete import SP500_STOCKS
        save_stocks_to_file(SP500_STOCKS, 'sp500_scraped.py')

if __name__ == '__main__':
    main()
