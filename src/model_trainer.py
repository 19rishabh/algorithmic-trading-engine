import yaml
import pandas as pd
import lightgbm as lgb
from pathlib import Path
import joblib

class ModelTrainer:
    """
    Handles splitting data, preparing panel data, and training the universal model.
    """
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.model_settings = self.config['model_settings']
        self.features_to_use = self.model_settings['features_to_use']
        self.target = self.config['target_settings']['future_period']
        self.target_col = f'fwd_return_{self.target}d'
        self.model_path = Path(self.model_settings['model_path'])

    def _load_config(self, config_path: str) -> dict:
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}")
            return {}
            
    def split_data(self, data_dict: dict) -> tuple:
        """Splits data into train and test sets BEFORE any other processing."""
        train_data = {}
        test_data = {}
        test_size = self.model_settings['test_size']

        for ticker, df in data_dict.items():
            split_index = int(len(df) * (1 - test_size))
            train_data[ticker] = df.iloc[:split_index].copy()
            test_data[ticker] = df.iloc[split_index:].copy()
        
        return train_data, test_data

    def prepare_panel_data(self, data_dict: dict) -> pd.DataFrame:
        """Combines and normalizes data into a panel format."""
        df_list = []
        for ticker, df in data_dict.items():
            temp_df = df.copy()
            temp_df['Ticker'] = ticker
            df_list.append(temp_df)
        
        panel_data = pd.concat(df_list)
        panel_data.reset_index(inplace=True)
        
        for feature in self.features_to_use:
            panel_data[f'{feature}_rank'] = panel_data.groupby('Date')[feature].rank(pct=True)
            
        panel_data['target_binary'] = (panel_data[self.target_col] > 0).astype(int)
        panel_data.dropna(inplace=True)
        panel_data.set_index(['Date', 'Ticker'], inplace=True)

        return panel_data

    def train_model(self, train_panel_data: pd.DataFrame):
        """Trains the universal model ONLY on the training panel data."""
        print("Starting model training...")
        
        ranked_features = [f'{feature}_rank' for feature in self.features_to_use]
        X_train = train_panel_data[ranked_features]
        y_train = train_panel_data['target_binary']

        model = lgb.LGBMClassifier(objective='binary', random_state=42)
        model.fit(X_train, y_train)

        print(f"Model training complete.")
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, self.model_path)
        print(f"Model saved to {self.model_path}")

        return model
