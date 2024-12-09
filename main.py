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

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO in production
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/option_insight.log'),
        logging.StreamHandler()
    ]
)

# Import local modules
try:
    from fetch_data import fetch_option_chain
    from black_scholes import black_scholes
    from greeks import calculate_greeks
    from strategies import covered_call, protective_put, iron_condor
except ImportError as e:
    logging.error(f"Import error: {e}", exc_info=True)
    sys.exit(1)

def main():
    try:
        logging.info("Starting Option Insight application")

        # Parse command-line arguments
        parser = argparse.ArgumentParser(description='OptionInsight CLI')
        parser.add_argument('--symbol', type=str, default='AAPL',
                            help='Stock symbol')
        parser.add_argument('--strategy', type=str, 
                            choices=['covered_call', 'protective_put', 'iron_condor'],
                            default='covered_call',
                            help='Option strategy to analyze')
        parser.add_argument('--expiration', type=str,
                            help='Option expiration date (YYYY-MM-DD)')
        args = parser.parse_args()

        symbol = args.symbol
        strategy = args.strategy
        expiration = args.expiration

        logging.info(f"Fetching data for symbol: {symbol}")

        # Fetch option chain data
        option_chain = fetch_option_chain(symbol)
        logging.info("Option chain fetched")

        if option_chain.empty:
            logging.error("No option data fetched. Exiting.")
            sys.exit(1)

        # Inspect the DataFrame
        logging.debug(f"Option chain columns: {option_chain.columns}")
        logging.debug(f"Option chain sample:\n{option_chain.head()}")

        # Ensure required columns are present
        required_columns = ['Underlying_Price', 'strike', 'Time_to_Expiration', 'Implied_Volatility', 'Option_Type']
        for col in required_columns:
            if col not in option_chain.columns:
                logging.error(f"Missing required column: {col}")
                sys.exit(1)

        # Convert data types as necessary
        try:
            numeric_columns = ['Underlying_Price', 'strike', 'Time_to_Expiration', 'Implied_Volatility']
            option_chain[numeric_columns] = option_chain[numeric_columns].apply(pd.to_numeric, errors='coerce')
        except Exception as e:
            logging.error(f"Error converting data types: {e}", exc_info=True)
            sys.exit(1)

        # Check for missing or invalid data
        if option_chain[numeric_columns].isnull().any().any():
            logging.error("Missing or invalid data detected in numeric columns.")
            logging.debug(f"Data with missing values:\n{option_chain[option_chain[numeric_columns].isnull().any(axis=1)]}")
            sys.exit(1)

        # Calculate Black-Scholes prices
        option_chain['BS_Price'] = option_chain.apply(lambda row: black_scholes(
            S=row['Underlying_Price'],
            K=row['strike'],  # Adjusted column name
            T=row['Time_to_Expiration'],
            r=0.01,  # risk-free rate
            sigma=row['Implied_Volatility'],
            option_type=row['Option_Type']
        ), axis=1)
        logging.info("Black-Scholes prices calculated")

        # Calculate Greeks
        try:
            greeks = option_chain.apply(
                lambda row: pd.Series(calculate_greeks(
                    S=row['Underlying_Price'],
                    K=row['strike'],
                    T=row['Time_to_Expiration'],
                    r=0.01,  # Risk-free rate
                    sigma=row['Implied_Volatility']
                )),
                axis=1
            )
            option_chain[['Delta', 'Gamma', 'Theta', 'Vega']] = greeks
            logging.info("Greeks calculated successfully")
        except Exception as e:
            logging.error(f"Error calculating Greeks: {e}", exc_info=True)
            sys.exit(1)

        # Apply the selected strategy
        try:
            if strategy == 'covered_call':
                strategies_result = covered_call(option_chain)
                logging.info("Covered Call strategy applied")
            elif strategy == 'protective_put':
                strategies_result = protective_put(option_chain)
                logging.info("Protective Put strategy applied")
            elif strategy == 'iron_condor':
                strategies_result = iron_condor(option_chain)
                logging.info("Iron Condor strategy applied")
        except Exception as e:
            logging.error(f"Error applying strategy {strategy}: {e}", exc_info=True)
            sys.exit(1)

        # Save the processed data
        output_file = 'output/options_analysis.csv'
        option_chain.to_csv(output_file, index=False)
        logging.info(f"Option analysis data exported to {output_file}")

    except Exception as e:
        logging.error(f"Critical error in main: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
