from flask import Flask, render_template, json, send_file, request
import pandas as pd
import numpy as np
from pathlib import Path

app = Flask(__name__)

# --- Define paths at the top for clarity ---
RESULTS_DIR = Path('results/')
PORTFOLIO_PATH = RESULTS_DIR / 'portfolio_results.csv'
TRADE_LOG_PATH = RESULTS_DIR / 'trade_log.csv'

def calculate_performance_metrics(results_df):
    """Helper function to calculate all KPIs from a results dataframe."""
    if results_df.empty:
        return {key: "N/A" for key in ['final_portfolio_value', 'total_return', 'max_drawdown', 'sharpe_ratio']}

    initial_value = results_df['Portfolio_Value'].iloc[0]
    final_value = results_df['Portfolio_Value'].iloc[-1]
    total_return = (final_value - initial_value) / initial_value
    daily_returns = results_df['Portfolio_Value'].pct_change().dropna()
    sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) if daily_returns.std() != 0 else 0
    rolling_max = results_df['Portfolio_Value'].cummax()
    daily_drawdown = (results_df['Portfolio_Value'] / rolling_max) - 1.0
    max_drawdown = daily_drawdown.min()

    return {
        'final_portfolio_value': f"₹{final_value:,.2f}",
        'total_return': f"{total_return:.2%}",
        'max_drawdown': f"{max_drawdown:.2%}",
        'sharpe_ratio': f"{sharpe_ratio:.2f}"
    }

@app.route('/', methods=['GET', 'POST'])
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    try:
        # --- 1. Load the FULL dataset ---
        full_results_df = pd.read_csv(PORTFOLIO_PATH, index_col='Date', parse_dates=True)
        
        # --- 2. Apply Filters (if any) ---
        filtered_df = full_results_df.copy() # Start with the full data
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        if request.method == 'POST':
            if start_date_str:
                filtered_df = filtered_df[filtered_df.index >= pd.to_datetime(start_date_str)]
            if end_date_str:
                filtered_df = filtered_df[filtered_df.index <= pd.to_datetime(end_date_str)]
        
        # --- 3. Calculate everything from the FILTERED data ---
        kpis = calculate_performance_metrics(filtered_df)

        # Prepare chart data from the filtered dataframe
        equity_curve_df = filtered_df.reset_index()
        equity_curve_df['Date'] = equity_curve_df['Date'].dt.strftime('%Y-%m-%d')
        
        daily_returns = filtered_df['Portfolio_Value'].pct_change().dropna()
        rolling_max = filtered_df['Portfolio_Value'].cummax()
        daily_drawdown = (filtered_df['Portfolio_Value'] / rolling_max) - 1.0
        drawdown_df = daily_drawdown.reset_index()
        drawdown_df['Date'] = drawdown_df['Date'].dt.strftime('%Y-%m-%d')
        
        chart_data = {
            'equity_curve': equity_curve_df[['Date', 'Portfolio_Value']].to_dict('records'),
            'drawdown': drawdown_df.rename(columns={0: 'Drawdown'}).to_dict('records'),
            'returns_histogram': daily_returns.tolist()
        }

        # Load and prepare recent trades (this part is fine as is)
        trade_log_df = pd.read_csv(TRADE_LOG_PATH, index_col='Date')
        recent_trades = trade_log_df.tail(20).reset_index()
        recent_trades['Date'] = pd.to_datetime(recent_trades['Date']).dt.strftime('%Y-%m-%d')
        recent_trades['Signal'] = recent_trades['Signal'].map('{:.2%}'.format)
        recent_trades['Daily_Return'] = recent_trades['Daily_Return'].map('{:.2%}'.format)
        recent_trades = recent_trades.to_dict('records')

    except Exception as e:
        print(f"An error occurred: {e}")
        kpis = {key: "Error" for key in ['final_portfolio_value', 'total_return', 'max_drawdown', 'sharpe_ratio']}
        chart_data = {'equity_curve': [], 'drawdown': [], 'returns_histogram': []}
        recent_trades = []
        start_date_str, end_date_str = None, None
        
    return render_template('dashboard.html', kpis=kpis, chart_data=chart_data, trades=recent_trades, start_date=start_date_str, end_date=end_date_str)

# ... (download route is unchanged) ...
@app.route('/download/trade_log')
def download_trade_log():
    try:
        return send_file(TRADE_LOG_PATH, as_attachment=True, download_name='full_trade_log.csv')
    except FileNotFoundError:
        return "Trade log file not found. Please run main.py first.", 404

if __name__ == '__main__':
    app.run(debug=True)
