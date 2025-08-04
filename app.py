from flask import Flask, render_template, json
import pandas as pd
import numpy as np
from pathlib import Path

app = Flask(__name__)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    results_path = Path('results/backtest_results.csv')
    kpis = {}
    chart_data = []

    try:
        results_df = pd.read_csv(results_path, index_col='Date', parse_dates=True)
        
        # --- Calculate KPIs ---
        initial_value = results_df['Portfolio_Value'].iloc[0]
        final_value = results_df['Portfolio_Value'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value
        daily_returns = results_df['Portfolio_Value'].pct_change()
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

        # --- Prepare Chart Data ---
        # Convert dataframe to a list of dictionaries for easy JSON conversion
        chart_df = results_df.reset_index()
        chart_df['Date'] = chart_df['Date'].dt.strftime('%Y-%m-%d')
        chart_data = chart_df[['Date', 'Portfolio_Value']].to_dict('records')

    except FileNotFoundError:
        kpis = {key: "N/A" for key in ['final_portfolio_value', 'total_return', 'max_drawdown', 'sharpe_ratio']}
    except Exception as e:
        print(f"An error occurred: {e}")
        kpis = {key: "Error" for key in ['final_portfolio_value', 'total_return', 'max_drawdown', 'sharpe_ratio']}
        
    # Pass both KPIs and chart_data to the template
    return render_template('dashboard.html', kpis=kpis, chart_data=chart_data)


if __name__ == '__main__':
    app.run(debug=True)