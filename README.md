# Stock Scanner

Flask + SQLite stock scanner deployed on cPanel (Passenger WSGI).

## Structure
- `app.py` — Flask backend, serves the API and the frontend
- `static/index.html` — frontend dashboard
- `update_stocks_live.py` — pulls live prices via yfinance, run on a schedule
- `run_live_update.sh` — shell wrapper used by the cPanel cron job to run the updater
- `passenger_wsgi.py`, `.htaccess` — cPanel/Passenger deployment config
- `requirements.txt` — Python dependencies
- `scripts_legacy/` — one-off data-fix, migration, and scraping scripts used during development. Not part of the live app; kept for reference.

## Not included
- `stocks.db` (runtime database — regenerate via the updater scripts, don't commit data)
- logs, `.bak` files, `__pycache__`

## Known issue to fix before making this repo public
`app.py` has a hardcoded admin login (`admin` / `password123`) in the `/api/login` route. Replace this with a real auth check or environment-variable-based credential before sharing the code publicly.
