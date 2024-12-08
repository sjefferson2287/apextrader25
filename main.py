# main.py

import sys
import os
import json
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import logging
import numpy as np
from datetime import datetime
import yfinance as yf
import pandas as pd

from fetch_data import fetch_option_chain, fetch_option_market_data
from black_scholes import black_scholes
from greeks import calculate_greeks
from strategies import covered_call, protective_put, iron_condor
from visualization import plot_pnl
from backtesting import backtest_strategy
from stress_testing import stress_test
from indicators import compute_rsi, compute_bollinger_bands, compute_iv_hv_ratio
from market_scanner import scan_market, load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('option_insight.log'),
        logging.StreamHandler()
    ]
)

def get_stock_price(ticker: str) -> float:
    """Fetch current stock price with fallback logic."""
    stock = yf.Ticker(ticker)
    stock_info = stock.info
    price = stock_info.get('regularMarketPrice')
    
    if not price:
        hist = stock.history(period='1d')
        if hist.empty:
            raise ValueError(f"No price data available for {ticker}")
        price = hist['Close'].iloc[0]
    
    return float(price)

def calculate_option_metrics(options_df: pd.DataFrame, S: float, r: float) -> pd.DataFrame:
    """Calculate theoretical prices and Greeks for options."""
    for index, row in options_df.iterrows():
        try:
            K = float(row['strike'])
            expiration = datetime.strptime(row['expiration'], '%Y-%m-%d')
            T = max((expiration - datetime.now()).days / 365.0, 0.0001)  # Prevent negative or zero time
            sigma = float(row['impliedVolatility']) if row['impliedVolatility'] > 0 else 0.2
            option_type = str(row['optionType']).lower()

            theo_price = black_scholes(S, K, T, r, sigma, option_type)
            delta, gamma, theta, vega = calculate_greeks(S, K, T, r, sigma)

            options_df.at[index, 'TheoreticalPrice'] = theo_price
            options_df.at[index, 'Delta'] = delta
            options_df.at[index, 'Gamma'] = gamma
            options_df.at[index, 'Theta'] = theta
            options_df.at[index, 'Vega'] = vega
            
        except Exception as e:
            logging.warning(f"Error calculating metrics for option {row}: {str(e)}")
            continue
            
    return options_df

def main() -> None:
    logging.info("Starting OptionInsight application")
    
    try:
        # Load configuration
        config = load_config()
        ticker = config['default_ticker']
        expiration = config['expiration']

        # Fetch stock price
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1y')
        S = hist['Close'].iloc[-1]
        logging.info(f"Current stock price for {ticker}: ${S:.2f}")

        # Compute technical indicators
        rsi = compute_rsi(hist)
        rolling_mean, upper_band, lower_band = compute_bollinger_bands(hist)

        # Fetch and process option data
        options_df = fetch_option_market_data(ticker)
        if options_df.empty:
            raise ValueError(f"No option data available for {ticker}")
        
        logging.info(f"Fetched {len(options_df)} options for {ticker}")

        # Calculate theoretical prices and Greeks
        options_df = calculate_option_metrics(options_df, S, 0.01)
        
        # Identify mispriced options
        options_df['Mispricing'] = options_df['lastPrice'] - options_df['TheoreticalPrice']
        significant_mispricings = options_df[abs(options_df['Mispricing']) > 0.5]
        
        logging.info(f"Found {len(significant_mispricings)} significantly mispriced options")
        
        # Export analysis results
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        options_df.to_csv(output_dir / 'options_analysis.csv', index=False)
        logging.info("Exported options analysis to CSV")

        # Strategy Simulation
        K = S * 1.05  # Strike price 5% above current price
        T = 30/365.0  # 30-day expiration
        sigma = 0.2  # Default volatility if not available
        
        bs_price = black_scholes(S, K, T, 0.01, sigma, 'call')
        premium = bs_price
        S_range = np.linspace(S * 0.8, S * 1.2, 100)
        
        # Covered Call simulation
        pnl_cc = covered_call(S, K, premium, S_range)
        plot_pnl(S_range, pnl_cc, 'Covered Call Strategy P&L', 
                output_dir / 'covered_call_pnl.png')

        # Backtesting
        backtest_results = backtest_strategy(covered_call, ticker, '2021-01-01', '2021-12-31')
        backtest_results.to_csv(output_dir / 'backtest_results.csv', index=False)
        logging.info("Backtest completed and results exported")

        # Stress Testing
        shocks = [-0.2, -0.1, 0, 0.1, 0.2]
        stress_results = stress_test(covered_call, S, K, premium, shocks)
        stress_results.to_csv(output_dir / 'stress_test_results.csv', index=False)
        logging.info("Stress test completed and results exported")

        # Market Scanning
        filtered_options = scan_market(ticker, expiration, config)
        filtered_options.to_csv(output_dir / 'filtered_options.csv', index=False)
        logging.info("Market scanning completed and results exported")

    except Exception as e:
        logging.error(f"Critical error in main: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()