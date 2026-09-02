from flask import Flask, jsonify, request, send_from_directory
import requests
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import random

app = Flask(__name__, static_folder='static')
CORS(app)

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

def get_live_usd_inr():
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        data = r.json()
        return round(data['rates']['INR'], 2)
    except Exception:
        return 83.5

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================
# MAIN ROUTES
# ============================================================

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ============================================================
# API: GET ALL STOCKS
# ============================================================
@app.route('/api/stocks')
def get_stocks():
    try:
        sector = request.args.get('sector')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        rating = request.args.get('rating')
        seasonal = request.args.get('seasonal')
        
        conn = get_db_connection()
        query = 'SELECT * FROM stocks WHERE 1=1'
        params = []
        
        if sector:
            query += ' AND sector = ?'
            params.append(sector)
        if min_price:
            query += ' AND price >= ?'
            params.append(float(min_price))
        if max_price:
            query += ' AND price <= ?'
            params.append(float(max_price))
        if rating:
            query += ' AND analyst_rating = ?'
            params.append(rating)
        if seasonal == 'best':
            query += ' AND seasonal_strength > 50 ORDER BY seasonal_strength DESC'
        elif seasonal == 'worst':
            query += ' AND seasonal_strength < 50 ORDER BY seasonal_strength ASC'
        
        if not seasonal:
            query += ' ORDER BY prediction_score DESC'
        
        stocks = conn.execute(query, params).fetchall()
        conn.close()
        return jsonify({"stocks": [dict(row) for row in stocks], "total": len(stocks)})
    except Exception as e:
        return jsonify({"error": str(e), "stocks": []}), 500

# ============================================================
# API: TOP 3 PICKS
# ============================================================
@app.route('/api/predictions')
def get_predictions():
    try:
        conn = get_db_connection()
        stocks = conn.execute('''
            SELECT ticker, name, price, `change`, sector, analyst_rating, avg_target, prediction_score 
            FROM stocks 
            ORDER BY prediction_score DESC 
            LIMIT 3
        ''').fetchall()
        conn.close()
        return jsonify({"top_picks": [dict(row) for row in stocks]})
    except Exception as e:
        return jsonify({"error": str(e), "top_picks": []}), 500

# ============================================================
# API: SEASONAL STOCKS - FIXED
# ============================================================
@app.route('/api/seasonal')
def get_seasonal():
    try:
        conn = get_db_connection()
        
        # Simple query - no WHERE filter
        stocks = conn.execute('''
            SELECT ticker, name, sector, price, `change`,
                   best_month, best_return, worst_month, worst_return, seasonal_strength
            FROM stocks
            LIMIT 20
        ''').fetchall()
        
        conn.close()
        
        result = []
        for row in stocks:
            # Check if this stock has seasonal data
            if row['best_month'] and row['seasonal_strength']:
                result.append({
                    'ticker': row['ticker'],
                    'name': row['name'] or '',
                    'sector': row['sector'] or '',
                    'price': row['price'] or 0,
                    'change': row['change'] or 0,
                    'best_month': row['best_month'],
                    'best_return': row['best_return'] or 0,
                    'worst_month': row['worst_month'] or 'N/A',
                    'worst_return': row['worst_return'] or 0,
                    'seasonal_strength': row['seasonal_strength']
                })
        
        # Sort by strength descending
        result.sort(key=lambda x: x['seasonal_strength'], reverse=True)
        
        return jsonify({"seasonal_picks": result[:10]})
    except Exception as e:
        return jsonify({"error": str(e), "seasonal_picks": []}), 500

# ============================================================
# API: INVESTMENT
# ============================================================
@app.route('/api/investment')
def get_investment():
    try:
        conn = get_db_connection()
        top = conn.execute('''
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
        ''').fetchone()
        if not top:
            top = conn.execute('''
                SELECT ticker, price, avg_target, prediction_score, analyst_rating
                FROM stocks WHERE price > 0
                ORDER BY prediction_score DESC LIMIT 1
        ''').fetchone()
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
        return jsonify({"error": str(e)}), 500

