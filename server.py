#! /usr/bin/python3

import os
import json
import time
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Enable CORS so your browser frontend is allowed to talk to this backend
CORS(app)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portfolio.json')

def load_portfolio_data():
    default_data = {
        'budget': 100000.0,
        'holdings': [],
        'transactions': [],
        'budgetLog': []
    }
    if not os.path.exists(DATA_FILE):
        save_portfolio_data(default_data)
        return default_data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {DATA_FILE}: {e}")
        return default_data

def save_portfolio_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {DATA_FILE}: {e}")

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    return jsonify(load_portfolio_data())

@app.route('/api/portfolio/buy', methods=['POST'])
def portfolio_buy():
    payload = request.get_json() or {}
    symbol = payload.get('symbol')
    ds = payload.get('ds')
    name = payload.get('name')
    sector = payload.get('sector', 'Equity')
    try:
        qty = int(payload.get('qty', 0))
        price = float(payload.get('price', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid numeric quantity or price'}), 400

    if not symbol or qty <= 0 or price <= 0:
        return jsonify({'error': 'Invalid purchase parameters'}), 400

    data = load_portfolio_data()
    total = qty * price
    if total > data.get('budget', 0):
        return jsonify({'error': 'Insufficient funds in wallet'}), 400

    # Deduct from budget
    data['budget'] = round(data.get('budget', 0) - total, 2)

    # Update holdings
    holdings = data.get('holdings', [])
    found = False
    for h in holdings:
        if h.get('symbol') == symbol:
            prev_qty = h.get('qty', 0)
            prev_avg = h.get('avgBuy', 0)
            new_qty = prev_qty + qty
            new_avg = (prev_qty * prev_avg + qty * price) / new_qty
            h['qty'] = new_qty
            h['avgBuy'] = round(new_avg, 2)
            found = True
            break
    if not found:
        holdings.append({
            'symbol': symbol,
            'ds': ds,
            'name': name,
            'sector': sector,
            'qty': qty,
            'avgBuy': round(price, 2)
        })
    data['holdings'] = holdings

    # Add transaction
    txn_id = hex(int(time.time() * 1000))[2:]
    now_iso = datetime.datetime.now().isoformat()
    transactions = data.get('transactions', [])
    transactions.append({
        'id': txn_id,
        'type': 'BUY',
        'symbol': symbol,
        'ds': ds,
        'name': name,
        'qty': qty,
        'price': round(price, 2),
        'total': round(total, 2),
        'date': now_iso
    })
    data['transactions'] = transactions

    # Log budget
    budget_log = data.get('budgetLog', [])
    budget_log.append({
        'type': 'BUY',
        'delta': -round(total, 2),
        'balance': data['budget'],
        'desc': f"Bought {qty}× {ds} @ ₹{price:.2f}",
        'date': now_iso
    })
    data['budgetLog'] = budget_log

    save_portfolio_data(data)
    return jsonify(data)

@app.route('/api/portfolio/sell', methods=['POST'])
def portfolio_sell():
    payload = request.get_json() or {}
    symbol = payload.get('symbol')
    try:
        qty = int(payload.get('qty', 0))
        price = float(payload.get('price', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid numeric quantity or price'}), 400

    if not symbol or qty <= 0 or price <= 0:
        return jsonify({'error': 'Invalid sell parameters'}), 400

    data = load_portfolio_data()
    holdings = data.get('holdings', [])
    holding = next((h for h in holdings if h.get('symbol') == symbol), None)
    if not holding or holding.get('qty', 0) < qty:
        return jsonify({'error': 'Insufficient shares to sell'}), 400

    proceeds = round(qty * price, 2)
    r_pnl = round(qty * (price - holding.get('avgBuy', 0)), 2)
    ds = holding.get('ds', symbol)
    name = holding.get('name', symbol)

    holding['qty'] -= qty
    if holding['qty'] <= 0:
        data['holdings'] = [h for h in holdings if h.get('symbol') != symbol]
    else:
        data['holdings'] = holdings

    data['budget'] = round(data.get('budget', 0) + proceeds, 2)

    txn_id = hex(int(time.time() * 1000))[2:]
    now_iso = datetime.datetime.now().isoformat()

    transactions = data.get('transactions', [])
    transactions.append({
        'id': txn_id,
        'type': 'SELL',
        'symbol': symbol,
        'ds': ds,
        'name': name,
        'qty': qty,
        'price': round(price, 2),
        'total': proceeds,
        'rPnL': r_pnl,
        'date': now_iso
    })
    data['transactions'] = transactions

    budget_log = data.get('budgetLog', [])
    budget_log.append({
        'type': 'SELL',
        'delta': proceeds,
        'balance': data['budget'],
        'desc': f"Sold {qty}× {ds} @ ₹{price:.2f}",
        'date': now_iso
    })
    data['budgetLog'] = budget_log

    save_portfolio_data(data)
    return jsonify(data)

@app.route('/api/portfolio/budget', methods=['POST'])
def portfolio_budget():
    payload = request.get_json() or {}
    action = payload.get('action') # 'topup' or 'set'
    try:
        amount = float(payload.get('amount', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount'}), 400

    data = load_portfolio_data()
    now_iso = datetime.datetime.now().isoformat()
    budget_log = data.get('budgetLog', [])

    if action == 'topup' and amount > 0:
        data['budget'] = round(data.get('budget', 0) + amount, 2)
        budget_log.append({
            'type': 'TOPUP',
            'delta': round(amount, 2),
            'balance': data['budget'],
            'desc': 'Funds added to wallet',
            'date': now_iso
        })
    elif action == 'set' and amount >= 0:
        data['budget'] = round(amount, 2)
        budget_log.append({
            'type': 'SET',
            'delta': round(amount, 2),
            'balance': data['budget'],
            'desc': f"Balance set manually to ₹{amount:,.2f}",
            'date': now_iso
        })
    else:
        return jsonify({'error': 'Invalid budget operation'}), 400

    data['budgetLog'] = budget_log
    save_portfolio_data(data)
    return jsonify(data)

@app.route('/api/portfolio/transactions/clear', methods=['POST'])
def clear_transactions():
    data = load_portfolio_data()
    data['transactions'] = []
    save_portfolio_data(data)
    return jsonify(data)

@app.route('/api/portfolio/sync', methods=['POST'])
def sync_portfolio():
    payload = request.get_json() or {}
    data = load_portfolio_data()
    # If the backend is currently empty, import client data from browser
    if len(data.get('holdings', [])) == 0 and len(payload.get('holdings', [])) > 0:
        data['holdings'] = payload.get('holdings', [])
        data['transactions'] = payload.get('transactions', [])
        data['budget'] = float(payload.get('budget', data.get('budget', 100000.0)))
        data['budgetLog'] = payload.get('budgetLog', [])
        save_portfolio_data(data)
    return jsonify(data)

@app.route('/api/prices', methods=['GET'])
def get_prices():
    symbols = request.args.get('symbols')
    
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400

    y_url = f"https://query1.finance.yahoo.com/v8/finance/spark?symbols={symbols}&range=1d&interval=1d"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        response = requests.get(y_url, headers=headers, timeout=10)
        response.raise_for_status() 
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Fetch Error: {e}")
        return jsonify({'error': 'Failed to fetch data from Yahoo'}), 500

@app.route('/api/chart', methods=['GET'])
def get_chart():
    symbol = request.args.get('symbol')
    range_param = request.args.get('range', '1d')
    
    if not symbol:
        return jsonify({'error': 'No symbol provided'}), 400

    # Configure range and interval for Yahoo Finance chart API
    # 1d -> 1 day with 5m intraday intervals
    # 1w -> 5 trading days with 15m intervals
    # 1y -> 1 year with 1d daily intervals
    range_map = {
        '1d': ('1d', '5m'),
        '1w': ('5d', '15m'),
        '5d': ('5d', '15m'),
        '1y': ('1y', '1d'),
    }
    y_range, y_interval = range_map.get(range_param, ('1d', '5m'))

    y_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={y_range}&interval={y_interval}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        response = requests.get(y_url, headers=headers, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Chart Fetch Error: {e}")
        return jsonify({'error': 'Failed to fetch chart data from Yahoo'}), 500

@app.route('/api/search', methods=['GET'])
def search_symbols():
    query = request.args.get('q')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    y_url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}&lang=en-US&region=IN&quotesCount=10&newsCount=0&enableFuzzyQuery=true"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        response = requests.get(y_url, headers=headers, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Search Error: {e}")
        return jsonify({'error': 'Failed to search Yahoo'}), 500

if __name__ == '__main__':
    print("Starting Python backend on http://localhost:3000")
    app.run(port=3000, debug=True)
