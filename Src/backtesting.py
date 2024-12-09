import numpy as np
import pandas as pd
import yfinance as yf
import logging

def backtest_strategy(strategy_func, ticker, start_date, end_date):
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
    stock = yf.Ticker(ticker)
    hist = stock.history(start=start_date, end=end_date)
    
    # Initialize results DataFrame
    results = pd.DataFrame(index=hist.index)
    results['Close'] = hist['Close']
    
    # Apply strategy and calculate P&L
    results['P&L'] = strategy_func(results['Close'])
    
    logging.info("Backtesting completed")
    return results