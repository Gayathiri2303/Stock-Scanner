import re

# ---------- app.py ----------
with open('app.py', 'r') as f:
    app_code = f.read()

# 1. Make sure requests is imported
if 'import requests' not in app_code:
    app_code = app_code.replace(
        "from flask import Flask, jsonify, request, send_from_directory",
        "from flask import Flask, jsonify, request, send_from_directory\nimport requests"
    )

# 2. Add a live USD/INR helper (once, right after DB_PATH line)
if 'def get_live_usd_inr' not in app_code:
    app_code = app_code.replace(
        "def get_db_connection():",
        '''def get_live_usd_inr():
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        data = r.json()
        return round(data['rates']['INR'], 2)
    except Exception:
        return 83.5

def get_db_connection():'''
    )

# 3. Replace /api/predictions with smarter ranking
old_predictions = '''@app.route('/api/predictions')
def get_predictions():
    try:
        conn = get_db_connection()
        stocks = conn.execute(\'\'\'
            SELECT ticker, name, price, change, sector, analyst_rating, avg_target, prediction_score
            FROM stocks
            ORDER BY prediction_score DESC
            LIMIT 3
        \'\'\').fetchall()
        conn.close()
        return jsonify({"top_picks": [dict(row) for row in stocks]})
    except Exception as e:
        return jsonify({"error": str(e), "top_picks": []}), 500'''

new_predictions = '''@app.route('/api/predictions')
def get_predictions():
    try:
        conn = get_db_connection()
        stocks = conn.execute(\'\'\'
            SELECT ticker, name, price, change, sector, analyst_rating, avg_target, prediction_score
            FROM stocks
            WHERE price > 0
            ORDER BY
                prediction_score DESC,
                CASE analyst_rating
                    WHEN 'Buy' THEN 1
                    WHEN 'Overweight' THEN 2
                    WHEN 'Hold' THEN 3
                    WHEN 'Underweight' THEN 4
                    WHEN 'Sell' THEN 5
                    ELSE 6
                END ASC,
                change DESC
            LIMIT 3
        \'\'\').fetchall()
        conn.close()
        return jsonify({"top_picks": [dict(row) for row in stocks]})
    except Exception as e:
        return jsonify({"error": str(e), "top_picks": []}), 500'''

if old_predictions in app_code:
    app_code = app_code.replace(old_predictions, new_predictions)
    print("✅ /api/predictions upgraded")
else:
    print("⚠️  /api/predictions block not matched — skipped (check manually)")

# 4. Replace /api/investment with smarter pick + live FX rate
old_investment = '''@app.route('/api/investment')
def get_investment():
    try:
        conn = get_db_connection()
        top = conn.execute(\'\'\'
            SELECT ticker, price, avg_target, prediction_score
            FROM stocks
            ORDER BY prediction_score DESC
            LIMIT 1
        \'\'\').fetchone()
        conn.close()
        if top:
            usd_inr = 83.5
            amount_inr = 10000
            usd_amount = amount_inr / usd_inr
            tcs = amount_inr * 0.05
            final_usd = usd_amount - (tcs / usd_inr)
            shares = round(final_usd / top['price'], 2) if top['price'] > 0 else 0
            return jsonify({
                "recommended_stock": top['ticker'],
                "usd_inr_rate": usd_inr,
                "usd_amount": round(usd_amount, 2),
                "tcs_amount": round(tcs, 2),
                "final_usd": round(final_usd, 2),
                "shares_estimate": shares,
                "withdrawal_time": "2 business days after selling",
                "stock_price": top['price']
            })
        return jsonify({"error": "No stocks available"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500'''

new_investment = '''@app.route('/api/investment')
def get_investment():
    try:
        conn = get_db_connection()
        top = conn.execute(\'\'\'
            SELECT ticker, price, avg_target, prediction_score, analyst_rating
            FROM stocks
            WHERE price > 0 AND price < 500 AND prediction_score >= 55
            ORDER BY
                CASE analyst_rating
                    WHEN 'Buy' THEN 1
                    WHEN 'Overweight' THEN 2
                    ELSE 3
                END ASC,
                prediction_score DESC
            LIMIT 1
        \'\'\').fetchone()
        if not top:
            top = conn.execute(\'\'\'
                SELECT ticker, price, avg_target, prediction_score, analyst_rating
                FROM stocks WHERE price > 0
                ORDER BY prediction_score DESC LIMIT 1
            \'\'\').fetchone()
        conn.close()
        if top:
            usd_inr = get_live_usd_inr()
            amount_inr = 10000
            tcs = amount_inr * 0.05
            net_inr = amount_inr - tcs
            final_usd = round(net_inr / usd_inr, 2)
            shares = round(final_usd / top['price'], 4) if top['price'] > 0 else 0
            upside = None
            if top['avg_target'] and top['price']:
                upside = round((top['avg_target'] - top['price']) / top['price'] * 100, 2)
            return jsonify({
                "recommended_stock": top['ticker'],
                "analyst_rating": top['analyst_rating'],
                "prediction_score": top['prediction_score'],
                "usd_inr_rate": usd_inr,
                "usd_amount": final_usd,
                "tcs_amount": round(tcs, 2),
                "final_usd": final_usd,
                "shares_estimate": shares,
                "target_upside_pct": upside,
                "withdrawal_time": "2 business days after selling",
                "stock_price": top['price']
            })
        return jsonify({"error": "No stocks available"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500'''

if old_investment in app_code:
    app_code = app_code.replace(old_investment, new_investment)
    print("✅ /api/investment upgraded")
else:
    print("⚠️  /api/investment block not matched — skipped (check manually)")

# 5. Add /api/last-updated route (once), right before the login route
if '/api/last-updated' not in app_code:
    app_code = app_code.replace(
        "@app.route('/api/login', methods=['POST'])",
        '''@app.route('/api/last-updated')
def get_last_updated():
    try:
        conn = get_db_connection()
        row = conn.execute('SELECT MAX(updated_at) as last FROM stocks').fetchone()
        conn.close()
        return jsonify({"last_updated": row['last'] if row else None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])'''
    )
    print("✅ /api/last-updated added")

with open('app.py', 'w') as f:
    f.write(app_code)

# ---------- static/index.html ----------
with open('static/index.html', 'r') as f:
    html_code = f.read()

old_js = '''    function updateLastUpdated() {
        const now = new Date();
        document.getElementById('lastUpdated').textContent = `Last updated: ${now.toLocaleString()}`;
    }'''

new_js = '''    async function updateLastUpdated() {
        try {
            const r = await fetch(`${API_BASE}/last-updated`);
            const d = await r.json();
            if (d.last_updated) {
                const dt = new Date(d.last_updated);
                document.getElementById('lastUpdated').textContent = `Last updated: ${dt.toLocaleString()}`;
            } else {
                document.getElementById('lastUpdated').textContent = `Last updated: N/A`;
            }
        } catch(e) {
            document.getElementById('lastUpdated').textContent = `Last updated: Error`;
        }
    }'''

if old_js in html_code:
    html_code = html_code.replace(old_js, new_js)
    print("✅ updateLastUpdated() upgraded to use real DB time")
else:
    print("⚠️  updateLastUpdated() block not matched — skipped (check manually)")

with open('static/index.html', 'w') as f:
    f.write(html_code)

print("\\nDone. Restart the app to apply changes.")
