# src/fetch_data.py

import yfinance as yf
import pandas as pd

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
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options

        all_options = []

        for expiration in expirations:
            try:
                # Fetch option chain for each expiration date
                opt = stock.option_chain(expiration)
                calls = opt.calls.copy()
                puts = opt.puts.copy()

                # Add option type and expiration date
                calls['Option_Type'] = 'call'
                puts['Option_Type'] = 'put'
                calls['Expiration'] = expiration
                puts['Expiration'] = expiration

                # Append to the list
                all_options.append(calls)
                all_options.append(puts)
            except Exception as e:
                print(f"Error fetching options for expiration {expiration}: {e}")

        if not all_options:
            print("No options data available.")
            return pd.DataFrame()  # Return empty DataFrame if no data

        # Concatenate all option data into a single DataFrame
        options_df = pd.concat(all_options, ignore_index=True)

        # Convert expiration dates to datetime
        options_df['Expiration'] = pd.to_datetime(options_df['Expiration'])
        options_df['Date'] = pd.to_datetime('today')

        # Calculate time to expiration in years
        options_df['Time_to_Expiration'] = (
            options_df['Expiration'] - options_df['Date']
        ).dt.days / 365

        # Add underlying price
        underlying_price = stock.history(period='1d')['Close'][0]
        options_df['Underlying_Price'] = underlying_price

        # Clean up implied volatility
        options_df['Implied_Volatility'] = options_df['impliedVolatility'].fillna(0)

        return options_df
    except Exception as e:
        print(f"Error fetching option chain for {ticker}: {e}")
        return pd.DataFrame()
