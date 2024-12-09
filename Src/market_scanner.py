# src/market_scanner.py
import json
import os
import numpy as np
import yfinance as yf
import pandas as pd
import logging
from datetime import datetime

def load_config(config_file='config.json'):
    """Load configuration from JSON file."""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', config_file)
        config_path = os.path.abspath(config_path)
        logging.debug(f"Loading config from: {config_path}")
        with open(config_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        raise

def extract_expiration(symbol):
    """Extract expiration date from option symbol (e.g., AAPL241213C00105000)"""
    try:
        # Get YYMMDD portion
        date_part = symbol[4:10]
        # Convert to datetime then format as YYYY-MM-DD
        date_obj = datetime.strptime(date_part, '%y%m%d')
        return date_obj.strftime('%Y-%m-%d')
    except Exception as e:
        logging.warning(f"Could not extract expiration from {symbol}: {e}")
        return None

def calculate_hv(hist_prices, window=20):
    """Calculate historical volatility"""
    log_returns = np.log(hist_prices / hist_prices.shift(1))
    hv = log_returns.rolling(window).std() * np.sqrt(252)
    return hv

def fetch_option_chain(ticker, expiration):
    """Fetch and prepare option chain data"""
    try:
        stock = yf.Ticker(ticker)
        options = stock.option_chain(expiration)
        
        # Get historical data for HV calculation
        hist = stock.history(period='1y')
        hv = calculate_hv(hist['Close'])
        current_hv = hv.iloc[-1]
        
        # Process calls and puts
        calls = options.calls.copy()
        puts = options.puts.copy()
        
        # Add metadata
        for df in [calls, puts]:
            df['historical_volatility'] = current_hv
            df['iv_hv_ratio'] = df['impliedVolatility'] / current_hv
        
        # Combine and add type labels
        calls['optionType'] = 'call'
        puts['optionType'] = 'put'
        options_df = pd.concat([calls, puts], ignore_index=True)
        
        # Extract expiration from symbols
        options_df['expiration'] = options_df['contractSymbol'].apply(extract_expiration)
        
        logging.debug(f"Fetched options data columns: {options_df.columns}")
        return options_df
        
    except Exception as e:
        logging.error(f"Error fetching options: {e}")
        raise

def scan_market(ticker: str, expiration: str, config: dict) -> pd.DataFrame:
    """Scan market for options meeting criteria"""
    try:
        # Get options data
        options_df = fetch_option_chain(ticker, expiration)
        logging.debug(f"Initial options count: {len(options_df)}")
        
        # Get parameters from config
        params = config.get('scanning_parameters', {})
        iv_threshold = params.get('high_iv_threshold', 0.2)
        strike_dist = params.get('strike_distance', 0.15)
        iv_hv_ratio_min = params.get('iv_hv_ratio_min', 1.0)
        
        # Apply filters with detailed logging
        iv_mask = options_df['impliedVolatility'] > iv_threshold
        strike_mask = (abs(options_df['strike'] - options_df['lastPrice']) / 
                      options_df['lastPrice'] < strike_dist)
        iv_hv_mask = options_df['iv_hv_ratio'] > iv_hv_ratio_min
        
        filtered_df = options_df[iv_mask & strike_mask & iv_hv_mask]
        
        # Log filtering results
        logging.debug(f"Options after IV filter: {iv_mask.sum()}")
        logging.debug(f"Options after strike filter: {strike_mask.sum()}")
        logging.debug(f"Options after IV/HV ratio filter: {iv_hv_mask.sum()}")
        
        logging.info(f"Found {len(filtered_df)} options matching criteria")
        return filtered_df

    except Exception as e:
        logging.error(f"Error in scan_market: {e}", exc_info=True)
        raise