from flask import Flask, request, render_template, jsonify
import yfinance as yf
import plotly.graph_objs as go
import json
from plotly.utils import PlotlyJSONEncoder
import pandas as pd

tracker = Flask(__name__)

@tracker.route('/', methods=['GET', 'POST'])

def home():
    company_name = None
    current_price = None
    error = None

    if request.method == 'POST':
        ticker_input = request.form.get('ticker', '').upper()
        try:
            ticker = yf.Ticker(ticker_input)
            info = ticker.info
            company_name = info.get('shortName')
            current_price = info.get('currentPrice')

            if not company_name or not current_price:
                error = f"Could not find valid data for ticker '{ticker_input}'."
                return render_template('index.html', error=error)
            
            return render_template('information.html', company_name=company_name, current_price=current_price, ticker=ticker_input)

        except Exception as e:
            error = f"Error retrieving data for '{ticker_input}'. Please check the ticker symbol. ({e})"
            return render_template('index.html', error=error)

    return render_template('index.html', company_name=company_name, current_price=current_price, error=error)

@tracker.route('/switch_chart', methods=['POST'])

def switch_chart():
    ticker = request.form.get('ticker')
    time_range = request.form.get('range') 

    intervals = {
        "1d": ("1d", "1m"),
        "5d": ("5d", "5m"),
        "1mo": ("1mo", "1h"),
        "6mo": ("6mo", "1d"),
        "1y": ("1y", "1d"),
        "5y": ("5y", "1wk")
    }

    period, interval = intervals.get(time_range, ("1d", "1m"))

    try:
        data = yf.download(ticker, period=period, interval=interval)

        # Handle yfinance MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]
            
            close_col_name = None
            if 'Close' in data.columns:
                close_col_name = 'Close'
            elif f'Close_{ticker}' in data.columns: 
                close_col_name = f'Close_{ticker}'
            
            if close_col_name:
                data = data[[close_col_name]].copy()
                data.columns = ['Close']
            else:
                raise ValueError("Could not find 'Close' column after flattening MultiIndex.")

        if data.empty:
            return jsonify({'error': f'No data available for {ticker} in the {time_range.upper()} range.'}), 404

        if 'Close' not in data.columns:
            return jsonify({'error': f'Close price data not found for {ticker}.'}), 404

        x_data = data.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
        y_data = data["Close"].tolist()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines',
            name='Close Price', line=dict(color="#36FFB9", width=2)
        ))

        # Base layout settings for the chart
        layout_settings = {
            'title': f'<b>{ticker}</b> - Close Price ({time_range.upper()})',
            'title_x': 0.01,
            'xaxis_title': 'Date',
            'yaxis_title': 'Price (USD)',
            'height': 450,
            'margin': dict(l=20, r=80, t=40, b=60),
            'font': dict(family="Red Hat Display, sans-serif", size=12, color="white"),
            'paper_bgcolor': "rgba(0,0,0,0)",
            'plot_bgcolor': "rgba(0,0,0,0)",
            'xaxis': dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                linecolor='rgba(255,255,255,0.3)',
                tickfont=dict(color='white') 
            ),
            'yaxis': dict(
                showgrid=False,
                showline=False,
                gridcolor='rgba(255,255,255,0.1)',
                linecolor='rgba(255,255,255,0.3)',
                tickfont=dict(color='white'),
                side='right'
            ),
            'title_font_color': "white",
            'hovermode': "x unified"
        }

        # Apply Plotly rangebreaks only for intraday intervals (1m, 30m)
        if interval in ["1m", "5m","30m", "1h"]:
            layout_settings['xaxis']['rangebreaks'] = [
                dict(bounds=["sat", "mon"]),  # Hide weekends
                dict(bounds=[20, 13.5], pattern="hour"), # Hide 4 PM ET (20:00 UTC) to 9:30 AM ET (13:30 UTC)
            ]

        fig.update_layout(layout_settings)

        graph_json = json.dumps(fig.to_dict(), cls=PlotlyJSONEncoder) 
        
        return jsonify({'graph_json': graph_json})

    except Exception as e:
        # Simplified error message for the frontend
        return jsonify({'error': 'Error generating chart data. Please try again or try a different ticker/range.'}), 500

if __name__ == '__main__':
    tracker.config['TEMPLATES_AUTO_RELOAD'] = True
    tracker.run(debug=True)