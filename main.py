# main.py
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
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from fetch_data import fetch_option_chain, fetch_option_market_data
from black_scholes import black_scholes
from greeks import calculate_greeks
from strategies import covered_call, protective_put, iron_condor
from visualization import plot_pnl
from backtesting import backtest_strategy
from stress_testing import stress_test
from indicators import compute_rsi, compute_bollinger_bands, compute_iv_hv_ratio
from market_scanner import scan_market, load_config
from sentiment_analysis import analyze_sentiment, aggregate_sentiment
from fetch_news import fetch_headlines
from data_augmentation import add_noise, scale_data, time_shift
from feature_selection import select_features
from risk_analytics import calculate_var

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('option_insight.log'),
        logging.StreamHandler()
    ]
)

def parse_arguments():
    parser = argparse.ArgumentParser(description='OptionInsight CLI')
    parser.add_argument('--ticker', type=str, default='AAPL',
                      help='Stock ticker symbol')
    parser.add_argument('--strategy', type=str, 
                      choices=['covered_call', 'protective_put', 'iron_condor'],
                      default='covered_call',
                      help='Option strategy to analyze')
    parser.add_argument('--expiration', type=str,
                      help='Option expiration date (YYYY-MM-DD)')
    return parser.parse_args()

def main():
    args = parse_arguments()
    logging.info(f"Starting OptionInsight application with ticker={args.ticker}, strategy={args.strategy}")
    
    try:
        config = load_config()
        ticker = args.ticker or config['default_ticker']
        expiration = args.expiration or config['expiration']
        
        # Define output directory
        output_dir = Path('output')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get current stock price
        stock = yf.Ticker(ticker)
        S = stock.history(period='1d')['Close'].iloc[-1]
        
        # Strategy Simulation
        K = S * 1.05  # Strike price 5% above current price
        T = 30/365.0  # 30-day expiration
        sigma = 0.2   # Default volatility if not available
        
        bs_price = black_scholes(S, K, T, 0.01, sigma, 'call')
        premium = bs_price
        S_range = np.linspace(S * 0.8, S * 1.2, 100)
        
        # Covered Call simulation
        pnl_cc = covered_call(S, K, premium, S_range)
        plot_pnl(S_range, pnl_cc, 'Covered Call Strategy P&L', output_dir / 'covered_call_pnl.png')
        logging.info("P&L plot saved")
        
        # Example: Augmenting stock price data
        augmented_S = add_noise(S)
        logging.info(f"Augmented stock price: {augmented_S:.2f}")

        # Apply augmentation to S_range
        S_range_augmented = add_noise(S_range)
        # Proceed with strategy simulation using S_range_augmented if desired
        pnl_cc_aug = covered_call(S, K, premium, S_range_augmented)
        plot_pnl(S_range_augmented, pnl_cc_aug, 'Covered Call Strategy P&L (Augmented)', output_dir / 'covered_call_pnl_aug.png')
        logging.info("Augmented P&L plot saved")
        
        # Backtesting
        backtest_results = backtest_strategy(covered_call, ticker, '2021-01-01', '2021-12-31')
        backtest_results.to_csv(output_dir / 'backtest_results.csv', index=False)
        logging.info("Backtest completed and results exported")
        
        # Example: Calculate VaR based on backtest results
        # Assuming 'P&L' column exists
        portfolio_returns = backtest_results['P&L']
        var = calculate_var(portfolio_returns, confidence_level=0.95, method='historical')
        logging.info(f"Value at Risk (VaR) at 95% confidence level: {var:.2f}")

        # Optionally, save VaR to CSV
        var_df = pd.DataFrame({'VaR_95_confidence': [var]})
        var_df.to_csv(output_dir / 'var_analysis.csv', index=False)
        logging.info("VaR analysis exported")
        
        # Stress Testing
        shocks = [-0.2, -0.1, 0, 0.1, 0.2]
        stress_results = stress_test(covered_call, S, K, premium, shocks)
        stress_results.to_csv(output_dir / 'stress_test_results.csv', index=False)
        logging.info("Stress test completed and results exported")
        
        # Market Scanning with debug logging
        logging.debug("Starting market scan...")
        filtered_options = scan_market(ticker, expiration, config)
        if len(filtered_options) == 0:
            logging.warning("No options met the filtering criteria. Consider adjusting parameters.")
        else:
            filtered_options.to_csv(output_dir / 'filtered_options.csv', index=False)
            logging.info(f"Found {len(filtered_options)} matching options")

        # Example: Selecting features for backtesting
        options_df = scan_market(ticker, expiration, config)
        if not options_df.empty:
            features = options_df.drop(['contractSymbol', 'lastTradeDate', 'optionType', 'expiration'], axis=1)
            target = features['lastPrice']  # Example target
            selected_features = select_features(features.drop('lastPrice', axis=1), target, method='mutual_info', threshold=0.05)
            logging.info(f"Features selected for analysis: {selected_features}")
            # Proceed with analysis using selected_features
        else:
            logging.warning("No options to analyze for feature selection.")

        # Fetch and Analyze News
        logging.debug("Fetching latest news headlines...")
        headlines = fetch_headlines(news_api_key, query=ticker)
        sentiments = [analyze_sentiment(headline) for headline in headlines]
        average_sentiment = aggregate_sentiment(sentiments)
        logging.info(f"Average sentiment for {ticker}: {average_sentiment:.2f}")

        # Optionally, save sentiment scores
        sentiment_df = pd.DataFrame(sentiments)
        sentiment_df.to_csv(output_dir / 'sentiment_scores.csv', index=False)
        logging.info("Sentiment scores exported")

    except Exception as e:
        logging.error(f"Critical error in main: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()