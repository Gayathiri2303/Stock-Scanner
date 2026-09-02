with open('app.py', 'r') as f:
    code = f.read()

old = '''@app.route('/api/investment')
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
        return jsonify({"error": "No stocks available"})'''

new = '''@app.route('/api/investment')
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
        return jsonify({"error": "No stocks available"})'''

if old in code:
    code = code.replace(old, new)
    with open('app.py', 'w') as f:
        f.write(code)
    print("✅ Patched successfully")
else:
    print("❌ Still no match — need to see exact bytes")
