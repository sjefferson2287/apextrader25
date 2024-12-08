import json
import yfinance as yf
import pandas as pd

def load_config(config_file='config.json'):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

def fetch_option_chain(ticker, expiration):
    stock = yf.Ticker(ticker)
    options = stock.option_chain(expiration)
    calls = options.calls
    puts = options.puts
    calls['optionType'] = 'call'
    puts['optionType'] = 'put'
    options_df = pd.concat([calls, puts], ignore_index=True)
    return options_df

def scan_market(ticker, expiration, config):
    options_df = fetch_option_chain(ticker, expiration)
    high_iv_threshold = config['scanning_parameters']['high_iv_threshold']
    strike_distance = config['scanning_parameters']['strike_distance']
    delta_min = config['scanning_parameters']['greeks']['delta_min']
    delta_max = config['scanning_parameters']['greeks']['delta_max']

    # Filter options based on scanning parameters
    filtered_options = options_df[
        (options_df['impliedVolatility'] > high_iv_threshold) &
        (abs(options_df['strike'] - options_df['lastPrice']) / options_df['lastPrice'] < strike_distance) &
        (options_df['delta'] >= delta_min) &
        (options_df['delta'] <= delta_max)
    ]

    return filtered_options

if __name__ == "__main__":
    config = load_config()
    ticker = config['default_ticker']
    expiration = config['expiration']
    filtered_options = scan_market(ticker, expiration, config)
    print(filtered_options)