from flask import Flask, render_template, json, send_file
import pandas as pd
import numpy as np
from pathlib import Path

app = Flask(__name__)

# --- NEW: Define paths at the top ---
RESULTS_DIR = Path('results/')
PORTFOLIO_PATH = RESULTS_DIR / 'portfolio_results.csv'
TRADE_LOG_PATH = RESULTS_DIR / 'trade_log.csv'

@app.route('/')
@app.route('/dashboard')
def dashboard():
    kpis = {}
    chart_data = {}
    recent_trades = []

    try:
        # Load portfolio results
        results_df = pd.read_csv(PORTFOLIO_PATH, index_col='Date', parse_dates=True)
        
        # --- Calculate KPIs (unchanged) ---
        # ... (same KPI calculation logic as before) ...
        initial_value = results_df['Portfolio_Value'].iloc[0]
        final_value = results_df['Portfolio_Value'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value
        daily_returns = results_df['Portfolio_Value'].pct_change().dropna()
        sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        rolling_max = results_df['Portfolio_Value'].cummax()
        daily_drawdown = (results_df['Portfolio_Value'] / rolling_max) - 1.0
        max_drawdown = daily_drawdown.min()

        kpis = {
            'final_portfolio_value': f"₹{final_value:,.2f}",
            'total_return': f"{total_return:.2%}",
            'max_drawdown': f"{max_drawdown:.2%}",
            'sharpe_ratio': f"{sharpe_ratio:.2f}"
        }

        # --- Prepare Chart Data (unchanged) ---
        # ... (same chart data preparation as before) ...
        equity_curve_df = results_df.reset_index()
        equity_curve_df['Date'] = equity_curve_df['Date'].dt.strftime('%Y-%m-%d')
        drawdown_df = daily_drawdown.reset_index()
        drawdown_df['Date'] = drawdown_df['Date'].dt.strftime('%Y-%m-%d')
        chart_data = {
            'equity_curve': equity_curve_df[['Date', 'Portfolio_Value']].to_dict('records'),
            'drawdown': drawdown_df.rename(columns={0: 'Drawdown'}).to_dict('records'),
            'returns_histogram': daily_returns.tolist()
        }

        # --- NEW: Load and prepare recent trades for display ---
        trade_log_df = pd.read_csv(TRADE_LOG_PATH, index_col='Date')
        # Get the last 20 trades and format them for the HTML table
        recent_trades = trade_log_df.tail(20).reset_index()
        # Format for better display
        recent_trades['Date'] = pd.to_datetime(recent_trades['Date']).dt.strftime('%Y-%m-%d')
        recent_trades['Signal'] = recent_trades['Signal'].map('{:.2%}'.format)
        recent_trades['Daily_Return'] = recent_trades['Daily_Return'].map('{:.2%}'.format)
        recent_trades = recent_trades.to_dict('records')

    except Exception as e:
        print(f"An error occurred: {e}")
        kpis = {key: "Error" for key in ['final_portfolio_value', 'total_return', 'max_drawdown', 'sharpe_ratio']}
        chart_data = {'equity_curve': [], 'drawdown': [], 'returns_histogram': []}
        recent_trades = []
        
    return render_template('dashboard.html', kpis=kpis, chart_data=chart_data, trades=recent_trades)

# --- NEW: Route for downloading the full trade log ---
@app.route('/download/trade_log')
def download_trade_log():
    try:
        return send_file(TRADE_LOG_PATH, as_attachment=True, download_name='full_trade_log.csv')
    except FileNotFoundError:
        return "Trade log file not found. Please run main.py first.", 404

if __name__ == '__main__':
    app.run(debug=True)