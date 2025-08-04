import yaml
import yfinance as yf
import pandas as pd
from pathlib import Path

class DataHandler:
    """
    Handles all data operations: loading config, fetching, and using
    an individual cache file for each ticker.
    """
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.data_settings = self.config['data_settings']
        self.tickers = self.data_settings['tickers']
        self.start_date = self.data_settings['start_date']
        self.end_date = self.data_settings['end_date']
        
        # This now correctly looks for 'cache_dir'
        self.cache_dir = Path(self.data_settings['cache_dir'])
        # Ensure the cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: str) -> dict:
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}")
            return {}

    def fetch_data(self) -> dict:
        """
        Fetches data for all tickers, using individual cache files for each.
        If a ticker's cache doesn't exist, it's downloaded and cached.
        """
        all_stock_data = {}
        for ticker in self.tickers:
            cache_file = self.cache_dir / f"{ticker}.pkl"

            if cache_file.exists():
                print(f"Loading '{ticker}' from cache...")
                all_stock_data[ticker] = pd.read_pickle(cache_file)
            else:
                print(f"Cache not found for '{ticker}'. Downloading from yfinance...")
                try:
                    data = yf.download(ticker, start=self.start_date, end=self.end_date, progress=False)
                    
                    if data.empty:
                        print(f"No data found for {ticker}. Skipping.")
                        continue
                    
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.get_level_values(0)

                    all_stock_data[ticker] = data
                    pd.to_pickle(data, cache_file)
                    print(f"Successfully downloaded and cached '{ticker}'.")
                
                except Exception as e:
                    print(f"Could not download data for {ticker}. Error: {e}")
        
        return all_stock_data