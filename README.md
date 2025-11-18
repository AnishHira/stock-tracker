# Stock Tracking Application

A Flask web application for visualising stock market data with interactive charts.

## Current Features

- Search for stocks by ticker symbol (eg. AAPL, NVDA, TSLA)
- Interactive Plotly charts showing historical price data
- Time range options (1d, 5d, 1m, 6m, 1y, 5y)

## Tech Stack

- Flask
- Plotly
- yfinance API
- pandas

## Installation

1. Clone the repository

2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate #macOS/Linux
```
3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
python stock_tracker.py
```

5. Open http://127.0.0.1:5000 in your browser

## Status

This project is still in active development!