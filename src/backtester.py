import yaml
import pandas as pd
from pathlib import Path
import joblib

class Backtester:
    """
    Handles the backtesting of a strategy using a universal model.
    """
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.backtest_settings = self.config['backtest_settings']
        self.model_settings = self.config['model_settings']
        self.initial_capital = self.backtest_settings['initial_capital']
        self.model_path = Path(self.model_settings['model_path'])
        self.results_path = Path(self.backtest_settings['results_path'])
        
        # Load the trained universal model
        try:
            self.model = joblib.load(self.model_path)
            print(f"Successfully loaded model from {self.model_path}")
        except FileNotFoundError:
            print(f"Error: Model file not found at {self.model_path}. Please train the model first.")
            self.model = None

    def _load_config(self, config_path: str) -> dict:
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}")
            return {}

    def run_backtest(self, panel_data: pd.DataFrame):
        """
        Runs a multi-asset backtest on the panel data.
        Strategy: On each day, go long on the stock with the highest 'up' probability.
        """
        if self.model is None:
            print("Cannot run backtest without a loaded model.")
            return None
        
        print("Running backtest...")
        
        # Prepare data for prediction
        ranked_features = [f'{feature}_rank' for feature in self.model_settings['features_to_use']]
        
        # Get unique dates from our panel data, sorted
        dates = sorted(panel_data.index.get_level_values('Date').unique())
        
        # Initialize portfolio
        portfolio_value = self.initial_capital
        portfolio_values = []
        
        for date in dates:
            # Get data for the current day for all stocks
            daily_data = panel_data.loc[date].copy()
            
            # Predict probability of 'up' movement for all stocks today
            # The model's predict_proba returns [[prob_down, prob_up], ...]
            up_probabilities = self.model.predict_proba(daily_data[ranked_features])[:, 1]
            daily_data['signal'] = up_probabilities
            
            # --- Strategy Logic ---
            # Find the stock with the highest predicted 'up' probability
            top_stock = daily_data.sort_values(by='signal', ascending=False).iloc[0]
            
            # Simulate holding this one stock for the day
            # We get the day's return from our target column (fwd_return)
            # This is a simplified "vectorized" backtest. We assume we invest our
            # entire portfolio in the top stock for one day.
            daily_return = top_stock[f"fwd_return_{self.config['target_settings']['future_period']}d"]
            portfolio_value *= (1 + daily_return)
            portfolio_values.append(portfolio_value)

        # Create results DataFrame
        results_df = pd.DataFrame({
            'Date': dates,
            'Portfolio_Value': portfolio_values
        }).set_index('Date')
        
        # Save results to CSV
        self.results_path.parent.mkdir(parents=True, exist_ok=True)
        results_df.to_csv(self.results_path)
        print(f"Backtest complete. Results saved to {self.results_path}")

        return results_df