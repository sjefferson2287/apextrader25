# src/strategies.py
import numpy as np
import pandas as pd
from typing import Union, List, Tuple

def covered_call(option_chain, K, premium, S_range):
    """
    Implements the covered call strategy.

    Parameters:
        option_chain (pd.DataFrame): The option chain data.
        K (float): The strike price.
        premium (float): The premium received for the call option.
        S_range (np.ndarray): The range of underlying prices to evaluate.

    Returns:
        pd.DataFrame: The results of the covered call strategy.
    """
    # Example implementation (you can customize this based on your strategy)
    results = []
    for S in S_range:
        payoff = min(S, K) + premium - option_chain['Underlying_Price'].iloc[0]
        results.append({'S': S, 'Payoff': payoff})

    return pd.DataFrame(results)

def protective_put(option_chain, K, premium, S_range):
    """
    Implements the protective put strategy.

    Parameters:
        option_chain (pd.DataFrame): The option chain data.
        K (float): The strike price.
        premium (float): The premium paid for the put option.
        S_range (np.ndarray): The range of underlying prices to evaluate.

    Returns:
        pd.DataFrame: The results of the protective put strategy.
    """
    # Example implementation (you can customize this based on your strategy)
    results = []
    for S in S_range:
        payoff = max(S, K) - premium - option_chain['Underlying_Price'].iloc[0]
        results.append({'S': S, 'Payoff': payoff})

    return pd.DataFrame(results)

def iron_condor(option_chain, K, premium, S_range):
    """
    Implements the iron condor strategy.

    Parameters:
        option_chain (pd.DataFrame): The option chain data.
        K (float): The strike price.
        premium (float): The premium received for the iron condor.
        S_range (np.ndarray): The range of underlying prices to evaluate.

    Returns:
        pd.DataFrame: The results of the iron condor strategy.
    """
    # Example implementation (you can customize this based on your strategy)
    results = []
    for S in S_range:
        payoff = min(S, K) + premium - option_chain['Underlying_Price'].iloc[0]
        results.append({'S': S, 'Payoff': payoff})

    return pd.DataFrame(results)