import sqlite3
from datetime import datetime

DB_PATH = '/home2/thekidsw/gayathiriportfolio.xyz/stockscanner/stocks.db'

def get_top_stocks(limit=5):
    """Get top performing stocks"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        stocks = c.execute('''
            SELECT * FROM stocks 
            ORDER BY prediction_score DESC 
            LIMIT ?
        ''', (limit,)).fetchall()
        
        conn.close()
        return [dict(row) for row in stocks]
    except Exception as e:
        print(f"Error getting top stocks: {e}")
        return []

def calculate_investment(amount_inr=10000):
    """Calculate investment details for ₹10,000"""
    try:
        # Get top stock
        top_stocks = get_top_stocks(1)
        if not top_stocks:
            return {"error": "No stock data available"}
        
        stock = top_stocks[0]
        
        # USD/INR rate
        usd_inr = stock.get('usd_inr', 83.5)
        if usd_inr == 0 or usd_inr is None:
            usd_inr = 83.5  # Default fallback
        
        # Calculate
        usd_amount = amount_inr / usd_inr
        tcs_rate = 0.05  # 5% TCS on LRS remittance
        tcs_amount = amount_inr * tcs_rate
        final_inr_amount = amount_inr - tcs_amount
        final_usd_amount = final_inr_amount / usd_inr
        
        # Withdrawal rules
        settlement_days = 2  # T+2 settlement
        withdrawal_info = f"{settlement_days} business days after selling"
        
        return {
            'investment_date': datetime.now().isoformat(),
            'amount_inr': amount_inr,
            'usd_inr_rate': round(usd_inr, 2),
            'usd_amount': round(usd_amount, 2),
            'tcs_percent': tcs_rate * 100,
            'tcs_amount': round(tcs_amount, 2),
            'final_usd_amount': round(final_usd_amount, 2),
            'recommended_stock': stock.get('ticker', 'N/A'),
            'stock_price_usd': stock.get('price', 0),
            'shares_estimate': round(final_usd_amount / stock['price'], 2) if stock.get('price', 0) > 0 else 0,
            'withdrawal_time': withdrawal_info,
            'settlement_days': settlement_days,
            'analyst_rating': stock.get('analyst_rating', 'Hold'),
            'avg_target': stock.get('avg_target', 0),
            'total_return_estimate': f"Based on {stock.get('analyst_rating', 'Hold')} rating"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    result = calculate_investment(10000)
    print("=" * 60)
    print("📊 INVESTMENT RECOMMENDATION")
    print("=" * 60)
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Amount: ₹{result['amount_inr']}")
        print(f"USD/INR: {result['usd_inr_rate']}")
        print(f"USD Amount: ${result['usd_amount']}")
        print(f"TCS (5%): ₹{result['tcs_amount']}")
        print(f"Final USD: ${result['final_usd_amount']}")
        print(f"Recommended Stock: {result['recommended_stock']}")
        print(f"Stock Price: ${result['stock_price_usd']}")
        print(f"Shares: {result['shares_estimate']}")
        print(f"Withdrawal: {result['withdrawal_time']}")
    print("=" * 60)
