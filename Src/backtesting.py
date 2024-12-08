import numpy as np
import pandas as pd
import yfinance as yf

def backtest_strategy(strategy_fn, ticker, start_date, end_date):
    """
    Backtest a given strategy over a date range.

    Parameters:
    strategy_fn (function): The strategy function to backtest
    ticker (str): The stock ticker symbol
    start_date (str): Start date in 'YYYY-MM-DD'
    end_date (str): End date in 'YYYY-MM-DD'

    Returns:
    DataFrame: Backtest results with dates and P&L
    """
    # Fetch historical data
    data = yf.download(ticker, start=start_date, end=end_date)
    dates = data.index
    pnl_list = []

    for date in dates:
        # Set up necessary parameters for the strategy
        S = data.loc[date, 'Close']  # Ensure S is a scalar
        K = S * 1.05  # Example strike price 5% above current price
        premium = 1.0  # Example premium, replace with actual calculation

        # Simulate strategy P&L at expiration
        S_T = S  # For simplicity, assume no price change
        pnl = strategy_fn(S, K, premium, np.array([S_T]).flatten())[0]
        pnl_list.append({'Date': date, 'P&L': pnl})

    results_df = pd.DataFrame(pnl_list)
    return results_df