# Stockfolio — India Portfolio Tracker & Financial Literacy Platform

**Stockfolio** is a lightweight, local client-server web application designed to track Indian equity portfolios (NSE/BSE), simulate paper trading, and educate beginners on stock market investing and technical analysis.

It combines an all-in-one React 18 single-page frontend with a local Python Flask backend that fetches real-time market data directly from Yahoo Finance without requiring paid API subscriptions or complex build tools.

---

## Key Features

* **⚡ Real-Time NSE Market Feed**: Live price streaming and continuous ticker updates for Indian stocks (e.g., Reliance, TCS, HDFC Bank, Infosys).
* **💾 Backend Portfolio Persistence**: Trades, cash balances, and transaction logs are stored permanently on disk in `portfolio.json` (with automatic browser `localStorage` offline backup).
* **📊 Interactive Multi-Timeframe Charts**: Native SVG price charts with hover crosshairs, period statistics, and timeframe switching:
  * **1 Day (`1d`)** — 5-minute interval candles
  * **1 Week (`1w`)** — 15-minute interval candles
  * **1 Year (`1y`)** — Daily candles
* **📈 Technical Indicators Engine**:
  * **50-Day & 200-Day SMA**: Rolling trend averages overlaid on 1-Year charts.
  * **Golden Cross & Death Cross**: Automated detection and tagging of major bullish and bearish momentum breakouts.
  * **Relative Strength Index (RSI - 14D)**: Wilder's smoothed momentum oscillator identifying overbought ($>70$) and oversold ($<30$) conditions.
* **📘 Stockfolio Academy ("Learn" Tab)**: A dedicated educational view explaining technical indicators, market psychology, and beginner investing rules with simple real-world analogies.
* **🎯 Smart Order Execution**: Selecting any stock in the **Buy** modal automatically fetches and fills its current market price (LTP) while keeping the price field fully editable.
* **💼 Wallet & Budget Management**: Deposit virtual funds, manually set balances, and inspect complete audit ledgers of deposits, purchases, and sales.

---

## Project Structure

```
stockfolio/
├── stockfolio.html    # Frontend SPA (React 18, Babel, SVG Charts, Learn View)
├── server.py          # Backend REST API (Flask, Yahoo Finance Proxy, JSON Storage)
├── portfolio.json     # Persistent database for cash, holdings, and trade history
├── ARCHITECTURE.md    # In-depth technical architecture and system blueprint
└── README.md          # Quickstart guide and project overview
```

---

## Prerequisites

* **Python 3.8+** (Download from [python.org](https://www.python.org/downloads/))
* A modern web browser (Google Chrome, Mozilla Firefox, Microsoft Edge, Brave, or Safari)

---

## Installation & Setup

### Step 1: Install Backend Dependencies

The Python server requires three lightweight packages:
```bash
pip install flask flask-cors requests
```

### Step 2: Start the Backend Server

The backend serves as a CORS-compliant bridge to Yahoo Finance and manages disk persistence for your portfolio:
```bash
python3 server.py
```
You will see confirmation that the server is active on `http://localhost:3000`. Keep this terminal window open in the background.

### Step 3: Open the Application

Because the React application compiles in-browser via Babel standalone, no build step or web server is required for the frontend.

Simply double-click [`stockfolio.html`](file:///home/aryan/src/stockfolio/stockfolio.html) or open it directly in your browser.

---

## How It Works (Architecture Overview)

```
┌────────────────────────────────┐         ┌─────────────────────────────────┐
│   stockfolio.html (Browser)    │ ◄─────► │     server.py (Port 3000)       │
│  - React 18 UI & State         │  REST   │  - Flask CORS Proxy Bridge      │
│  - SVG Charting Engine         │  JSON   │  - /api/prices, /api/chart      │
│  - Technical Indicator Math    │         │  - Portfolio CRUD & Storage     │
└────────────────────────────────┘         └───────┬─────────────────┬───────┘
                                                   │                 │
                                                   ▼                 ▼
                                    ┌──────────────────────┐ ┌──────────────┐
                                    │ Yahoo Finance Cloud  │ │portfolio.json│
                                    │ (v8 Chart & Search)  │ │(Local Disk)  │
                                    └──────────────────────┘ └──────────────┘
```

1. **CORS Bypassing**: Web browsers restrict client-side scripts from querying external APIs like Yahoo Finance. `server.py` acts as a secure local proxy, fetching quotes on behalf of the browser without CORS restrictions.
2. **Persistent Storage**: All buy/sell orders, top-ups, and balance adjustments are dispatched to `/api/portfolio/*` endpoints and committed to [`portfolio.json`](file:///home/aryan/src/stockfolio/portfolio.json) on disk.
3. **Indicator Calculation**: Historical price points retrieved via `/api/chart` are processed client-side using rolling window vector math for moving averages and RSI.

For a deeper dive, read the full [`ARCHITECTURE.md`](file:///home/aryan/src/stockfolio/ARCHITECTURE.md).

---

## Troubleshooting

* **Page displays "Loading Stockfolio…":**
  Ensure you are opening [`stockfolio.html`](file:///home/aryan/src/stockfolio/stockfolio.html) in a modern browser with JavaScript enabled. Check the browser console (`F12` $\to$ Console) if any extensions are blocking scripts.
* **Ticker shows "ERR" or prices won't load:**
  Verify that `server.py` is actively running on `http://localhost:3000`. If closed, restart it in your terminal (`python3 server.py`).
* **Port 3000 in use:**
  If another process is using port 3000, modify `port=3000` at the bottom of [`server.py`](file:///home/aryan/src/stockfolio/server.py) and update the corresponding `localhost:3000` URLs in [`stockfolio.html`](file:///home/aryan/src/stockfolio/stockfolio.html).
