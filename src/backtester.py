import yaml
import pandas as pd
from pathlib import Path
import joblib

class Backtester:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.backtest_settings = self.config['backtest_settings']
        self.model_settings = self.config['model_settings']
        self.initial_capital = self.backtest_settings['initial_capital']
        self.model_path = Path(self.model_settings['model_path'])
        
        # Paths for saving results
        self.results_dir = Path(self.backtest_settings['results_dir'])
        self.portfolio_results_path = self.results_dir / 'portfolio_results.csv'
        self.trade_log_path = self.results_dir / 'trade_log.csv'
        
        try:
            self.model = joblib.load(self.model_path)
            print(f"Successfully loaded model from {self.model_path}")
        except FileNotFoundError:
            self.model = None

    def _load_config(self, config_path: str) -> dict:
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}")
            return {}

    def run_backtest(self, test_set_data: pd.DataFrame):
        """
        Runs a multi-asset backtest on the UNSEEN test set data.
        This version correctly simulates trades to avoid lookahead bias.
        """
        if self.model is None:
            print("Cannot run backtest without a loaded model.")
            return None
        
        print("Running backtest on unseen test data...")
        
        ranked_features = [f'{feature}_rank' for feature in self.model_settings['features_to_use']]
        dates = sorted(test_set_data.index.get_level_values('Date').unique())
        
        portfolio_value = self.initial_capital
        portfolio_values = []
        trade_log = []
        
        # Create a pivot table of closing prices for easy lookup
        close_prices_pivot = test_set_data['Close'].unstack(level='Ticker')

        # We loop until the second to last day because we need the next day's price to calculate return
        for i in range(len(dates) - 1):
            current_date = dates[i]
            next_date = dates[i+1]
            
            # Get data for all stocks on the current day
            daily_data = test_set_data.loc[current_date].copy()
            
            # Get model's prediction (probability of price going up)
            up_probabilities = self.model.predict_proba(daily_data[ranked_features])[:, 1]
            daily_data['signal'] = up_probabilities
            
            # --- Strategy Logic: Pick the stock with the highest signal ---
            top_stock_ticker = daily_data.sort_values(by='signal', ascending=False).index[0]
            
            # --- Correct Return Calculation ---
            # Look up the price for today and tomorrow to simulate the trade
            price_today = close_prices_pivot.loc[current_date, top_stock_ticker]
            price_tomorrow = close_prices_pivot.loc[next_date, top_stock_ticker]
            
            # Avoid division by zero if price is somehow zero
            if price_today > 0:
                daily_return = (price_tomorrow - price_today) / price_today
            else:
                daily_return = 0

            # Log the trade and update portfolio value
            trade_log.append({
                'Date': current_date,
                'Ticker': top_stock_ticker,
                'Signal': daily_data.loc[top_stock_ticker, 'signal'],
                'Daily_Return': daily_return,
                'Portfolio_Value_Before': portfolio_value,
                'Portfolio_Value_After': portfolio_value * (1 + daily_return)
            })

            portfolio_value *= (1 + daily_return)
            portfolio_values.append(portfolio_value)

        # --- Save Results ---
        # Note: The results will have one less day than the test set size
        results_df = pd.DataFrame({'Date': dates[:-1], 'Portfolio_Value': portfolio_values}).set_index('Date')
        trade_log_df = pd.DataFrame(trade_log).set_index('Date')

        self.results_dir.mkdir(parents=True, exist_ok=True)
        results_df.to_csv(self.portfolio_results_path)
        trade_log_df.to_csv(self.trade_log_path)

        print(f"Backtest complete. Results saved to {self.results_dir}")
        return results_df, trade_log_df
