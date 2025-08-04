# Import our custom classes from the 'src' package
from src.data_handler import DataHandler
from src.feature_engineer import FeatureEngineer
from src.model_trainer import ModelTrainer
from src.backtester import Backtester

def run_pipeline():
    """
    Executes the entire data-to-backtest pipeline.
    """
    print("--- Starting Quant Trading Pipeline ---")

    # Define the path to our configuration file
    config_path = 'config/strategy_config.yaml'

    # --- Step 1: Data Handling ---
    print("\n[Phase 1/4] Data Handling...")
    data_handler = DataHandler(config_path=config_path)
    raw_data = data_handler.fetch_data()

    # --- Step 2: Feature Engineering ---
    print("\n[Phase 2/4] Feature Engineering...")
    feature_engineer = FeatureEngineer(config_path=config_path)
    featured_data = feature_engineer.add_features(raw_data)

    # --- Step 3: Model Training ---
    print("\n[Phase 3/4] Model Training...")
    model_trainer = ModelTrainer(config_path=config_path)
    panel_data = model_trainer.prepare_panel_data(featured_data)
    model_trainer.train_model(panel_data)

    # --- Step 4: Backtesting ---
    print("\n[Phase 4/4] Backtesting...")
    backtester = Backtester(config_path=config_path)
    backtester.run_backtest(panel_data)

    print("\n--- Pipeline Finished Successfully ---")


if __name__ == "__main__":
    # This block ensures that the run_pipeline() function is called 
    # only when the script is executed directly.
    run_pipeline()
