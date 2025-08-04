import pandas as pd

def run_backtest(X_test, y_pred, initial_capital=100000.0):
    """
    Runs a backtest for a given set of predictions and price data.

    Args:
        X_test (pd.DataFrame): DataFrame with test features, must include 'Close' price.
        y_pred (np.array): Array of model predictions (0 or 1).
        initial_capital (float): The starting capital for the portfolio.

    Returns:
        pd.DataFrame: A DataFrame with the portfolio value over time.
    """
    portfolio_values = []
    portfolio = {
        'cash': initial_capital,
        'stock_shares': 0
    }

    for i in range(len(X_test)):
        current_price = X_test.iloc[i]['Close']
        signal = y_pred[i]
        if signal == 1 and portfolio['cash'] > 0:
            shares_to_buy = portfolio['cash'] / current_price
            portfolio['stock_shares'] += shares_to_buy
            portfolio['cash'] = 0
        elif signal == 0 and portfolio['stock_shares'] > 0:
            cash_from_sale = portfolio['stock_shares'] * current_price
            portfolio['cash'] += cash_from_sale
            portfolio['stock_shares'] = 0
        current_portfolio_value = portfolio['cash'] + (portfolio['stock_shares'] * current_price)
        portfolio_values.append(current_portfolio_value)

    results_df = pd.DataFrame(index=X_test.index)
    results_df['Portfolio_Value'] = portfolio_values
    
    return results_df