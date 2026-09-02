import schedule
import time
from scraper import scrape_all_stocks
from datetime import datetime

def job():
    print(f"⏰ Running scheduled scrape at {datetime.now()}")
    scrape_all_stocks()

# Schedule every 5 minutes
schedule.every(5).minutes.do(job)

print("🚀 Scheduler started! Scraping every 5 minutes...")

# Run once immediately
scrape_all_stocks()

while True:
    schedule.run_pending()
    time.sleep(1)
