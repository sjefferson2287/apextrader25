import argparse
import logging
import os
import sys
from pathlib import Path
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Add src directory to Python path
current_dir = Path(__file__).resolve().parent
src_path = current_dir / 'src'
sys.path.append(str(src_path))

# Ensure logs directory exists
logs_dir = current_dir / 'logs'
if not logs_dir.exists():
    logs_dir.mkdir()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO in production
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'option_insight.log'),
        logging.StreamHandler()
    ]
)

# Import local modules
try:
    from fetch_data import fetch_option_chain  # Corrected import
    from black_scholes import black_scholes
    from greeks import calculate_greeks
    from strategies import covered_call, protective_put, iron_condor
    from binomial_tree import binomial_tree_option_price
except ImportError as e:
    logging.error(f"Import error: {e}", exc_info=True)
    sys.exit(1)

def identify_mispriced_options(option_chain):
    """
    Identify mispriced options by comparing theoretical prices with market prices.
    """
    mispriced_options = option_chain[(option_chain['BT_Price'] - option_chain['lastPrice']).abs() > 1.0]
    if not mispriced_options.empty:
        logging.info(f"Mispriced options found:\n{mispriced_options[['contractSymbol', 'lastPrice', 'BT_Price']]}")
    else:
        logging.info("No mispriced options found.")
    return mispriced_options

def main():
    # Parsing command-line arguments
    parser = argparse.ArgumentParser(description='OptionInsight CLI')
    parser.add_argument('--symbols', nargs='+', type=str, default=['AAPL'],
                        help='List of stock symbols')
    parser.add_argument('--strategy', type=str,
                        choices=['covered_call', 'protective_put', 'iron_condor'],
                        default='covered_call',
                        help='Option strategy to analyze')
    parser.add_argument('--expiration', type=str,
                        help='Option expiration date (YYYY-MM-DD)')  # This argument is no longer used
    args = parser.parse_args()

    symbols = args.symbols
    strategy = args.strategy
    # expiration = args.expiration # No longer used

    option_chains = []
    for symbol in symbols:
        try:
            # Use the correct fetch_option_chain function from fetch_data.py
            option_chain = fetch_option_chain(symbol)
            if not option_chain.empty:
                option_chains.append(option_chain)
            else:
                logging.warning(f"No option data fetched for {symbol}. Skipping.")
        except Exception as e:
            logging.error(f"Failed to fetch data for {symbol}: {e}", exc_info=True)
            # Decide whether to continue or exit.  For now, skip.
            continue

    if not option_chains:
        logging.error("No option data fetched for any symbol. Exiting.")
        sys.exit(1)

    option_chain = pd.concat(option_chains, ignore_index=True)


    # Ensure required columns are present
    required_columns = ['Underlying_Price', 'strike', 'Time_to_Expiration', 'impliedVolatility', 'Option_Type']
    for col in required_columns:
        if col not in option_chain.columns:
            logging.error(f"Missing required column: {col}")
            sys.exit(1)

    # Convert data types as necessary
    try:
        numeric_columns = ['Underlying_Price', 'strike', 'Time_to_Expiration', 'impliedVolatility']
        option_chain[numeric_columns] = option_chain[numeric_columns].apply(pd.to_numeric, errors='coerce')
    except Exception as e:
        logging.error(f"Error converting data types: {e}", exc_info=True)
        sys.exit(1)

    # Check for missing or invalid data
    if option_chain[numeric_columns].isnull().any().any():
        logging.error("Missing or invalid data detected in numeric columns.")
        logging.debug(f"Data with missing values:\n{option_chain[option_chain[numeric_columns].isnull().any(axis=1)]}")
        sys.exit(1)


    # Calculate Binomial Tree prices
    option_chain['BT_Price'] = option_chain.apply(lambda row: binomial_tree_option_price(
        S=row['Underlying_Price'],
        K=row['strike'],
        T=row['Time_to_Expiration'],
        r=0.01,  # risk-free rate
        sigma=row['impliedVolatility'],
        N=100,  # You can adjust the number of steps
        option_type=row['Option_Type'].lower(),
        american=True # Use True for American options, False for European
    ), axis=1)
    logging.info("Binomial Tree prices calculated")

    # Calculate Greeks
    option_chain[['Delta', 'Gamma', 'Theta', 'Vega', 'Rho']] = option_chain.apply(lambda row: calculate_greeks(
        S=row['Underlying_Price'],
        K=row['strike'],
        T=row['Time_to_Expiration'],
        r=0.01,  # risk-free rate
        sigma=row['impliedVolatility']
    ), axis=1, result_type='expand')
    logging.info("Greeks calculated")

    # print option_chain
    logging.info(f"Option chain sample:\n{option_chain.head()}")

    # Identify mispriced options
    mispriced_options = identify_mispriced_options(option_chain)


    # Define additional parameters for strategies (placeholders, not yet used)
    K = option_chain['strike'].iloc[0]
    premium = option_chain['lastPrice'].iloc[0]
    S_range = np.linspace(option_chain['Underlying_Price'].min(), option_chain['Underlying_Price'].max(), 100)

    # Apply the selected strategy (placeholders for now)
    if strategy == 'covered_call':
        strategies_result = covered_call(option_chain, K, premium, S_range)
        logging.info("Covered Call strategy applied")
    elif strategy == 'protective_put':
        strategies_result = protective_put(option_chain, K, premium, S_range)
        logging.info("Protective Put strategy applied")
    elif strategy == 'iron_condor':
        strategies_result = iron_condor(option_chain, K, premium, S_range)
        logging.info("Iron Condor strategy applied")



    # Save the processed data
    option_chain.to_csv('output/options_analysis.csv', index=False)
    logging.info("Option analysis data exported")



if __name__ == "__main__":
    main()
