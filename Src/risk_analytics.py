# src/risk_analytics.py
import numpy as np
import pandas as pd
import logging

def calculate_var_historical(returns, confidence_level=0.95):
    """
    Calculate VaR using Historical Simulation.
    """
    if not isinstance(returns, pd.Series):
        returns = pd.Series(returns)
    var = np.percentile(returns, (1 - confidence_level) * 100)
    return var

def calculate_var_parametric(returns, confidence_level=0.95):
    """
    Calculate VaR using Parametric (Variance-Covariance) Method.
    Assumes returns are normally distributed.
    """
    mean = returns.mean()
    std = returns.std()
    var = mean + std * np.percentile(np.random.normal(0, 1, 100000), (1 - confidence_level) * 100)
    return var

def calculate_var(portfolio_returns, confidence_level=0.95, method='historical'):
    """
    Wrapper to choose VaR calculation method.
    """
    if method == 'historical':
        var = calculate_var_historical(portfolio_returns, confidence_level)
    elif method == 'parametric':
        var = calculate_var_parametric(portfolio_returns, confidence_level)
    else:
        logging.warning(f"VaR calculation method {method} not recognized. Defaulting to historical.")
        var = calculate_var_historical(portfolio_returns, confidence_level)
    
    logging.info(f"VaR ({method.capitalize()}) at {confidence_level*100}% confidence level: {var:.2f}")
    return var