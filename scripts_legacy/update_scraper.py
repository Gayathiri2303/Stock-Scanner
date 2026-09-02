import os
import sys

# Read the stock list from stocks_list.py
with open('stocks_list.py', 'r') as f:
    exec(f.read())

# Read the current scraper.py
with open('scraper.py', 'r') as f:
    scraper_content = f.read()

# Replace the US_STOCKS definition with the new one
import re
pattern = r'US_STOCKS = \[.*?\]'
replacement = f'US_STOCKS = {US_STOCKS}'
new_content = re.sub(pattern, replacement, scraper_content, flags=re.DOTALL)

# Write back to scraper.py
with open('scraper.py', 'w') as f:
    f.write(new_content)

print(f"✅ Updated scraper.py with {len(US_STOCKS)} stocks!")
