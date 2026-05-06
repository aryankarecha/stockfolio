#! /usr/bin/python3

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# Enable CORS so your browser frontend is allowed to talk to this backend
CORS(app)

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
