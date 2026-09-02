import requests
import sqlite3
import time
from datetime import datetime

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

# ============================================================
# 300+ REAL STOCKS LIST
# ============================================================
REAL_STOCKS = [
    # ===== TECHNOLOGY =====
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
    {"ticker": "MSFT", "name": "Microsoft Corp.", "sector": "Technology"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
    {"ticker": "NVDA", "name": "NVIDIA Corp.", "sector": "Technology"},
    {"ticker": "META", "name": "Meta Platforms", "sector": "Technology"},
    {"ticker": "NFLX", "name": "Netflix Inc.", "sector": "Technology"},
    {"ticker": "ADBE", "name": "Adobe Inc.", "sector": "Technology"},
    {"ticker": "CRM", "name": "Salesforce Inc.", "sector": "Technology"},
    {"ticker": "AMD", "name": "Advanced Micro Devices", "sector": "Technology"},
    {"ticker": "INTC", "name": "Intel Corp.", "sector": "Technology"},
    {"ticker": "IBM", "name": "IBM Corp.", "sector": "Technology"},
    {"ticker": "ORCL", "name": "Oracle Corp.", "sector": "Technology"},
    {"ticker": "CSCO", "name": "Cisco Systems", "sector": "Technology"},
    {"ticker": "TXN", "name": "Texas Instruments", "sector": "Technology"},
    {"ticker": "QCOM", "name": "Qualcomm Inc.", "sector": "Technology"},
    {"ticker": "INTU", "name": "Intuit Inc.", "sector": "Technology"},
    {"ticker": "NOW", "name": "ServiceNow Inc.", "sector": "Technology"},
    {"ticker": "UBER", "name": "Uber Technologies", "sector": "Technology"},
    {"ticker": "SHOP", "name": "Shopify Inc.", "sector": "Technology"},
    {"ticker": "SPOT", "name": "Spotify Technology", "sector": "Technology"},
    {"ticker": "PANW", "name": "Palo Alto Networks", "sector": "Technology"},
    {"ticker": "CRWD", "name": "CrowdStrike Holdings", "sector": "Technology"},
    {"ticker": "FTNT", "name": "Fortinet Inc.", "sector": "Technology"},
    {"ticker": "ZS", "name": "Zscaler Inc.", "sector": "Technology"},
    {"ticker": "OKTA", "name": "Okta Inc.", "sector": "Technology"},
    {"ticker": "DDOG", "name": "Datadog Inc.", "sector": "Technology"},
    {"ticker": "NET", "name": "Cloudflare Inc.", "sector": "Technology"},
    {"ticker": "MDB", "name": "MongoDB Inc.", "sector": "Technology"},
    {"ticker": "HUBS", "name": "HubSpot Inc.", "sector": "Technology"},
    {"ticker": "TEAM", "name": "Atlassian Corp.", "sector": "Technology"},
    {"ticker": "WDAY", "name": "Workday Inc.", "sector": "Technology"},
    {"ticker": "VEEV", "name": "Veeva Systems", "sector": "Technology"},
    {"ticker": "DOCU", "name": "DocuSign Inc.", "sector": "Technology"},
    {"ticker": "ZM", "name": "Zoom Video", "sector": "Technology"},
    {"ticker": "DELL", "name": "Dell Technologies", "sector": "Technology"},
    {"ticker": "HPQ", "name": "HP Inc.", "sector": "Technology"},
    {"ticker": "HPE", "name": "Hewlett Packard Enterprise", "sector": "Technology"},
    
    # ===== HEALTHCARE =====
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
    {"ticker": "UNH", "name": "UnitedHealth Group", "sector": "Healthcare"},
    {"ticker": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare"},
    {"ticker": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare"},
    {"ticker": "MRK", "name": "Merck & Co.", "sector": "Healthcare"},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific", "sector": "Healthcare"},
    {"ticker": "LLY", "name": "Eli Lilly and Co.", "sector": "Healthcare"},
    {"ticker": "AMGN", "name": "Amgen Inc.", "sector": "Healthcare"},
    {"ticker": "CVS", "name": "CVS Health Corp.", "sector": "Healthcare"},
    {"ticker": "GILD", "name": "Gilead Sciences", "sector": "Healthcare"},
    {"ticker": "BMY", "name": "Bristol-Myers Squibb", "sector": "Healthcare"},
    {"ticker": "MDT", "name": "Medtronic plc", "sector": "Healthcare"},
    {"ticker": "SYK", "name": "Stryker Corp.", "sector": "Healthcare"},
    {"ticker": "BSX", "name": "Boston Scientific", "sector": "Healthcare"},
    {"ticker": "ISRG", "name": "Intuitive Surgical", "sector": "Healthcare"},
    {"ticker": "ABT", "name": "Abbott Laboratories", "sector": "Healthcare"},
    {"ticker": "DHR", "name": "Danaher Corp.", "sector": "Healthcare"},
    {"ticker": "EW", "name": "Edwards Lifesciences", "sector": "Healthcare"},
    {"ticker": "HUM", "name": "Humana Inc.", "sector": "Healthcare"},
    {"ticker": "CI", "name": "Cigna Group", "sector": "Healthcare"},
    {"ticker": "ZTS", "name": "Zoetis Inc.", "sector": "Healthcare"},
    {"ticker": "REGN", "name": "Regeneron Pharmaceuticals", "sector": "Healthcare"},
    {"ticker": "VRTX", "name": "Vertex Pharmaceuticals", "sector": "Healthcare"},
    {"ticker": "HCA", "name": "HCA Healthcare", "sector": "Healthcare"},
    {"ticker": "ELV", "name": "Elevance Health", "sector": "Healthcare"},
    {"ticker": "CNC", "name": "Centene Corp.", "sector": "Healthcare"},
    
    # ===== FINANCIAL =====
    {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "Financial"},
    {"ticker": "V", "name": "Visa Inc.", "sector": "Financial"},
    {"ticker": "MA", "name": "Mastercard", "sector": "Financial"},
    {"ticker": "BAC", "name": "Bank of America", "sector": "Financial"},
    {"ticker": "WFC", "name": "Wells Fargo", "sector": "Financial"},
    {"ticker": "C", "name": "Citigroup Inc.", "sector": "Financial"},
    {"ticker": "BLK", "name": "BlackRock Inc.", "sector": "Financial"},
    {"ticker": "GS", "name": "Goldman Sachs", "sector": "Financial"},
    {"ticker": "MS", "name": "Morgan Stanley", "sector": "Financial"},
    {"ticker": "AXP", "name": "American Express", "sector": "Financial"},
    {"ticker": "PYPL", "name": "PayPal Holdings", "sector": "Financial"},
    {"ticker": "SCHW", "name": "Charles Schwab", "sector": "Financial"},
    {"ticker": "PNC", "name": "PNC Financial Services", "sector": "Financial"},
    {"ticker": "USB", "name": "U.S. Bancorp", "sector": "Financial"},
    {"ticker": "TFC", "name": "Truist Financial", "sector": "Financial"},
    {"ticker": "BK", "name": "Bank of New York Mellon", "sector": "Financial"},
    {"ticker": "STT", "name": "State Street Corp.", "sector": "Financial"},
    {"ticker": "NTRS", "name": "Northern Trust Corp.", "sector": "Financial"},
    {"ticker": "FITB", "name": "Fifth Third Bank", "sector": "Financial"},
    {"ticker": "KEY", "name": "KeyCorp", "sector": "Financial"},
    {"ticker": "HBAN", "name": "Huntington Bank", "sector": "Financial"},
    {"ticker": "RF", "name": "Regions Financial", "sector": "Financial"},
    {"ticker": "CFG", "name": "Citizens Financial", "sector": "Financial"},
    {"ticker": "MTB", "name": "M&T Bank", "sector": "Financial"},
    
    # ===== CONSUMER =====
    {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer"},
    {"ticker": "PG", "name": "Procter & Gamble", "sector": "Consumer"},
    {"ticker": "KO", "name": "Coca-Cola Co.", "sector": "Consumer"},
    {"ticker": "PEP", "name": "PepsiCo Inc.", "sector": "Consumer"},
    {"ticker": "HD", "name": "Home Depot", "sector": "Consumer"},
    {"ticker": "MCD", "name": "McDonald's Corp.", "sector": "Consumer"},
    {"ticker": "NKE", "name": "Nike Inc.", "sector": "Consumer"},
    {"ticker": "COST", "name": "Costco Wholesale", "sector": "Consumer"},
    {"ticker": "TGT", "name": "Target Corp.", "sector": "Consumer"},
    {"ticker": "SBUX", "name": "Starbucks Corp.", "sector": "Consumer"},
    {"ticker": "DIS", "name": "Walt Disney Co.", "sector": "Consumer"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Consumer"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer"},
    {"ticker": "CVX", "name": "Chevron Corp.", "sector": "Consumer"},
    {"ticker": "XOM", "name": "Exxon Mobil", "sector": "Consumer"},
    {"ticker": "BA", "name": "Boeing Co.", "sector": "Consumer"},
    {"ticker": "GE", "name": "General Electric", "sector": "Consumer"},
    {"ticker": "CAT", "name": "Caterpillar Inc.", "sector": "Consumer"},
    {"ticker": "UPS", "name": "United Parcel Service", "sector": "Consumer"},
    {"ticker": "MMM", "name": "3M Co.", "sector": "Consumer"},
    {"ticker": "HON", "name": "Honeywell International", "sector": "Consumer"},
    {"ticker": "RTX", "name": "Raytheon Technologies", "sector": "Consumer"},
    {"ticker": "LMT", "name": "Lockheed Martin", "sector": "Consumer"},
    {"ticker": "DE", "name": "Deere & Co.", "sector": "Consumer"},
    {"ticker": "EMR", "name": "Emerson Electric", "sector": "Consumer"},
    {"ticker": "ETN", "name": "Eaton Corp.", "sector": "Consumer"},
    {"ticker": "ITW", "name": "Illinois Tool Works", "sector": "Consumer"},
    {"ticker": "SHW", "name": "Sherwin-Williams", "sector": "Consumer"},
    {"ticker": "DOW", "name": "Dow Inc.", "sector": "Consumer"},
    {"ticker": "DD", "name": "DuPont de Nemours", "sector": "Consumer"},
    {"ticker": "CL", "name": "Colgate-Palmolive", "sector": "Consumer"},
    {"ticker": "KMB", "name": "Kimberly-Clark", "sector": "Consumer"},
    {"ticker": "GIS", "name": "General Mills", "sector": "Consumer"},
    {"ticker": "MDLZ", "name": "Mondelez International", "sector": "Consumer"},
    {"ticker": "HSY", "name": "Hershey Co.", "sector": "Consumer"},
    {"ticker": "MKC", "name": "McCormick & Co.", "sector": "Consumer"},
    {"ticker": "CPB", "name": "Campbell Soup", "sector": "Consumer"},
    {"ticker": "CAG", "name": "Conagra Brands", "sector": "Consumer"},
    {"ticker": "TSN", "name": "Tyson Foods", "sector": "Consumer"},
    
    # ===== INDUSTRIAL =====
    {"ticker": "NOC", "name": "Northrop Grumman", "sector": "Industrial"},
    {"ticker": "GD", "name": "General Dynamics", "sector": "Industrial"},
    {"ticker": "TXT", "name": "Textron Inc.", "sector": "Industrial"},
    {"ticker": "PH", "name": "Parker-Hannifin", "sector": "Industrial"},
    {"ticker": "AME", "name": "AMETEK Inc.", "sector": "Industrial"},
    {"ticker": "ROK", "name": "Rockwell Automation", "sector": "Industrial"},
    {"ticker": "DOV", "name": "Dover Corp.", "sector": "Industrial"},
    {"ticker": "IR", "name": "Ingersoll Rand", "sector": "Industrial"},
    {"ticker": "XYL", "name": "Xylem Inc.", "sector": "Industrial"},
    {"ticker": "WAB", "name": "Westinghouse Air Brake", "sector": "Industrial"},
    {"ticker": "LDOS", "name": "Leidos Holdings", "sector": "Industrial"},
    {"ticker": "GWW", "name": "W.W. Grainger", "sector": "Industrial"},
    {"ticker": "FAST", "name": "Fastenal Co.", "sector": "Industrial"},
    {"ticker": "AOS", "name": "A.O. Smith Corp.", "sector": "Industrial"},
    {"ticker": "RHI", "name": "Robert Half", "sector": "Industrial"},
    {"ticker": "LUV", "name": "Southwest Airlines", "sector": "Industrial"},
    {"ticker": "DAL", "name": "Delta Air Lines", "sector": "Industrial"},
    {"ticker": "UAL", "name": "United Airlines", "sector": "Industrial"},
    {"ticker": "AAL", "name": "American Airlines", "sector": "Industrial"},
    {"ticker": "JBLU", "name": "JetBlue Airways", "sector": "Industrial"},
    {"ticker": "ODFL", "name": "Old Dominion Freight", "sector": "Industrial"},
    {"ticker": "XPO", "name": "XPO Logistics", "sector": "Industrial"},
    {"ticker": "CSX", "name": "CSX Corporation", "sector": "Industrial"},
    {"ticker": "NSC", "name": "Norfolk Southern", "sector": "Industrial"},
    {"ticker": "UNP", "name": "Union Pacific", "sector": "Industrial"},
    {"ticker": "FDX", "name": "FedEx", "sector": "Industrial"},
    
    # ===== ENERGY =====
    {"ticker": "COP", "name": "ConocoPhillips", "sector": "Energy"},
    {"ticker": "SLB", "name": "Schlumberger Ltd.", "sector": "Energy"},
    {"ticker": "EOG", "name": "EOG Resources", "sector": "Energy"},
    {"ticker": "PSX", "name": "Phillips 66", "sector": "Energy"},
    {"ticker": "OXY", "name": "Occidental Petroleum", "sector": "Energy"},
    {"ticker": "MPC", "name": "Marathon Petroleum", "sector": "Energy"},
    {"ticker": "VLO", "name": "Valero Energy", "sector": "Energy"},
    {"ticker": "KMI", "name": "Kinder Morgan", "sector": "Energy"},
    {"ticker": "WMB", "name": "Williams Companies", "sector": "Energy"},
    {"ticker": "OKE", "name": "ONEOK Inc.", "sector": "Energy"},
    {"ticker": "PXD", "name": "Pioneer Natural Resources", "sector": "Energy"},
    {"ticker": "HES", "name": "Hess Corp.", "sector": "Energy"},
    {"ticker": "MRO", "name": "Marathon Oil", "sector": "Energy"},
    {"ticker": "DVN", "name": "Devon Energy", "sector": "Energy"},
    {"ticker": "FANG", "name": "Diamondback Energy", "sector": "Energy"},
    {"ticker": "CTRA", "name": "Coterra Energy", "sector": "Energy"},
    {"ticker": "BKR", "name": "Baker Hughes", "sector": "Energy"},
    {"ticker": "HAL", "name": "Halliburton Co.", "sector": "Energy"},
    {"ticker": "NOV", "name": "NOV Inc.", "sector": "Energy"},
    {"ticker": "APA", "name": "APA Corp.", "sector": "Energy"},
    {"ticker": "EQT", "name": "EQT Corp.", "sector": "Energy"},
    {"ticker": "RRC", "name": "Range Resources", "sector": "Energy"},
    {"ticker": "NRG", "name": "NRG Energy", "sector": "Energy"},
    
    # ===== TELECOM =====
    {"ticker": "VZ", "name": "Verizon Communications", "sector": "Telecom"},
    {"ticker": "T", "name": "AT&T Inc.", "sector": "Telecom"},
    {"ticker": "TMUS", "name": "T-Mobile US", "sector": "Telecom"},
    {"ticker": "CMCSA", "name": "Comcast Corp.", "sector": "Telecom"},
    {"ticker": "CHTR", "name": "Charter Communications", "sector": "Telecom"},
    {"ticker": "FOXA", "name": "Fox Corp.", "sector": "Telecom"},
    {"ticker": "NWSA", "name": "News Corp.", "sector": "Telecom"},
    {"ticker": "WBD", "name": "Warner Bros. Discovery", "sector": "Telecom"},
    {"ticker": "SIRI", "name": "Sirius XM", "sector": "Telecom"},
    {"ticker": "LYV", "name": "Live Nation", "sector": "Telecom"},
    {"ticker": "CCI", "name": "Crown Castle", "sector": "Telecom"},
    {"ticker": "AMT", "name": "American Tower", "sector": "Telecom"},
    {"ticker": "SBAC", "name": "SBA Communications", "sector": "Telecom"},
    {"ticker": "SNAP", "name": "Snap Inc.", "sector": "Telecom"},
]

def get_price(ticker):
    """Fetch real price from Yahoo Finance"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        if not data['chart']['result']:
            return None
            
        result = data['chart']['result'][0]
        meta = result['meta']
        
        price = meta.get('regularMarketPrice', 0)
        if price == 0:
            return None
            
        return {
            'price': round(price, 2),
            'change': round(meta.get('regularMarketChangePercent', 0), 2),
            'volume': meta.get('regularMarketVolume', 0),
        }
    except Exception as e:
        return None

def update_all_stocks():
    """Main function to update all stocks"""
    print("🚀 Fast Updater Started")
    print("=" * 40)
    print(f"📊 Total stocks: {len(REAL_STOCKS)}")
    print("-" * 40)
    
    updated_count = 0
    failed_count = 0
    
    for i, stock in enumerate(REAL_STOCKS, 1):
        print(f"  [{i}/{len(REAL_STOCKS)}] {stock['ticker']}...", end=" ")
        
        price_data = get_price(stock['ticker'])
        
        if price_data and price_data['price'] > 0:
            try:
                conn = sqlite3.connect(DB_PATH, timeout=30)
                c = conn.cursor()
                
                change = price_data['change']
                if change > 3:
                    rating = 'Buy'
                    target = round(price_data['price'] * 1.15, 2)
                elif change > 0:
                    rating = 'Overweight'
                    target = round(price_data['price'] * 1.08, 2)
                else:
                    rating = 'Hold'
                    target = round(price_data['price'] * 1.02, 2)
                
                now = datetime.now().isoformat()
                
                c.execute('''
                    INSERT OR REPLACE INTO stocks (
                        ticker, name, sector, price, `change`, volume,
                        analyst_rating, avg_target, prediction_score, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    stock['ticker'],
                    stock['name'],
                    stock['sector'],
                    price_data['price'],
                    price_data['change'],
                    price_data['volume'],
                    rating,
                    target,
                    int(50 + (change * 5)),
                    now
                ))
                
                conn.commit()
                conn.close()
                updated_count += 1
                print(f"✅ ${price_data['price']} ({price_data['change']}%)")
                
            except Exception as e:
                failed_count += 1
                print(f"❌ DB Error: {str(e)[:30]}")
        else:
            failed_count += 1
            print("❌ No data")
        
        time.sleep(0.2)  # Rate limiting
    
    print("-" * 40)
    print(f"✅ Updated: {updated_count} stocks")
    print(f"❌ Failed: {failed_count} stocks")
    print("=" * 40)
    print("✅ Done!")

if __name__ == '__main__':
    update_all_stocks()