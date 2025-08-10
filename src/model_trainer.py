import yaml
import pandas as pd
import lightgbm as lgb
from pathlib import Path
import joblib

class ModelTrainer:
    def __init__(self, config_path: str):
        # ... (init is the same)

    def _load_config(self, config_path: str) -> dict:
        # ... (unchanged)
        
    def split_data(self, data_dict: dict) -> tuple:
        """NEW: Splits data into train and test sets BEFORE any other processing."""
        print("Splitting data into training and testing sets...")
        train_data = {}
        test_data = {}
        test_size = self.model_settings['test_size']

        for ticker, df in data_dict.items():
            split_index = int(len(df) * (1 - test_size))
            train_data[ticker] = df.iloc[:split_index].copy()
            test_data[ticker] = df.iloc[split_index:].copy()
        
        return train_data, test_data

    def prepare_panel_data(self, data_dict: dict) -> pd.DataFrame:
        # ... (this method is the same as your current version)

    def train_model(self, train_panel_data: pd.DataFrame):
        """This method now ONLY trains the model and returns it."""
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
