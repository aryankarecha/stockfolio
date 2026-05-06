# Stockfolio — India Portfolio Tracker

Stockfolio is a lightweight, local client-server web application for tracking Indian stock portfolios (NSE/BSE). It features a responsive UI built with React and fetches live market data directly from Yahoo Finance.

To bypass strict browser CORS restrictions and unreliable public proxy servers, this project pairs a single-file frontend with a tiny, local Python Flask server to securely route API requests.

---

## Project Structure

The entire application runs on just two files:

- `stockfolio.html` — The Frontend. This file contains the React application, CSS styling, and UI logic packed into a single document. It stores all portfolio data locally in your browser.
- `server.py` — The Backend. A lightweight Flask server that acts as a secure bridge, fetching live ticker data and search results directly from the Yahoo Finance API.

---

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- **Python 3.x** (Download from [python.org](https://www.python.org/downloads/))
- A modern web browser (Chrome, Firefox, Safari, Edge)

---

## Installation & Setup

### Step 1: Install Backend Dependencies
The Python server requires three basic libraries to run: `flask` (the web framework), `flask-cors` (to allow your browser to talk to the server), and `requests` (to fetch data from Yahoo).

Open your terminal, navigate to the folder containing your files, and run:
```bash
pip install flask flask-cors requests
```

### Step 2: Start the Backend Server

The frontend relies entirely on the backend to fetch live prices and search queries. You must start the server before opening the app.

In your terminal, run:

```bash
python server.py
```

You should see a message confirming the server is running on http://localhost:3000. Keep this terminal window open and running in the background while you use the app!

### Step 3: Open the Frontend App

Because the backend is handling all the complex network requests, the frontend does not need to be hosted on a web server to work locally.

Simply double-click the stockfolio.html file to open it in your default web browser. (Alternatively, you can drag and drop the file into an open browser tab).

## How It Works (The Architecture)

- The UI Request: stockfolio.html runs locally in your browser. When it needs live prices or wants to search for a stock, it sends a local HTTP request to your Python server running on port 3000.
- The CORS Bypass: server.py receives the request. Because it is a standalone Python script and not a web browser, it is not bound by CORS security rules. It safely queries Yahoo Finance's v8/spark and v1/search endpoints directly.
- The Data Delivery: Yahoo Finance sends the live data back to the Python server, which immediately parses it and forwards it to your React UI to be displayed.
- Data Persistence: All portfolio data (your specific holdings, transaction history, and budget) is saved securely in your browser's localStorage. It will persist automatically even if you close the tab or restart your computer.

## Troubleshooting

- The app is stuck on "Loading Stockfolio...": This usually means there is a syntax error in the HTML file preventing the React compiler (Babel) from running. Open your browser's Developer Tools (Right Click > Inspect > Console) to look for JavaScript syntax errors.
- The ticker says "ERR" or prices won't load: Ensure that your terminal running server.py is open and active. If the terminal is closed or crashed, the app loses its connection to the live data feed.
- Search returns no results: Ensure you are searching for valid Indian companies. The backend API is specifically tuned to filter for .NS (NSE) and .BO (BSE) suffixes on Yahoo Finance.
- Address already in use error: If Python complains that port 3000 is in use, another app is using it. You can change port=3000 to port=5000 at the very bottom of server.py, and then update the http://localhost:3000 API links inside stockfolio.html to match.


