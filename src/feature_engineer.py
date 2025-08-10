import yaml
import pandas as pd
import pandas_ta as ta

class FeatureEngineer:
    """
    Handles all feature engineering and target creation.
    """
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.feature_settings = self.config['feature_settings']
        self.target_settings = self.config['target_settings']

    def _load_config(self, config_path: str) -> dict:
        """Loads the YAML configuration file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}")
            return {}

    def add_features(self, data_dict: dict) -> dict:
        """
        Adds technical indicators and the target variable to each stock's DataFrame.
        """
        for ticker, df in data_dict.items():
            df.ta.rsi(length=self.feature_settings['rsi_length'], append=True)
            df.ta.macd(fast=self.feature_settings['macd_fast'], 
                      slow=self.feature_settings['macd_slow'], 
                      signal=self.feature_settings['macd_signal'], 
                      append=True)
            df.ta.bbands(length=self.feature_settings['bbands_length'], 
                        std=self.feature_settings['bbands_std'], 
                        append=True)
            
            future_period = self.target_settings['future_period']
            df[f'fwd_return_{future_period}d'] = df['Close'].pct_change(periods=future_period).shift(-future_period)

            df.dropna(inplace=True)
        
        return data_dict