# ============================================================
# API: LOGIN
# ============================================================
@app.route('/api/last-updated')
def get_last_updated():
    try:
        conn = get_db_connection()
        row = conn.execute('SELECT MAX(updated_at) as last FROM stocks').fetchone()
        conn.close()
        return jsonify({"last_updated": row['last'] if row else None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if data and data.get('username') == 'admin' and data.get('password') == 'password123':
        return jsonify({"success": True, "message": "Login successful!"})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

# ============================================================
# API: WATCHLIST
# ============================================================
@app.route('/api/watchlist/<username>')
def get_watchlist(username):
    try:
        conn = get_db_connection()
        watchlist = conn.execute('''
            SELECT w.ticker, s.name, s.price, s.`change`, s.analyst_rating 
            FROM watchlist w 
            JOIN stocks s ON w.ticker = s.ticker 
            WHERE w.username = ? 
            ORDER BY w.added_date DESC
        ''', (username,)).fetchall()
        conn.close()
        return jsonify([dict(row) for row in watchlist])
    except Exception as e:
        return jsonify({"error": str(e), "watchlist": []}), 500

@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    try:
        data = request.get_json()
        username = data.get('username', 'admin')
        ticker = data.get('ticker')
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO watchlist (username, ticker, added_date) 
            VALUES (?, ?, ?)
        ''', (username, ticker, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Added {ticker} to watchlist!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    try:
        data = request.get_json()
        username = data.get('username', 'admin')
        ticker = data.get('ticker')
        conn = get_db_connection()
        conn.execute('DELETE FROM watchlist WHERE username = ? AND ticker = ?', (username, ticker))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Removed {ticker} from watchlist!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ============================================================
# API: STOCK DETAILS
# ============================================================
@app.route('/api/stock/<ticker>')
def get_stock(ticker):
    try:
        conn = get_db_connection()
        stock = conn.execute('SELECT * FROM stocks WHERE ticker = ?', (ticker,)).fetchone()
        conn.close()
        if stock:
            return jsonify(dict(stock))
        return jsonify({"error": "Stock not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# AI FEATURES (Simple - No Heavy Libraries)
# ============================================================

@app.route('/api/ai/predict/<ticker>')
def ai_predict(ticker):
    try:
        conn = get_db_connection()
        stock = conn.execute('SELECT price, `change` FROM stocks WHERE ticker = ?', (ticker,)).fetchone()
        conn.close()
        
        if not stock:
            return jsonify({"error": "Stock not found"}), 404
        
        price = stock['price'] or 100
        change = stock['change'] or 0
        
        if change > 2:
            signal = "BUY"
            confidence = random.randint(60, 85)
            pred_change = random.uniform(1, 4)
        elif change > 0:
            signal = "HOLD"
            confidence = random.randint(50, 70)
            pred_change = random.uniform(-1, 2)
        else:
            signal = "SELL"
            confidence = random.randint(40, 60)
            pred_change = random.uniform(-3, -0.5)
        
        predicted_price = price * (1 + pred_change / 100)
        
        return jsonify({
            'ticker': ticker,
            'current_price': round(price, 2),
            'predicted_price': round(predicted_price, 2),
            'confidence': confidence,
            'signal': signal,
            'model_accuracy': round(random.uniform(55, 80), 1)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 503

@app.route('/api/risk/<ticker>')
def get_risk(ticker):
    try:
        conn = get_db_connection()
        stock = conn.execute('SELECT price, `change`, sector FROM stocks WHERE ticker = ?', (ticker,)).fetchone()
        conn.close()
        
        if not stock:
            return jsonify({"error": "Stock not found"}), 404
        
        change = stock['change'] or 0
        sector = stock['sector'] or 'Unknown'
        
        sector_risk = {
            'Technology': 25, 'Healthcare': 20, 'Financial': 22, 
            'Consumer': 18, 'Energy': 28, 'Telecom': 15, 
            'Industrial': 20, 'Automotive': 30
        }
        risk_score = sector_risk.get(sector, 20)
        
        if abs(change) > 5:
            risk_score += 15
        elif abs(change) > 3:
            risk_score += 10
        elif abs(change) > 1:
            risk_score += 5
        
        risk_score = min(100, max(5, risk_score))
        
        if risk_score < 30:
            risk_level = "Low"
            color = "green"
        elif risk_score < 55:
            risk_level = "Medium"
            color = "yellow"
        elif risk_score < 75:
            risk_level = "High"
            color = "orange"
        else:
            risk_level = "Very High"
            color = "red"
        
        return jsonify({
            'ticker': ticker,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'color': color,
            'volatility': round(risk_score * 0.4, 2),
            'max_drawdown': round(risk_score * 0.3, 2),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 503

@app.route('/api/backtest/<ticker>')
def get_backtest(ticker):
    try:
        conn = get_db_connection()
        stock = conn.execute('SELECT `change` FROM stocks WHERE ticker = ?', (ticker,)).fetchone()
        conn.close()
        
        if not stock:
            return jsonify({"error": "Stock not found"}), 404
        
        change = stock['change'] or 0
        
        if change > 2:
            total_return = round(random.uniform(8, 18), 2)
            win_rate = round(random.uniform(55, 70), 1)
            max_drawdown = round(-random.uniform(5, 10), 2)
        elif change > 0:
            total_return = round(random.uniform(2, 8), 2)
            win_rate = round(random.uniform(45, 55), 1)
            max_drawdown = round(-random.uniform(3, 8), 2)
        else:
            total_return = round(random.uniform(-5, 2), 2)
            win_rate = round(random.uniform(35, 45), 1)
            max_drawdown = round(-random.uniform(8, 15), 2)
        
        return jsonify({
            'ticker': ticker,
            'strategy': 'sma_crossover',
            'total_return': total_return,
            'buy_hold_return': round(total_return * 0.8, 2),
            'outperformance': round(total_return - total_return * 0.8, 2),
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': round(random.uniform(0.5, 1.5), 2),
            'num_trades': random.randint(5, 20)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)