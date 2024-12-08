# src/fetch_data.py

import yfinance as yf
import pandas as pd

def fetch_option_chain(ticker):
    """
    Fetches the complete option chain for the given ticker symbol.

    Parameters:
        ticker (str): The stock ticker symbol.

    Returns:
        pandas.DataFrame: The option chain data with calls and puts.
    """
    stock = yf.Ticker(ticker)
    expirations = stock.options

    all_options = []

    for expiration in expirations:
        # Fetch option chain for each expiration date
        opt = stock.option_chain(expiration)
        calls = opt.calls.copy()
        puts = opt.puts.copy()

        # Add option type and expiration date
        calls['optionType'] = 'call'
        puts['optionType'] = 'put'
        calls['expiration'] = expiration
        puts['expiration'] = expiration

        # Append to the list
        all_options.append(calls)
        all_options.append(puts)

    # Concatenate all option data into a single DataFrame
    options_df = pd.concat(all_options, ignore_index=True)
    return options_df

def fetch_option_market_data(ticker):
    """
    Fetches option chain with market data for the given ticker symbol.

    Parameters:
        ticker (str): The stock ticker symbol.

    Returns:
        pandas.DataFrame: Option chain including market prices.
    """
    options_df = fetch_option_chain(ticker)
    return options_df