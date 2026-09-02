import requests
import json
import sqlite3
from datetime import datetime

# Get S&P 500 stocks from Wikipedia (free, reliable source)
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
response = requests.get(url)
from bs4 import BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find the table with S&P 500 companies
table = soup.find('table', {'id': 'constituents'})
rows = table.find_all('tr')[1:]  # Skip header

sp500_stocks = []
sector_map = {
    'Information Technology': 'Technology',
    'Health Care': 'Healthcare',
    'Financials': 'Financial',
    'Consumer Discretionary': 'Consumer',
    'Consumer Staples': 'Consumer',
    'Industrials': 'Industrial',
    'Energy': 'Energy',
    'Communication Services': 'Telecom',
    'Utilities': 'Utilities',
    'Real Estate': 'Real Estate',
    'Materials': 'Materials'
}

for row in rows:
    cols = row.find_all('td')
    if len(cols) >= 4:
        ticker = cols[0].text.strip()
        name = cols[1].text.strip()
        sector = cols[3].text.strip()
        sector = sector_map.get(sector, sector)
        
        sp500_stocks.append({
            'ticker': ticker,
            'name': name,
            'sector': sector
        })

print(f"✅ Found {len(sp500_stocks)} S&P 500 stocks")

# Save to file
with open('sp500_complete.py', 'w') as f:
    f.write(f'SP500_STOCKS = {sp500_stocks}\n')
    f.write(f'print(f"✅ Loaded {{len(SP500_STOCKS)}} stocks")\n')

print("✅ Saved to sp500_complete.py")
