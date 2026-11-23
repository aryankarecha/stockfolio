# Stockfolio — System Architecture & Working Guide

This document provides a comprehensive explanation of how **Stockfolio** is structured, how its frontend and backend components interact, and how data flows through the application from external market APIs to the user interface.

---

## 1. High-Level System Architecture

Stockfolio is designed as a **lightweight, local client-server web application** optimized for simplicity and zero-configuration setup.

```
┌────────────────────────────────────────────────────────┐
│                   Web Browser                          │
│                                                        │
│   stockfolio.html (Single Page Application)            │
│   ├── React 18 (Component UI & State)                 │
│   ├── Babel Standalone (In-Browser JSX Transpilation)  │
│   ├── In-Memory & LocalStorage Offline Cache           │
│   └── SVG Interactive Chart & Indicators Engine        │
└──────────────▲───────────────────────────┬─────────────┘
               │ JSON Responses            │ REST Requests
               │ (Port 3000)               │ (GET / POST)
┌──────────────┴───────────────────────────▼─────────────┐
│             Python Backend (server.py)                 │
│                                                        │
│   Flask REST API + Flask-CORS                          │
│   ├── /api/prices?symbols=...    (Market Quote Proxy)  │
│   ├── /api/chart?symbol=...      (Historical Quotes)   │
│   ├── /api/search?q=...          (NSE/BSE Search)      │
│   └── /api/portfolio/*           (Persistence Engine)  │
└──────────────▲───────────────────────────┬─────────────┘
               │ Yahoo Finance Data        │ Local Disk
               │ (JSON via HTTPS)          │ (Read / Write)
┌──────────────┴──────────────┐     ┌──────▼─────────────┐
│  Yahoo Finance Cloud APIs   │     │   portfolio.json   │
│  - query1.finance.yahoo.com │     │  (Persistent Store │
│  - /v8/finance/chart        │     │   on Backend Disk) │
│  - /v1/finance/search       │     └────────────────────┘
└─────────────────────────────┘
```

### Why This Architecture?
1. **Bypassing Browser CORS**: Modern web browsers enforce Cross-Origin Resource Sharing (CORS), blocking client-side JavaScript from fetching market data directly from Yahoo Finance. The local Python Flask backend acts as a server-side bridge that queries Yahoo without CORS restrictions.
2. **True Persistence**: Early versions saved trades strictly in browser `localStorage`. Shifting portfolio persistence to a backend JSON database (`portfolio.json`) ensures your portfolio, transactions, and cash ledger remain permanent across different browsers, private windows, or system restarts.
3. **No Build Step Required**: The frontend runs directly in any modern browser without needing Node.js, Webpack, or npm.

---

## 2. Directory Structure & Files

