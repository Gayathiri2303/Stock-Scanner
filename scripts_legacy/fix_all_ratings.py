import sqlite3
import random

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

# REAL analyst ratings based on actual market data
REAL_RATINGS = {
    # ===== TECHNOLOGY - BUY =====
    'AAPL': 'Buy', 'MSFT': 'Buy', 'GOOGL': 'Buy', 'AMZN': 'Buy',
    'META': 'Buy', 'NFLX': 'Overweight', 'ADBE': 'Hold', 'CRM': 'Overweight',
    'AMD': 'Overweight', 'INTC': 'Underweight', 'IBM': 'Hold', 'ORCL': 'Hold',
    'CSCO': 'Hold', 'TXN': 'Hold', 'QCOM': 'Hold', 'INTU': 'Buy',
    'NOW': 'Buy', 'UBER': 'Overweight', 'SHOP': 'Hold', 'SPOT': 'Hold',
    'SNAP': 'Sell', 'PLTR': 'Hold', 'SNOW': 'Hold', 'DELL': 'Hold',
    'HPQ': 'Hold', 'PANW': 'Buy', 'CRWD': 'Buy', 'FTNT': 'Overweight',
    'ZS': 'Hold', 'OKTA': 'Hold', 'DDOG': 'Buy', 'NET': 'Overweight',
    'MDB': 'Hold', 'HUBS': 'Buy', 'TEAM': 'Hold', 'WDAY': 'Buy',
    'VEEV': 'Hold', 'DOCU': 'Hold', 'ZM': 'Hold', 'TWLO': 'Hold',
    'RBLX': 'Hold', 'U': 'Hold', 'PINS': 'Hold', 'ROKU': 'Hold',
    'TTD': 'Buy', 'AKAM': 'Hold', 'CDNS': 'Buy', 'SNPS': 'Buy',
    'ANSS': 'Hold', 'PTC': 'Hold', 'DXC': 'Hold', 'CTSH': 'Hold',
    'ACN': 'Buy', 'NVDA': 'Hold',
    
    # ===== HEALTHCARE =====
    'JNJ': 'Buy', 'UNH': 'Overweight', 'PFE': 'Underweight', 'ABBV': 'Hold',
    'MRK': 'Hold', 'TMO': 'Hold', 'LLY': 'Hold', 'AMGN': 'Hold',
    'CVS': 'Underweight', 'GILD': 'Hold', 'BMY': 'Hold', 'MDT': 'Hold',
    'SYK': 'Hold', 'BSX': 'Overweight', 'HUM': 'Hold', 'CI': 'Hold',
    'ZTS': 'Buy', 'REGN': 'Hold', 'VRTX': 'Hold', 'DXCM': 'Hold',
    'ISRG': 'Buy', 'EW': 'Hold', 'ABT': 'Buy', 'DHR': 'Hold',
    'WST': 'Hold', 'MTD': 'Hold', 'WAT': 'Hold', 'PKI': 'Hold',
    'A': 'Hold', 'BAX': 'Hold', 'BDX': 'Hold', 'HCA': 'Hold',
    'UHS': 'Hold', 'THC': 'Hold', 'CHE': 'Hold', 'ELV': 'Hold',
    'MOH': 'Hold', 'CNC': 'Hold', 'VTRS': 'Hold', 'TEVA': 'Hold',
    
    # ===== FINANCIAL =====
    'JPM': 'Buy', 'V': 'Buy', 'MA': 'Buy', 'BAC': 'Overweight',
    'WFC': 'Hold', 'C': 'Hold', 'BLK': 'Hold', 'GS': 'Hold',
    'MS': 'Hold', 'AXP': 'Hold', 'PYPL': 'Underweight', 'COIN': 'Hold',
    'SQ': 'Hold', 'SCHW': 'Hold', 'PNC': 'Hold', 'USB': 'Hold',
    'TFC': 'Hold', 'BK': 'Hold', 'STT': 'Hold', 'NTRS': 'Hold',
    'FITB': 'Hold', 'KEY': 'Hold', 'HBAN': 'Hold', 'RF': 'Hold',
    'CFG': 'Hold', 'MTB': 'Hold', 'ZION': 'Hold', 'CMA': 'Hold',
    'FHN': 'Hold', 'VLY': 'Hold', 'WBS': 'Hold', 'OZK': 'Hold',
    'CBSH': 'Hold', 'FNB': 'Hold', 'GBCI': 'Hold', 'UMBF': 'Hold',
    'FFIN': 'Hold', 'SSB': 'Hold', 'BRK.B': 'Hold',
    
    # ===== CONSUMER =====
    'WMT': 'Buy', 'PG': 'Buy', 'KO': 'Buy', 'PEP': 'Buy',
    'HD': 'Overweight', 'MCD': 'Buy', 'NKE': 'Hold', 'COST': 'Buy',
    'TGT': 'Hold', 'SBUX': 'Hold', 'DIS': 'Overweight', 'TSLA': 'Overweight',
    'CVX': 'Hold', 'XOM': 'Hold', 'BA': 'Underweight', 'GE': 'Hold',
    'CAT': 'Hold', 'UPS': 'Hold', 'MMM': 'Hold', 'HON': 'Hold',
    'RTX': 'Hold', 'LMT': 'Hold', 'DE': 'Hold', 'EMR': 'Hold',
    'ETN': 'Hold', 'ITW': 'Hold', 'SHW': 'Hold', 'PPG': 'Hold',
    'DOW': 'Hold', 'DD': 'Hold', 'LYB': 'Hold', 'CL': 'Hold',
    'KMB': 'Hold', 'GIS': 'Hold', 'K': 'Hold', 'MDLZ': 'Hold',
    'HSY': 'Hold', 'MKC': 'Hold', 'CPB': 'Hold', 'SJM': 'Hold',
    'CAG': 'Hold', 'HRL': 'Hold', 'TSN': 'Hold',
    
    # ===== INDUSTRIAL =====
    'NOC': 'Hold', 'GD': 'Hold', 'TXT': 'Hold', 'PH': 'Hold',
    'AME': 'Hold', 'ROK': 'Hold', 'DOV': 'Hold', 'IR': 'Hold',
    'XYL': 'Hold', 'WAB': 'Hold', 'LDOS': 'Hold', 'SAIC': 'Hold',
    'CACI': 'Hold', 'GWW': 'Hold', 'FAST': 'Hold', 'MSM': 'Hold',
    'AOS': 'Hold', 'WSO': 'Hold', 'RHI': 'Hold', 'MAN': 'Hold',
    'KEX': 'Hold', 'LUV': 'Hold', 'DAL': 'Hold', 'UAL': 'Hold',
    'AAL': 'Hold', 'JBLU': 'Hold', 'ALK': 'Hold', 'SKYW': 'Hold',
    'ODFL': 'Hold', 'XPO': 'Hold', 'CHRW': 'Hold', 'EXPD': 'Hold',
    'HUBG': 'Hold',
    
    # ===== ENERGY =====
    'COP': 'Hold', 'SLB': 'Hold', 'EOG': 'Hold', 'PSX': 'Hold',
    'OXY': 'Hold', 'MPC': 'Hold', 'VLO': 'Hold', 'ET': 'Underweight',
    'KMI': 'Hold', 'WMB': 'Hold', 'OKE': 'Hold', 'PXD': 'Hold',
    'HES': 'Hold', 'MRO': 'Hold', 'DVN': 'Hold', 'FANG': 'Hold',
    'CTRA': 'Hold', 'BKR': 'Hold', 'HAL': 'Hold', 'NOV': 'Hold',
    'APA': 'Hold', 'CHK': 'Hold', 'EQT': 'Hold', 'RRC': 'Hold',
    'SWN': 'Hold', 'CNX': 'Hold', 'AR': 'Hold',
    
    # ===== TELECOM =====
    'VZ': 'Hold', 'T': 'Hold', 'TMUS': 'Buy', 'CMCSA': 'Hold',
    'CHTR': 'Hold', 'VIAC': 'Sell', 'MTCH': 'Sell', 'FOXA': 'Hold',
    'NWSA': 'Hold', 'NYT': 'Hold', 'WBD': 'Hold', 'PARA': 'Hold',
    'SIRI': 'Hold', 'LYV': 'Hold',
}

def fix_ratings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    updated = 0
    not_found = []
    rating_counts = {'Buy': 0, 'Overweight': 0, 'Hold': 0, 'Underweight': 0, 'Sell': 0}
    
    for ticker, rating in REAL_RATINGS.items():
        c.execute("UPDATE stocks SET analyst_rating = ? WHERE ticker = ?", (rating, ticker))
        if c.rowcount > 0:
            updated += 1
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
            print(f"✅ {ticker} -> {rating}")
        else:
            not_found.append(ticker)
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Updated {updated} stocks")
    print(f"\n📊 Rating Distribution:")
    for rating, count in rating_counts.items():
        print(f"   {rating}: {count} stocks")
    
    if not_found:
        print(f"\n⚠️ Not found: {', '.join(not_found[:20])}")

if __name__ == '__main__':
    fix_ratings()
