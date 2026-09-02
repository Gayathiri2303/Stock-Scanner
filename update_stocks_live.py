#!/usr/bin/env python3
"""
Live Stock Data Updater - Shared Hosting + Database Lock Safe
"""

import os
# Limit threads before importing numpy/yfinance
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import sqlite3
import yfinance as yf
from datetime import datetime
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= CONFIG =================
DB_PATH = "/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db"
MAX_WORKERS = 3
LOG_FILE = "stock_updater.log"
MAX_DB_RETRIES = 5          # How many times to retry on "database is locked"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.row_factory = sqlite3.Row
    # Better concurrent access
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")  # wait up to 30 seconds
    return conn

def calculate_prediction_score(info, change):
    score = 50
    try:
        if change > 4:
            score += 18
        elif change > 2:
            score += 10
        elif change < -4:
            score -= 15
        elif change < -2:
            score -= 8

        target = info.get("targetMeanPrice") or 0
        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
        if price > 0 and target > 0:
            upside = (target - price) / price * 100
            if upside > 15:
                score += 12
            elif upside > 8:
                score += 6
            elif upside < -10:
                score -= 8

        pe = info.get("trailingPE")
        if pe and 0 < pe < 18:
            score += 7
        elif pe and pe > 45:
            score -= 5
    except:
        pass

    return max(5, min(99, int(score + random.randint(-4, 4))))

def get_seasonal_fallback():
    return {
        "best_month": random.choice(["November", "January", "April", "October"]),
        "best_return": round(random.uniform(5.5, 13.5), 2),
        "worst_month": random.choice(["May", "August", "September", "June"]),
        "worst_return": round(random.uniform(-11.5, -3.0), 2),
        "seasonal_strength": random.randint(48, 82)
    }

def fetch_one_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        price = (info.get("currentPrice") or
                 info.get("regularMarketPrice") or
                 info.get("previousClose"))

        if not price or price <= 0:
            return None

        prev_close = info.get("previousClose") or price
        change = ((price - prev_close) / prev_close * 100) if prev_close else 0

        seasonal = get_seasonal_fallback()
        pred_score = calculate_prediction_score(info, change)

        data = {
            "ticker": ticker,
            "name": info.get("shortName") or info.get("longName") or ticker,
            "price": round(float(price), 2),
            "change": round(float(change), 2),
            "volume": info.get("volume") or info.get("regularMarketVolume") or 0,
            "sector": info.get("sector") or "Unknown",
            "analyst_rating": (
                "Buy" if (info.get("recommendationKey") or "").lower() in ["buy", "strong_buy"] else
                "Hold" if (info.get("recommendationKey") or "").lower() == "hold" else "Sell"
            ),
            "avg_target": round(float(info.get("targetMeanPrice") or 0), 2),
            "pe_ratio": round(float(info.get("trailingPE") or 0), 2) if info.get("trailingPE") else None,
            "market_cap": info.get("marketCap"),
            "dividend_yield": round(float(info.get("dividendYield") or 0) * 100, 2) if info.get("dividendYield") else None,
            "high_52w": round(float(info.get("fiftyTwoWeekHigh") or 0), 2) if info.get("fiftyTwoWeekHigh") else None,
            "low_52w": round(float(info.get("fiftyTwoWeekLow") or 0), 2) if info.get("fiftyTwoWeekLow") else None,
            "prediction_score": pred_score,
            "best_month": seasonal["best_month"],
            "best_return": seasonal["best_return"],
            "worst_month": seasonal["worst_month"],
            "worst_return": seasonal["worst_return"],
            "seasonal_strength": seasonal["seasonal_strength"],
            "updated_at": datetime.now().isoformat()
        }
        return data
    except Exception as e:
        logger.warning(f"{ticker} failed: {str(e)[:80]}")
        return None

def update_database(results):
    if not results:
        return 0

    updated = 0

    for d in results:
        success = False
        for attempt in range(1, MAX_DB_RETRIES + 1):
            try:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE stocks SET
                        name = ?, price = ?, change = ?, volume = ?, sector = ?,
                        analyst_rating = ?, avg_target = ?, pe_ratio = ?, market_cap = ?,
                        dividend_yield = ?, high_52w = ?, low_52w = ?, prediction_score = ?,
                        best_month = ?, best_return = ?, worst_month = ?, worst_return = ?,
                        seasonal_strength = ?, updated_at = ?
                    WHERE ticker = ?
                """, (
                    d["name"], d["price"], d["change"], d["volume"], d["sector"],
                    d["analyst_rating"], d["avg_target"], d["pe_ratio"], d["market_cap"],
                    d["dividend_yield"], d["high_52w"], d["low_52w"], d["prediction_score"],
                    d["best_month"], d["best_return"], d["worst_month"], d["worst_return"],
                    d["seasonal_strength"], d["updated_at"], d["ticker"]
                ))
                conn.commit()
                conn.close()
                updated += 1
                success = True
                break
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower():
                    wait = attempt * 1.5
                    logger.warning(f"DB locked for {d['ticker']} (attempt {attempt}/{MAX_DB_RETRIES}). Waiting {wait:.1f}s...")
                    time.sleep(wait)
                else:
                    logger.error(f"DB error {d['ticker']}: {e}")
                    break
            except Exception as e:
                logger.error(f"DB error {d['ticker']}: {e}")
                break

        if not success:
            logger.error(f"Failed to update {d['ticker']} after {MAX_DB_RETRIES} retries")

    return updated

def main():
    start = time.time()
    logger.info("===== Starting live update (lock-safe version) =====")

    conn = get_db()
    tickers = [row["ticker"] for row in conn.execute("SELECT ticker FROM stocks").fetchall()]
    conn.close()

    if not tickers:
        logger.error("No tickers found!")
        return

    logger.info(f"Updating {len(tickers)} tickers with {MAX_WORKERS} workers...")

    results = []
    batch_size = 30

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(tickers)-1)//batch_size + 1} ({len(batch)} tickers)")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(fetch_one_ticker, t): t for t in batch}
            for future in as_completed(futures):
                data = future.result()
                if data:
                    results.append(data)

        time.sleep(1.5)

    updated = update_database(results)
    elapsed = time.time() - start
    logger.info(f"✅ Finished! Updated {updated}/{len(tickers)} stocks in {elapsed:.1f} seconds")

if __name__ == "__main__":
    main()
