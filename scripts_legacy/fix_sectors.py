import sqlite3

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

# Map sub-industries to main sectors
SECTOR_MAP = {
    # Technology
    'Software': 'Technology',
    'Software—Infrastructure': 'Technology',
    'Software—Application': 'Technology',
    'Semiconductors': 'Technology',
    'Semiconductor Equipment & Materials': 'Technology',
    'Information Technology Services': 'Technology',
    'IT Services': 'Technology',
    'Electronic Components': 'Technology',
    'Consumer Electronics': 'Technology',
    'Computer Hardware': 'Technology',
    'Data Processing': 'Technology',
    'Cloud Computing': 'Technology',
    'Cybersecurity': 'Technology',
    'Artificial Intelligence': 'Technology',
    'Tech Hardware': 'Technology',
    
    # Healthcare
    'Drug Manufacturers': 'Healthcare',
    'Drug Manufacturers—General': 'Healthcare',
    'Drug Manufacturers—Specialty & Generic': 'Healthcare',
    'Biotechnology': 'Healthcare',
    'Medical Devices': 'Healthcare',
    'Medical Instruments & Supplies': 'Healthcare',
    'Diagnostics & Research': 'Healthcare',
    'Health Care Plans': 'Healthcare',
    'Health Care Information Services': 'Healthcare',
    'Medical Care Facilities': 'Healthcare',
    'Pharmaceuticals': 'Healthcare',
    'Biosimilars': 'Healthcare',
    
    # Financial
    'Banks': 'Financial',
    'Banks—Regional': 'Financial',
    'Banks—Diversified': 'Financial',
    'Insurance': 'Financial',
    'Insurance—Life': 'Financial',
    'Insurance—Property & Casualty': 'Financial',
    'Insurance—Reinsurance': 'Financial',
    'Capital Markets': 'Financial',
    'Asset Management': 'Financial',
    'Financial Data & Stock Exchanges': 'Financial',
    'Credit Services': 'Financial',
    'Consumer Finance': 'Financial',
    'Investment Banking': 'Financial',
    'Financial Conglomerates': 'Financial',
    
    # Consumer
    'Consumer Packaged Goods': 'Consumer',
    'Consumer Goods': 'Consumer',
    'Retail': 'Consumer',
    'Retail—Apparel & Specialty': 'Consumer',
    'Retail—Cyclical': 'Consumer',
    'Retail—Defensive': 'Consumer',
    'Auto Manufacturers': 'Consumer',
    'Automobiles': 'Consumer',
    'Restaurants': 'Consumer',
    'Leisure': 'Consumer',
    'Entertainment': 'Consumer',
    'Travel & Leisure': 'Consumer',
    'Food & Beverage': 'Consumer',
    'Beverages': 'Consumer',
    'Household & Personal Products': 'Consumer',
    'Apparel': 'Consumer',
    'Luxury Goods': 'Consumer',
    'E-commerce': 'Consumer',
    
    # Industrial
    'Industrial Products': 'Industrial',
    'Machinery': 'Industrial',
    'Aerospace & Defense': 'Industrial',
    'Airlines': 'Industrial',
    'Airports & Air Services': 'Industrial',
    'Shipping': 'Industrial',
    'Logistics': 'Industrial',
    'Transportation': 'Industrial',
    'Railroads': 'Industrial',
    'Trucking': 'Industrial',
    'Construction': 'Industrial',
    'Engineering & Construction': 'Industrial',
    'Building Products': 'Industrial',
    'Specialty Industrial Machinery': 'Industrial',
    'Electrical Equipment': 'Industrial',
    'Tools & Accessories': 'Industrial',
    
    # Energy
    'Oil & Gas': 'Energy',
    'Oil & Gas E&P': 'Energy',
    'Oil & Gas Integrated': 'Energy',
    'Oil & Gas Midstream': 'Energy',
    'Oil & Gas Refining': 'Energy',
    'Oil & Gas Services': 'Energy',
    'Oil & Gas Drilling': 'Energy',
    'Oil & Gas Equipment': 'Energy',
    'Independent Power Producers': 'Energy',
    'Independent Power Producers & Energy Traders': 'Energy',
    'Renewable Energy': 'Energy',
    'Solar Energy': 'Energy',
    'Wind Energy': 'Energy',
    'Energy Infrastructure': 'Energy',
    'Energy Services': 'Energy',
    
    # Telecom
    'Telecommunications': 'Telecom',
    'Communication & Networking': 'Telecom',
    'Communication Equipment': 'Telecom',
    'Broadcasting': 'Telecom',
    'Media': 'Telecom',
    'Cable TV': 'Telecom',
    'Wireless Communications': 'Telecom',
    'Internet & Digital Media': 'Telecom',
    
    # Utilities
    'Utilities': 'Utilities',
    'Electric Utilities': 'Utilities',
    'Water Utilities': 'Utilities',
    'Gas Utilities': 'Utilities',
    'Renewable Utilities': 'Utilities',
    
    # Real Estate
    'Real Estate': 'Real Estate',
    'Office REITs': 'Real Estate',
    'Residential REITs': 'Real Estate',
    'Retail REITs': 'Real Estate',
    'Industrial REITs': 'Real Estate',
    'Healthcare REITs': 'Real Estate',
    'Hotel REITs': 'Real Estate',
    
    # Materials
    'Materials': 'Materials',
    'Chemicals': 'Materials',
    'Specialty Chemicals': 'Materials',
    'Industrial Gases': 'Materials',
    'Metals': 'Materials',
    'Mining': 'Materials',
    'Forest Products': 'Materials',
    'Paper & Paper Products': 'Materials',
    'Plastics': 'Materials',
}

def fix_sectors():
    """Update sectors in database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get all stocks with their sectors
    c.execute("SELECT ticker, sector FROM stocks WHERE sector IS NOT NULL")
    stocks = c.fetchall()
    
    updated = 0
    sector_counts = {}
    
    for ticker, sector in stocks:
        if sector:
            # Check if sector is in map or use as-is
            mapped_sector = SECTOR_MAP.get(sector)
            if mapped_sector:
                # Update with mapped sector
                c.execute("UPDATE stocks SET sector = ? WHERE ticker = ?", (mapped_sector, ticker))
                updated += 1
                sector_counts[mapped_sector] = sector_counts.get(mapped_sector, 0) + 1
            else:
                # Try partial match
                for key, value in SECTOR_MAP.items():
                    if key.lower() in sector.lower() or sector.lower() in key.lower():
                        c.execute("UPDATE stocks SET sector = ? WHERE ticker = ?", (value, ticker))
                        updated += 1
                        sector_counts[value] = sector_counts.get(value, 0) + 1
                        break
    
    conn.commit()
    conn.close()
    
    print(f"✅ Updated {updated} stocks with correct sectors")
    print(f"\n📊 New Sector Distribution:")
    for sector, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {sector}: {count} stocks")

def show_sample():
    """Show sample of updated sectors"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("\n📊 Sample Stocks with Correct Sectors:")
    c.execute("SELECT ticker, name, sector FROM stocks ORDER BY RANDOM() LIMIT 20")
    for ticker, name, sector in c.fetchall():
        print(f"   {ticker}: {sector}")
    
    conn.close()

if __name__ == '__main__':
    fix_sectors()
    show_sample()
