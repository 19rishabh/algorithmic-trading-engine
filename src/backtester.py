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
        
        # NEW: Define path for the trade log
        self.results_dir = Path(self.backtest_settings['results_dir'])
        self.portfolio_results_path = self.results_dir / 'portfolio_results.csv'
        self.trade_log_path = self.results_dir / 'trade_log.csv'
        
        try:
            self.model = joblib.load(self.model_path)
            print(f"Successfully loaded model from {self.model_path}")
        except FileNotFoundError:
            self.model = None

    def _load_config(self, config_path: str) -> dict:
        # ... (this method is unchanged)
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}")
            return {}

    def run_backtest(self, panel_data: pd.DataFrame):
        if self.model is None: # ... (unchanged)
            return None
        
        print("Running backtest and generating trade log...")
        ranked_features = [f'{feature}_rank' for feature in self.model_settings['features_to_use']]
        dates = sorted(panel_data.index.get_level_values('Date').unique())
        
        portfolio_value = self.initial_capital
        portfolio_values = []
        trade_log = [] # NEW: List to store our trades

        for date in dates:
            daily_data = panel_data.loc[date].copy()
            up_probabilities = self.model.predict_proba(daily_data[ranked_features])[:, 1]
            daily_data['signal'] = up_probabilities
            
            top_stock = daily_data.sort_values(by='signal', ascending=False).iloc[0]
            daily_return = top_stock[f"fwd_return_{self.config['target_settings']['future_period']}d"]
            
            # NEW: Log the trade details
            trade_log.append({
                'Date': date,
                'Ticker': top_stock['Ticker'],
                'Signal': top_stock['signal'],
                'Daily_Return': daily_return,
                'Portfolio_Value_Before': portfolio_value,
                'Portfolio_Value_After': portfolio_value * (1 + daily_return)
            })

            portfolio_value *= (1 + daily_return)
            portfolio_values.append(portfolio_value)

        # --- Save Results ---
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Save portfolio history
        results_df = pd.DataFrame({'Date': dates, 'Portfolio_Value': portfolio_values}).set_index('Date')
        results_df.to_csv(self.portfolio_results_path)
        
        # NEW: Save the full trade log
        trade_log_df = pd.DataFrame(trade_log).set_index('Date')
        trade_log_df.to_csv(self.trade_log_path)

        print(f"Backtest complete. Results saved to {self.results_dir}")
        return results_df, trade_log_df