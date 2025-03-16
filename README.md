# OptionInsight

## Project Overview

OptionInsight is a Python-based tool for analyzing, backtesting, and simulating options trading strategies. It leverages the Black-Scholes model, Binomial Tree model, historical data from yfinance, and customizable strategies to identify profitable opportunities and visualize performance.

## Key Features

*   **Option Chain Retrieval:** Fetches option chain data from yfinance.
*   **Black-Scholes Model:** Calculates theoretical option prices using the Black-Scholes model.
*   **Binomial Tree Pricing:** Calculates theoretical option prices using the Binomial Tree model.
*   **Option Greeks Calculation:** Calculates Delta, Gamma, Theta, Vega, and Rho for options.
*   **Strategy Backtesting:** Backtests various option strategies using historical data.
*   **Profit/Loss Simulation:** Simulates profit and loss for different option strategies.
*   **Mispricing Identification:** Identifies potentially mispriced options.
*   **Stress Testing:** Evaluates strategy robustness under extreme market conditions.
*   **Data Export:** Exports processed data and backtest results to CSV for offline analysis.

## Core Functionalities

*   **Option Chain Retrieval:** Retrieves option chain data using yfinance and consolidates call and put options into one DataFrame for ease of analysis.
*   **Black-Scholes Pricing:** Calculates option Greeks (Delta, Gamma, Theta, Vega, Rho) using the Black-Scholes model, facilitating sensitivity and risk analysis.
*   **Binomial Tree Pricing:** Calculates theoretical option prices using the Binomial Tree model.
*   **Mispricing Identification:** Flags potentially mispriced options where theoretical and market prices differ, highlighting trading opportunities.
*   **Profit/Loss Simulation:** Models P&L for single options and multi-leg strategies (e.g., covered calls, protective puts, iron condors), visualizing potential outcomes across a range of underlying prices.
*   **Backtesting Framework:** Integrates historical data to simulate past performance of chosen strategies. Currently tested with Covered Calls, Protective Puts, and Iron Condors on multiple tickers (AAPL, MSFT, TSLA, AMZN, SPY). Computes key metrics like Max Profit, Max Loss, Average P&L, and Win Rate.
*   **Stress Testing:** Evaluates strategy robustness under extreme market conditions, assessing performance during large price swings or volatility spikes.
*   **Data Export:** Saves processed data, theoretical prices, Greeks, mispricing flags, and backtest results to CSV for offline analysis.

## Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/sjefferson2287/apextrader25.git
    cd OptionInsight
    ```

2.  Create a virtual environment and install dependencies:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux and macOS
    venv\Scripts\activate  # On Windows
    pip install -r requirements.txt
    ```

## Usage

1.  Run the main script:

    ```bash
    python main.py --symbols AAPL MSFT --strategy covered_call
    ```

    *   `--symbols`: List of stock symbols to analyze (default: AAPL).
    *   `--strategy`: Option strategy to analyze (default: covered\_call). Choices: covered\_call, protective\_put, iron\_condor.

2.  The results will be saved to `output/options_analysis.csv`.

## Configuration

The `config.json` file contains the following configuration parameters:

```json
{
    "default_ticker": "AAPL",
    "expiration": "2024-12-20",
    "news_api_key": "YOUR_NEWS_API_KEY",
    "scanning_parameters": {
        "high_iv_threshold": 0.2,
        "strike_distance": 0.15,
        "iv_hv_ratio_min": 1.0
    }
}
```

*   `default_ticker`: Default stock ticker symbol.
*   `expiration`: Default option expiration date.
*   `news_api_key`: API key for fetching news data (not currently used).
*   `scanning_parameters`: Parameters for option scanning:
    *   `high_iv_threshold`: Threshold for high implied volatility.
    *   `strike_distance`: Distance from the current price for strikes to consider.
    *   `iv_hv_ratio_min`: Minimum ratio of implied volatility to historical volatility.

## Directory Structure

```
OptionInsight/
├── logs/                  # Log files (contains option_insight.log)
├── output/                # Output files (contains CSV and PNG files)
├── src/                   # Python modules
│   ├── __init__.py
│   ├── backtesting.py     # Backtesting logic
│   ├── binomial_tree.py   # Binomial tree option pricing
│   ├── black_scholes.py   # Black-Scholes calculations
│   ├── data_augmentation.py# Data augmentation techniques
│   ├── feature_selection.py# Feature selection methods
│   ├── fetch_data.py      # Data retrieval (yfinance)
│   ├── fetch_news.py      # Fetching news data
│   ├── greeks.py          # Option Greeks calculations
│   ├── indicators.py      # Technical indicators
│   ├── market_scanner.py  # Market scanning logic
│   ├── risk_analytics.py  # Risk analysis tools
│   ├── sentiment_analysis.py # Sentiment analysis of news
│   ├── setup.py           # Setup and configuration
│   ├── strategies.py      # Implementations of strategies (covered calls, etc.)
│   ├── stress_testing.py  # Stress test simulations
│   ├── utils.py           # Helper functions
│   └── visualization.py   # Plotting, reporting
│
├── Test/                  # Unit and integration tests
│   └── test_black_scholes.py
│
├── main.py                # Main entry point for execution
├── README.md              # Project overview (this document)
└── requirements.txt       # Python dependencies
```

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with descriptive commit messages.
4.  Submit a pull request.

## License

[Specify the license here]
