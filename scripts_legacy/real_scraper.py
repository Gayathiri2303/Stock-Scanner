import requests
import sqlite3
import time
from datetime import datetime

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

# 300+ REAL S&P 500 Stocks
REAL_STOCKS = [
    # ===== TECHNOLOGY (60 stocks) =====
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
    {"ticker": "TWLO", "name": "Twilio Inc.", "sector": "Technology"},
    {"ticker": "RBLX", "name": "Roblox Corp.", "sector": "Technology"},
    {"ticker": "U", "name": "Unity Software", "sector": "Technology"},
    {"ticker": "PINS", "name": "Pinterest Inc.", "sector": "Technology"},
    {"ticker": "ROKU", "name": "Roku Inc.", "sector": "Technology"},
    {"ticker": "TTD", "name": "Trade Desk Inc.", "sector": "Technology"},
    {"ticker": "AKAM", "name": "Akamai Technologies", "sector": "Technology"},
    {"ticker": "CDNS", "name": "Cadence Design Systems", "sector": "Technology"},
    {"ticker": "SNPS", "name": "Synopsys Inc.", "sector": "Technology"},
    {"ticker": "ANSS", "name": "ANSYS Inc.", "sector": "Technology"},
    {"ticker": "PTC", "name": "PTC Inc.", "sector": "Technology"},
    {"ticker": "DXC", "name": "DXC Technology", "sector": "Technology"},
    {"ticker": "CTSH", "name": "Cognizant Technology", "sector": "Technology"},
    {"ticker": "ACN", "name": "Accenture plc", "sector": "Technology"},
    {"ticker": "INFY", "name": "Infosys Ltd.", "sector": "Technology"},
    {"ticker": "WIT", "name": "Wipro Ltd.", "sector": "Technology"},
    {"ticker": "HCLTECH", "name": "HCL Technologies", "sector": "Technology"},
    {"ticker": "TCS", "name": "Tata Consultancy Services", "sector": "Technology"},
    {"ticker": "TECHM", "name": "Tech Mahindra", "sector": "Technology"},
    {"ticker": "LTTS", "name": "L&T Technology Services", "sector": "Technology"},
    {"ticker": "DELL", "name": "Dell Technologies", "sector": "Technology"},
    {"ticker": "HPQ", "name": "HP Inc.", "sector": "Technology"},
    {"ticker": "HPE", "name": "Hewlett Packard Enterprise", "sector": "Technology"},
    {"ticker": "JBL", "name": "Jabil Inc.", "sector": "Technology"},
    {"ticker": "FLEX", "name": "Flex Ltd.", "sector": "Technology"},
    {"ticker": "GLW", "name": "Corning Inc.", "sector": "Technology"},
    {"ticker": "APH", "name": "Amphenol Corp.", "sector": "Technology"},
    
    # ===== HEALTHCARE (50 stocks) =====
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
    {"ticker": "DXCM", "name": "DexCom Inc.", "sector": "Healthcare"},
    {"ticker": "HCA", "name": "HCA Healthcare", "sector": "Healthcare"},
    {"ticker": "UHS", "name": "Universal Health Services", "sector": "Healthcare"},
    {"ticker": "THC", "name": "Tenet Healthcare", "sector": "Healthcare"},
    {"ticker": "CHE", "name": "Chemed Corp.", "sector": "Healthcare"},
    {"ticker": "ELV", "name": "Elevance Health", "sector": "Healthcare"},
    {"ticker": "MOH", "name": "Molina Healthcare", "sector": "Healthcare"},
    {"ticker": "CNC", "name": "Centene Corp.", "sector": "Healthcare"},
    {"ticker": "VTRS", "name": "Viatris Inc.", "sector": "Healthcare"},
    {"ticker": "TEVA", "name": "Teva Pharmaceutical", "sector": "Healthcare"},
    {"ticker": "NVO", "name": "Novo Nordisk", "sector": "Healthcare"},
    {"ticker": "NVS", "name": "Novartis AG", "sector": "Healthcare"},
    {"ticker": "GSK", "name": "GSK plc", "sector": "Healthcare"},
    {"ticker": "AZN", "name": "AstraZeneca plc", "sector": "Healthcare"},
    {"ticker": "SNY", "name": "Sanofi SA", "sector": "Healthcare"},
    {"ticker": "RHHBY", "name": "Roche Holding AG", "sector": "Healthcare"},
    {"ticker": "BAX", "name": "Baxter International", "sector": "Healthcare"},
    {"ticker": "BDX", "name": "Becton Dickinson", "sector": "Healthcare"},
    {"ticker": "WST", "name": "West Pharmaceutical", "sector": "Healthcare"},
    {"ticker": "MTD", "name": "Mettler Toledo", "sector": "Healthcare"},
    {"ticker": "WAT", "name": "Waters Corp.", "sector": "Healthcare"},
    {"ticker": "PKI", "name": "PerkinElmer Inc.", "sector": "Healthcare"},
    {"ticker": "A", "name": "Agilent Technologies", "sector": "Healthcare"},
    {"ticker": "BIIB", "name": "Biogen", "sector": "Healthcare"},
    {"ticker": "INCY", "name": "Incyte", "sector": "Healthcare"},
    {"ticker": "MRNA", "name": "Moderna", "sector": "Healthcare"},
    {"ticker": "BIO", "name": "Bio-Rad Laboratories", "sector": "Healthcare"},
    
    # ===== FINANCIAL (50 stocks) =====
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
    {"ticker": "COIN", "name": "Coinbase Global", "sector": "Financial"},
    {"ticker": "SQ", "name": "Block Inc.", "sector": "Financial"},
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
    {"ticker": "ZION", "name": "Zions Bancorp", "sector": "Financial"},
    {"ticker": "CMA", "name": "Comerica Inc.", "sector": "Financial"},
    {"ticker": "FHN", "name": "First Horizon Corp.", "sector": "Financial"},
    {"ticker": "VLY", "name": "Valley National Bancorp", "sector": "Financial"},
    {"ticker": "WBS", "name": "Webster Financial", "sector": "Financial"},
    {"ticker": "OZK", "name": "Bank OZK", "sector": "Financial"},
    {"ticker": "CBSH", "name": "Commerce Bancshares", "sector": "Financial"},
    {"ticker": "FNB", "name": "FNB Corp.", "sector": "Financial"},
    {"ticker": "GBCI", "name": "Glacier Bancorp", "sector": "Financial"},
    {"ticker": "UMBF", "name": "UMB Financial", "sector": "Financial"},
    {"ticker": "FFIN", "name": "First Financial Bankshares", "sector": "Financial"},
    {"ticker": "SSB", "name": "SouthState Corp.", "sector": "Financial"},
    {"ticker": "ABC", "name": "AmerisourceBergen", "sector": "Financial"},
    {"ticker": "MCK", "name": "McKesson Corp.", "sector": "Financial"},
    {"ticker": "CAH", "name": "Cardinal Health", "sector": "Financial"},
    {"ticker": "BRK.B", "name": "Berkshire Hathaway", "sector": "Financial"},
    {"ticker": "AIG", "name": "American International Group", "sector": "Financial"},
    {"ticker": "AFL", "name": "Aflac", "sector": "Financial"},
    {"ticker": "ALL", "name": "Allstate", "sector": "Financial"},
    {"ticker": "MET", "name": "MetLife", "sector": "Financial"},
    {"ticker": "PRU", "name": "Prudential Financial", "sector": "Financial"},
    {"ticker": "CB", "name": "Chubb Limited", "sector": "Financial"},
    {"ticker": "PGR", "name": "Progressive Corporation", "sector": "Financial"},
    {"ticker": "HIG", "name": "Hartford", "sector": "Financial"},
    
    # ===== CONSUMER (50 stocks) =====
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
    {"ticker": "PPG", "name": "PPG Industries", "sector": "Consumer"},
    {"ticker": "DOW", "name": "Dow Inc.", "sector": "Consumer"},
    {"ticker": "DD", "name": "DuPont de Nemours", "sector": "Consumer"},
    {"ticker": "LYB", "name": "LyondellBasell", "sector": "Consumer"},
    {"ticker": "CL", "name": "Colgate-Palmolive", "sector": "Consumer"},
    {"ticker": "KMB", "name": "Kimberly-Clark", "sector": "Consumer"},
    {"ticker": "GIS", "name": "General Mills", "sector": "Consumer"},
    {"ticker": "K", "name": "Kellogg Co.", "sector": "Consumer"},
    {"ticker": "MDLZ", "name": "Mondelez International", "sector": "Consumer"},
    {"ticker": "HSY", "name": "Hershey Co.", "sector": "Consumer"},
    {"ticker": "MKC", "name": "McCormick & Co.", "sector": "Consumer"},
    {"ticker": "CPB", "name": "Campbell Soup", "sector": "Consumer"},
    {"ticker": "SJM", "name": "J.M. Smucker Co.", "sector": "Consumer"},
    {"ticker": "CAG", "name": "Conagra Brands", "sector": "Consumer"},
    {"ticker": "HRL", "name": "Hormel Foods", "sector": "Consumer"},
    {"ticker": "TSN", "name": "Tyson Foods", "sector": "Consumer"},
    {"ticker": "BF.B", "name": "Brown-Forman", "sector": "Consumer"},
    {"ticker": "STZ", "name": "Constellation Brands", "sector": "Consumer"},
    {"ticker": "TAP", "name": "Molson Coors", "sector": "Consumer"},
    {"ticker": "LW", "name": "Lamb Weston", "sector": "Consumer"},
    {"ticker": "TWN", "name": "Hostess Brands", "sector": "Consumer"},
    {"ticker": "ABNB", "name": "Airbnb", "sector": "Consumer"},
    
    # ===== INDUSTRIAL (40 stocks) =====
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
    {"ticker": "SAIC", "name": "Science Applications", "sector": "Industrial"},
    {"ticker": "CACI", "name": "CACI International", "sector": "Industrial"},
    {"ticker": "GWW", "name": "W.W. Grainger", "sector": "Industrial"},
    {"ticker": "FAST", "name": "Fastenal Co.", "sector": "Industrial"},
    {"ticker": "MSM", "name": "MSC Industrial Direct", "sector": "Industrial"},
    {"ticker": "AOS", "name": "A.O. Smith Corp.", "sector": "Industrial"},
    {"ticker": "WSO", "name": "Watsco Inc.", "sector": "Industrial"},
    {"ticker": "RHI", "name": "Robert Half", "sector": "Industrial"},
    {"ticker": "MAN", "name": "ManpowerGroup", "sector": "Industrial"},
    {"ticker": "KEX", "name": "Kirby Corp.", "sector": "Industrial"},
    {"ticker": "LUV", "name": "Southwest Airlines", "sector": "Industrial"},
    {"ticker": "DAL", "name": "Delta Air Lines", "sector": "Industrial"},
    {"ticker": "UAL", "name": "United Airlines", "sector": "Industrial"},
    {"ticker": "AAL", "name": "American Airlines", "sector": "Industrial"},
    {"ticker": "JBLU", "name": "JetBlue Airways", "sector": "Industrial"},
    {"ticker": "ALK", "name": "Alaska Air Group", "sector": "Industrial"},
    {"ticker": "SKYW", "name": "SkyWest Inc.", "sector": "Industrial"},
    {"ticker": "ODFL", "name": "Old Dominion Freight", "sector": "Industrial"},
    {"ticker": "XPO", "name": "XPO Logistics", "sector": "Industrial"},
    {"ticker": "CHRW", "name": "C.H. Robinson", "sector": "Industrial"},
    {"ticker": "EXPD", "name": "Expeditors International", "sector": "Industrial"},
    {"ticker": "HUBG", "name": "Hub Group", "sector": "Industrial"},
    {"ticker": "CSX", "name": "CSX Corporation", "sector": "Industrial"},
    {"ticker": "NSC", "name": "Norfolk Southern", "sector": "Industrial"},
    {"ticker": "UNP", "name": "Union Pacific", "sector": "Industrial"},
    {"ticker": "FDX", "name": "FedEx", "sector": "Industrial"},
    {"ticker": "UPS", "name": "United Parcel Service", "sector": "Industrial"},
    {"ticker": "GNRC", "name": "Generac", "sector": "Industrial"},
    {"ticker": "PWR", "name": "Quanta Services", "sector": "Industrial"},
    
    # ===== ENERGY (30 stocks) =====
    {"ticker": "COP", "name": "ConocoPhillips", "sector": "Energy"},
    {"ticker": "SLB", "name": "Schlumberger Ltd.", "sector": "Energy"},
    {"ticker": "EOG", "name": "EOG Resources", "sector": "Energy"},
    {"ticker": "PSX", "name": "Phillips 66", "sector": "Energy"},
    {"ticker": "OXY", "name": "Occidental Petroleum", "sector": "Energy"},
    {"ticker": "MPC", "name": "Marathon Petroleum", "sector": "Energy"},
    {"ticker": "VLO", "name": "Valero Energy", "sector": "Energy"},
    {"ticker": "ET", "name": "Energy Transfer LP", "sector": "Energy"},
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
    {"ticker": "CHK", "name": "Chesapeake Energy", "sector": "Energy"},
    {"ticker": "EQT", "name": "EQT Corp.", "sector": "Energy"},
    {"ticker": "RRC", "name": "Range Resources", "sector": "Energy"},
    {"ticker": "SWN", "name": "Southwestern Energy", "sector": "Energy"},
    {"ticker": "CNX", "name": "CNX Resources", "sector": "Energy"},
    {"ticker": "AR", "name": "Antero Resources", "sector": "Energy"},
    {"ticker": "CHRD", "name": "Chord Energy", "sector": "Energy"},
    {"ticker": "TPL", "name": "Texas Pacific Land", "sector": "Energy"},
    {"ticker": "NRG", "name": "NRG Energy", "sector": "Energy"},
    
    # ===== TELECOM (20 stocks) =====
    {"ticker": "VZ", "name": "Verizon Communications", "sector": "Telecom"},
    {"ticker": "T", "name": "AT&T Inc.", "sector": "Telecom"},
    {"ticker": "TMUS", "name": "T-Mobile US", "sector": "Telecom"},
    {"ticker": "CMCSA", "name": "Comcast Corp.", "sector": "Telecom"},
    {"ticker": "CHTR", "name": "Charter Communications", "sector": "Telecom"},
    {"ticker": "VIAC", "name": "Paramount Global", "sector": "Telecom"},
    {"ticker": "MTCH", "name": "Match Group", "sector": "Telecom"},
    {"ticker": "FOXA", "name": "Fox Corp.", "sector": "Telecom"},
    {"ticker": "NWSA", "name": "News Corp.", "sector": "Telecom"},
    {"ticker": "NYT", "name": "New York Times", "sector": "Telecom"},
    {"ticker": "WBD", "name": "Warner Bros. Discovery", "sector": "Telecom"},
    {"ticker": "PARA", "name": "Paramount Global", "sector": "Telecom"},
    {"ticker": "SIRI", "name": "Sirius XM", "sector": "Telecom"},
    {"ticker": "LYV", "name": "Live Nation", "sector": "Telecom"},
    {"ticker": "CCI", "name": "Crown Castle", "sector": "Telecom"},
    {"ticker": "AMT", "name": "American Tower", "sector": "Telecom"},
    {"ticker": "SBAC", "name": "SBA Communications", "sector": "Telecom"},
    {"ticker": "ECHO", "name": "EchoStar", "sector": "Telecom"},
    {"ticker": "RDDT", "name": "Reddit", "sector": "Telecom"},
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

def insert_stock(c, stock, price_data):
    """Insert or update a stock in the database"""
    now = datetime.now().isoformat()
    
    # Determine analyst rating based on change
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

def update_all_stocks():
    """Main function to update all stocks"""
    print("🚀 REAL Stock Price Updater Started")
    print("=" * 50)
    print(f"📊 Total stocks: {len(REAL_STOCKS)}")
    print("-" * 50)
    
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        c = conn.cursor()
        
        # Create table if it doesn't exist (SQLite compatible)
        c.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                ticker VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100),
                price DECIMAL(10,2),
                `change` DECIMAL(8,2),
                volume BIGINT,
                market_cap DECIMAL(20,2),
                pe_ratio DECIMAL(10,2),
                high_52w DECIMAL(10,2),
                low_52w DECIMAL(10,2),
                dividend_yield DECIMAL(8,2),
                sector VARCHAR(50),
                analyst_rating VARCHAR(20),
                avg_target DECIMAL(10,2),
                revenue_10yr TEXT,
                profit_margin DECIMAL(8,2),
                debt_equity DECIMAL(10,2),
                earnings_date VARCHAR(50),
                news TEXT,
                prediction_score INT,
                updated_at DATETIME,
                usd_inr DECIMAL(10,2),
                best_month VARCHAR(20),
                best_return DECIMAL(8,2),
                worst_month VARCHAR(20),
                worst_return DECIMAL(8,2),
                seasonal_strength INT,
                volatility DECIMAL(8,2)
            )
        ''')
        
        # Create watchlist table (SQLite compatible)
        c.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) DEFAULT 'admin',
                ticker VARCHAR(20),
                added_date DATETIME,
                UNIQUE (username, ticker)
            )
        ''')
        
        print(f"📊 Updating {len(REAL_STOCKS)} stocks...")
        print("-" * 50)
        
        updated_count = 0
        for i, stock in enumerate(REAL_STOCKS, 1):
            print(f"  [{i}/{len(REAL_STOCKS)}] {stock['ticker']}...", end=" ")
            price_data = get_price(stock['ticker'])
            
            if price_data and price_data['price'] > 0:
                insert_stock(c, stock, price_data)
                updated_count += 1
                print(f"✅ ${price_data['price']} ({price_data['change']}%)")
            else:
                print("❌ No data")
            
            time.sleep(0.3)  # Rate limiting
        
        conn.commit()
        conn.close()
        
        print("-" * 50)
        print(f"✅ Updated {updated_count} out of {len(REAL_STOCKS)} stocks with REAL prices!")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == '__main__':
    update_all_stocks()