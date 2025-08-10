import yaml
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from pathlib import Path
import joblib

class ModelTrainer:
    """
    Handles the training of a single, universal model on panel data.
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

    def prepare_panel_data(self, data_dict: dict) -> pd.DataFrame:
        """
        Combines data from all tickers into a single panel DataFrame.
        Also normalizes features cross-sectionally (by ranking).
        """
        print("Preparing panel data for model training...")
        # Add a 'Ticker' column to each dataframe before combining
        for ticker, df in data_dict.items():
            df['Ticker'] = ticker
        
        # Combine all dataframes into one
        panel_data = pd.concat(data_dict.values())
        
        # --- Cross-sectional Ranking (Normalization) ---
        # For each day, rank stocks based on their feature values.
        # This makes features comparable across different stocks.
        for feature in self.features_to_use:
            panel_data[f'{feature}_rank'] = panel_data.groupby(level='Date')[feature].rank(pct=True)
            
        # Create a binary target variable for classification
        # 1 if future return is positive, 0 otherwise.
        panel_data['target_binary'] = (panel_data[self.target_col] > 0).astype(int)

        panel_data.dropna(inplace=True)
        # Set a MultiIndex for easier time-series and cross-sectional access
        panel_data.set_index(['Date', 'Ticker'], inplace=True, append=True)
        panel_data.index = panel_data.index.droplevel(0) # Drop the old integer index

        print("Panel data preparation complete.")
        return panel_data

    def train_model(self, panel_data: pd.DataFrame):
        """
        Trains a universal LightGBM model on the prepared panel data.
        
        Returns:
            tuple: A tuple containing the trained model and the test set DataFrame.
        """
        print("Starting model training...")
        
        # Define features (ranked) and target
        ranked_features = [f'{feature}_rank' for feature in self.features_to_use]
        X = panel_data[ranked_features]
        y = panel_data['target_binary']

        # Perform a chronological split (cannot shuffle time-series data)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=self.model_settings['test_size'], 
            shuffle=False
        )

        # Train the LightGBM Classifier
        model = lgb.LGBMClassifier(objective='binary', random_state=42)
        model.fit(X_train, y_train)

        # Evaluate the model
        accuracy = model.score(X_test, y_test)
        print(f"Model training complete. Test Accuracy: {accuracy:.4f}")

        # Save the trained model
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, self.model_path)
        print(f"Model saved to {self.model_path}")

        # --- THIS IS THE CRITICAL CHANGE ---
        # Get the full data for the test set period
        test_set_data = panel_data.loc[X_test.index]
        
        # Return both the model and the data it should be tested on
        return model, test_set_data
