#!/usr/bin/env python3
"""
Populate realistic seasonal data for all stocks in stocks.db
Run this once (or after you refresh stock data).
"""

import sqlite3
import random
from datetime import datetime

DB_PATH = "/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db"

# Realistic best/worst months by sector (common seasonal patterns)
SECTOR_PATTERNS = {
    "Technology": {
        "best_months": ["November", "January", "October"],
        "worst_months": ["May", "August", "September"],
        "strength_range": (55, 85),
    },
    "Healthcare": {
        "best_months": ["January", "April", "November"],
        "worst_months": ["June", "August", "September"],
        "strength_range": (50, 80),
    },
    "Financial": {
        "best_months": ["November", "December", "January"],
        "worst_months": ["May", "June", "September"],
        "strength_range": (45, 75),
    },
    "Energy": {
        "best_months": ["February", "March", "November"],
        "worst_months": ["July", "August", "May"],
        "strength_range": (50, 82),
    },
    "Consumer": {
        "best_months": ["November", "December", "March"],
        "worst_months": ["June", "August", "February"],
        "strength_range": (48, 78),
    },
    "Industrial": {
        "best_months": ["January", "March", "November"],
        "worst_months": ["May", "August", "September"],
        "strength_range": (45, 75),
    },
    "Automotive": {
        "best_months": ["March", "April", "November"],
        "worst_months": ["July", "August", "December"],
        "strength_range": (42, 72),
    },
    "Telecom": {
        "best_months": ["November", "January", "April"],
        "worst_months": ["June", "August", "September"],
        "strength_range": (40, 70),
    },
}

DEFAULT_PATTERN = {
    "best_months": ["November", "January", "April"],
    "worst_months": ["May", "August", "September"],
    "strength_range": (45, 75),
}

def get_pattern(sector):
    if not sector:
        return DEFAULT_PATTERN
    sector = sector.strip()
    for key in SECTOR_PATTERNS:
        if key.lower() in sector.lower():
            return SECTOR_PATTERNS[key]
    return DEFAULT_PATTERN

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all tickers
    cursor.execute("SELECT ticker, sector FROM stocks")
    rows = cursor.fetchall()

    if not rows:
        print("No stocks found in database!")
        conn.close()
        return

    print(f"Found {len(rows)} stocks. Populating seasonal data...\n")

    updated = 0
    for row in rows:
        ticker = row["ticker"]
        sector = row["sector"] or "Unknown"
        pattern = get_pattern(sector)

        best_month = random.choice(pattern["best_months"])
        worst_month = random.choice(pattern["worst_months"])

        # Best return usually positive, worst usually negative
        best_return = round(random.uniform(4.5, 14.5), 2)
        worst_return = round(random.uniform(-12.0, -2.5), 2)

        seasonal_strength = random.randint(*pattern["strength_range"])

        cursor.execute("""
            UPDATE stocks
            SET best_month = ?,
                best_return = ?,
                worst_month = ?,
                worst_return = ?,
                seasonal_strength = ?
            WHERE ticker = ?
        """, (best_month, best_return, worst_month, worst_return, seasonal_strength, ticker))

        updated += 1
        if updated % 50 == 0:
            print(f"  Updated {updated} stocks...")

    conn.commit()
    conn.close()

    print(f"\n✅ Successfully updated seasonal data for {updated} stocks!")
    print("Now refresh the website → Seasonal section should show data.")

if __name__ == "__main__":
    main()
