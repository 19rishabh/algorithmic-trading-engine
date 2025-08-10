from src.data_handler import DataHandler
from src.feature_engineer import FeatureEngineer
from src.model_trainer import ModelTrainer
from src.backtester import Backtester

def run_pipeline():
    print("--- Starting Quant Trading Pipeline ---")
    config_path = 'config/strategy_config.yaml'

    # --- Step 1: Data Handling (No change) ---
    data_handler = DataHandler(config_path=config_path)
    raw_data = data_handler.fetch_data()

    # --- Step 2: Split Data FIRST ---
    print("\n[Phase 2/5] Splitting data into Train/Test sets...")
    model_trainer = ModelTrainer(config_path=config_path)
    train_raw_data, test_raw_data = model_trainer.split_data(raw_data)

    # --- Step 3: Feature Engineering (Done separately on each set) ---
    print("\n[Phase 3/5] Feature Engineering...")
    feature_engineer = FeatureEngineer(config_path=config_path)
    train_featured_data = feature_engineer.add_features(train_raw_data)
    test_featured_data = feature_engineer.add_features(test_raw_data)

    # --- Step 4: Model Training (Only on training data) ---
    print("\n[Phase 4/5] Model Training...")
    train_panel_data = model_trainer.prepare_panel_data(train_featured_data)
    model = model_trainer.train_model(train_panel_data)

    # --- Step 5: Backtesting (Only on testing data) ---
    print("\n[Phase 5/5] Backtesting...")
    test_panel_data = model_trainer.prepare_panel_data(test_featured_data)
    backtester = Backtester(config_path=config_path)
    backtester.run_backtest(test_panel_data)

    print("\n--- Pipeline Finished Successfully ---")

if __name__ == "__main__":
    run_pipeline()
