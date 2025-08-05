# Quantitative Factor-Based Trading Strategy & Backtesting Engine
https://algorithmic-trading-engine-production.up.railway.app/

This project is a complete, end-to-end system for developing, backtesting, and analyzing a quantitative, factor-based stock trading strategy. The system automatically downloads historical stock data, engineers predictive features, trains a universal machine learning model on cross-sectional data, and runs a multi-asset backtest. The results are presented in a dynamic, interactive web dashboard built with Flask and deployed as a containerized application.

## ✨ Key Features

* **Professional Quantitative Strategy:** Implements a universal factor model, training a single `LightGBM` classifier on normalized, cross-sectional panel data rather than over-fitting to a single stock.
* **Modular & Object-Oriented:** The entire pipeline is built with reusable Python classes for Data Handling, Feature Engineering, Model Training, and Backtesting, promoting clean code and separation of concerns.
* **Configuration-Driven:** The entire strategy (tickers, dates, features, model parameters) is controlled from a single `config.yaml` file, allowing for rapid strategy testing without changing the source code.
* **Automated End-to-End Pipeline:** A single command (`python main.py`) runs the entire process from data acquisition to generating final backtest results.
* **Interactive Web Dashboard:** A dynamic frontend built with **Flask** and **Chart.js** visualizes key performance indicators (KPIs), the equity curve, drawdown, returns distribution, and a detailed trade log with date-range filtering.
* **Robust Caching:** Features intelligent, ticker-specific caching to minimize redundant data downloads.
* **Containerized & Deployed:** Includes a `Dockerfile` for easy containerization and has been successfully deployed to a public cloud platform (Railway).

## 🛠️ Tech Stack

| Category | Technology / Library |
| ----- | ----- |
| **Language** | Python 3.11+ |
| **Backend Framework** | Flask |
| **Frontend** | HTML, CSS, JavaScript |
| **Charting** | Chart.js |
| **Machine Learning** | LightGBM (LGBMClassifier), scikit-learn |
| **Data & Analysis** | pandas, NumPy, yfinance, pandas_ta |
| **Deployment** | Docker, Gunicorn |
| **Configuration** | PyYAML |
| **Version Control** | Git & GitHub |

## 🚀 How to Run Locally

### Prerequisites
* Python 3.11 or higher
* Git

### 1. Clone the Repository
```
git clone https://github.com/19rishabh/algorithmic-trading-engine.git
cd algorithmic-trading-engine
```

### 2. Set Up the Virtual Environment
```
Create and activate the virtual environment
python -m venv quant_env

On Windows
quant_env\Scripts\activate

On macOS / Linux
source quant_env/bin/activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Run the Full Pipeline
This command will download the data, train the model, and generate the backtest results in the `/results` folder.
```
python main.py
```

### 5. Launch the Dashboard
This command will start the Flask web server.
```
python app.py
```

Open your web browser and navigate to **http://127.0.0.1:5000** to view the dashboard.

## 📂 Project Structure
```
├── config/             # Contains the central strategy_config.yaml
├── data/               # (Generated & Ignored) Caches raw ticker data
├── models/             # (Generated & Ignored) Stores the trained universal model
├── notebooks/          # Contains the research.ipynb for experimentation
├── results/            # (Generated & Ignored) Stores the final backtest CSVs
├── src/                # All core Python source code (OOP classes)
├── static/             # CSS and JavaScript files for the frontend
├── templates/          # HTML templates for the Flask app
├── app.py              # The Flask web application
├── main.py             # The main pipeline orchestrator script
├── Dockerfile          # Configuration for containerizing the application
└── requirements.txt    # Project dependencies
```