| File / Folder | Role | Description |
| :--- | :--- | :--- |
| [`stockfolio.html`](file:///home/aryan/src/stockfolio/stockfolio.html) | **Frontend** | Complete single-page React application containing styling, components, chart drawing, indicator calculations, and client-side logic. |
| [`server.py`](file:///home/aryan/src/stockfolio/server.py) | **Backend** | Python Flask server running on `http://localhost:3000`. Handles API calls to Yahoo Finance and manages disk read/write for `portfolio.json`. |
| [`portfolio.json`](file:///home/aryan/src/stockfolio/portfolio.json) | **Database** | Persistent JSON ledger holding your cash balance, owned stock holdings, trade history, and transaction logs. |
| [`README.md`](file:///home/aryan/src/stockfolio/README.md) | **Setup Guide** | Quickstart instructions and basic troubleshooting tips. |

---

## 3. Backend Architecture (`server.py`)

The backend is built with Python 3 and Flask. It exposes clean REST endpoints consumed by the React UI.

### 3.1 Endpoints Overview

#### 1. Price Quotes (`GET /api/prices?symbols=...`)
* **Purpose**: Fetches real-time / current market quotes for one or more stock tickers.
* **Mechanism**: Calls Yahoo Finance's `v8/finance/chart/{symbol}` endpoint for each requested symbol.
* **Returns**: A JSON map containing the Last Traded Price (LTP), price change, and percentage change:
  ```json
  {
    "RELIANCE.NS": { "price": 2980.50, "change": 14.20, "pct": 0.48 },
    "TCS.NS": { "price": 4120.10, "change": -10.50, "pct": -0.25 }
  }
  ```

#### 2. Historical Chart Data (`GET /api/chart?symbol=...&range=...`)
* **Purpose**: Fetches historical candle data for charting and technical indicator computation.
* **Supported Ranges**:
  * `1d` (1 Day) — 5-minute interval candles
  * `1w` (1 Week) — 15-minute interval candles
  * `1y` (1 Year) — 1-day interval candles
* **Mechanism**: Queries Yahoo Finance's `v8/finance/chart/{symbol}?range={range}&interval={interval}` and forwards timestamps, close prices, and metadata to the client.

#### 3. Stock Search (`GET /api/search?q=...`)
* **Purpose**: Enables the search modal in the UI to discover Indian stocks by company name or ticker.
* **Mechanism**: Queries Yahoo Finance's `v1/finance/search` API and filters results specifically to Indian exchanges (tickers ending in `.NS` for NSE and `.BO` for BSE).

#### 4. Portfolio Persistence Engine (`/api/portfolio/*`)
* `GET /api/portfolio`: Reads and returns `portfolio.json` (budget, holdings, transactions, budgetLog).
* `POST /api/portfolio/buy`: Validates wallet balance, deducts purchase cost, updates or creates holding, appends to transaction history, logs to budget ledger, and saves to disk.
* `POST /api/portfolio/sell`: Validates share quantity, credits sale proceeds to wallet, calculates realized profit/loss, updates or removes holding, logs transaction, and saves to disk.
* `POST /api/portfolio/budget`: Handles manual balance overrides (`set`) and wallet deposits (`topup`).
* `POST /api/portfolio/transactions/clear`: Clears past transaction history without deleting owned holdings.
* `POST /api/portfolio/sync`: Automatically migrates existing browser `localStorage` data into `portfolio.json` on initial boot if backend storage is fresh.

---

## 4. Frontend Architecture (`stockfolio.html`)

The frontend is an all-in-one single-page application (SPA) powered by **React 18** and **Babel Standalone**.

### 4.1 UI Component Tree

```
App (Root State, Data Fetching, Router)
├── TickerBar (Continuous scrolling marquee of top NSE stocks)
├── NavBar (Tab navigation, live wallet balance pill, refresh trigger)
│
├── Views (Rendered conditionally based on active tab)
│   ├── Dashboard (NAV overview, total invested, P&L cards, top holdings)
│   ├── HoldingsView (Full portfolio table, live P&L, Buy/Sell buttons)
│   ├── TransactionsView (Complete historical trade ledger with realized P&L)
│   ├── BudgetView (Wallet manager, cash top-ups, audit history)
│   └── LearnView (Educational academy for technical indicators)
│
└── Modals (Rendered on user action)
    ├── BuyModal (Stock search, live LTP auto-fill, quantity, total price)
    ├── SellModal (Share count selector, live P&L preview, cash return)
    ├── StockChartModal (1D / 1W / 1Y interactive graphs + technical indicator stats)
    │   └── StockChart (Custom SVG rendering engine with hover tooltips and SMA curves)
    └── ConfirmModal (Destructive action confirmation dialog)
```

### 4.2 State Management & Synchronization
* **Server as Primary Source of Truth**: On load, `App` calls `http://localhost:3000/api/portfolio`. The retrieved holdings, transactions, and budget populate React state.
* **Optimistic UI Updates**: When you buy, sell, or adjust budget, React immediately updates local state so the interface feels instantaneous, while simultaneously sending the mutation to the backend.
* **Offline Backup**: State changes are mirrored to browser `localStorage` as a secondary backup in case the Python server is temporarily closed.
* **Auto-Refresh Polling**: Every 5 minutes, `loadPrices()` automatically polls the backend for fresh NSE quotes.

---

## 5. Technical Indicators & Charting Engine

The chart is drawn using a lightweight, native SVG system (`StockChart`) embedded directly in React, avoiding bloated 3rd-party charting libraries.

### 5.1 Simple Moving Averages (50-Day & 200-Day SMA)
* **What it is**: The arithmetic average of closing prices over a specific rolling window:
  $$\text{SMA}_n = \frac{1}{n} \sum_{i=1}^n \text{Close}_i$$
* **50-Day SMA (Yellow Line)**: Represents medium-term momentum.
* **200-Day SMA (Blue Line)**: Represents long-term institutional trend direction.
* **Implementation** ([`stockfolio.html`](file:///home/aryan/src/stockfolio/stockfolio.html)): Implemented with a sliding window $O(N)$ algorithm in `calculateSMA()`.

### 5.2 Golden Cross & Death Cross Detection
* **Golden Cross**: Triggers when the 50-Day SMA crosses **above** the 200-Day SMA from below. In technical analysis, this signals strong bullish momentum and potential long-term trend reversal to the upside.
* **Death Cross**: Triggers when the 50-Day SMA crosses **below** the 200-Day SMA from above. Signals long-term bearish momentum and risk of further downside.
* **Implementation** ([`stockfolio.html`](file:///home/aryan/src/stockfolio/stockfolio.html)): `detectCrossovers()` scans consecutive SMA data points, detects the exact historical crossover date and price, and displays a prominent badge (`🌟 Golden Cross` or `⚠️ Death Cross`) in the chart header.

### 5.3 Relative Strength Index (RSI - 14 Day)
* **What it is**: An oscillator bounded between 0 and 100 measuring price speed and magnitude:
  $$\text{RSI} = 100 - \left( \frac{100}{1 + \text{RS}} \right), \quad \text{where } \text{RS} = \frac{\text{Average Gain}}{\text{Average Loss}}$$
* **Smoothing**: Uses Wilder's Exponential Smoothing technique over a standard 14-day window.
* **Thresholds**:
  * **RSI > 70 (Overbought - Red)**: Stock price has rallied aggressively; short-term pullback or profit-taking is common.
  * **RSI < 30 (Oversold - Green)**: Heavy selling pressure; potential bargain territory or technical bounce candidate.
  * **30 to 70 (Neutral)**: Normal market action.

---

## 6. End-to-End User Workflows

### 6.1 Buying a Stock
1. Click **"+ Buy Stock"** in the Dashboard or Holdings tab.
2. In `BuyModal`, type a company name or ticker (e.g. `Reliance` or `TCS`).
3. The server queries Yahoo Finance and displays live suggestions.
4. Selecting a stock instantly fetches its current market price (LTP) and auto-populates the **Buy Price** field (which remains editable).
5. Entering a quantity calculates the total cost. If funds are sufficient, clicking **"Confirm Buy"** dispatches `POST /api/portfolio/buy`.
6. The backend deducts funds from `portfolio.json`, updates holdings, appends to transactions, and returns the updated state to React.

### 6.2 Selling a Stock
1. In the **Holdings** tab, click **"Sell"** next to any owned stock.
2. `SellModal` displays your purchase price, the current market price, and calculates your realized profit or loss in real time.
3. Choosing the quantity to sell and clicking **"Confirm Sell"** calls `POST /api/portfolio/sell`.
4. The backend adjusts or deletes the holding, credits cash back to your wallet, records the realized P&L in the transaction history, and persists changes to disk.

### 6.3 Analyzing Charts & Indicators
1. Click on any stock row or click the **"Chart"** button.
2. `StockChartModal` fetches historical price data via `/api/chart`.
3. Switch between **1 Day**, **1 Week**, and **1 Year** tabs.
4. On the 1 Year tab, 50-SMA and 200-SMA lines are superimposed over the price graph, and current RSI and crossover signals are calculated and displayed.
5. Click **"📘 How to read these?"** to open the dedicated **Learn** tab for an in-depth breakdown of the indicators.
