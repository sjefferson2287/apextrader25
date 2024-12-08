# src/strategies.py
import numpy as np
from typing import Union, List, Tuple

def covered_call(S: float, K: float, premium: float, 
                S_range: Union[List[float], np.ndarray]) -> np.ndarray:
    """
    Calculate P&L for a covered call strategy using vectorized operations.

    Parameters:
    S (float): Current stock price
    K (float): Strike price of the call option
    premium (float): Premium received from selling the call option
    S_range (array-like): Range of stock prices at expiration

    Returns:
    np.ndarray: P&L values corresponding to the stock prices in S_range
    """
    # Convert input to numpy array
    S_range = np.asarray(S_range).reshape(-1)
    print(f"Debug - S_range shape: {S_range.shape}")  # Debug statement

    # Vectorized calculations
    stock_profit = S_range - S
    option_loss = np.maximum(0, S_range - K)
    total_pnl = stock_profit - option_loss + premium

    return total_pnl

def protective_put(S: float, K: float, premium: float, 
                  S_range: Union[List[float], np.ndarray]) -> np.ndarray:
    """
    Calculate P&L for a protective put strategy using vectorized operations.

    Parameters:
    S (float): Current stock price
    K (float): Strike price of the put option
    premium (float): Premium paid for buying the put option
    S_range (array-like): Range of stock prices at expiration

    Returns:
    np.ndarray: P&L values corresponding to the stock prices in S_range
    """
    # Convert input to numpy array
    S_range = np.asarray(S_range)
    
    # Vectorized calculations
    stock_profit = S_range - S
    option_profit = np.maximum(0, K - S_range)
    total_pnl = stock_profit + option_profit - premium
    
    return total_pnl

def iron_condor(S: float, K1: float, K2: float, K3: float, K4: float, 
                premium_received: float, S_range: Union[List[float], np.ndarray]) -> np.ndarray:
    """
    Calculate P&L for an iron condor strategy using vectorized operations.

    Parameters:
    S (float): Current stock price
    K1, K2, K3, K4 (float): Strike prices (K1 < K2 < K3 < K4)
    premium_received (float): Net premium received from selling the spreads
    S_range (array-like): Range of stock prices at expiration

    Returns:
    np.ndarray: P&L values corresponding to the stock prices in S_range
    """
    # Input validation
    if not (K1 < K2 < K3 < K4):
        raise ValueError("Strike prices must satisfy K1 < K2 < K3 < K4")
    
    # Convert input to numpy array
    S_range = np.asarray(S_range)
    
    # Calculate max loss
    max_loss = (K2 - K1) + (K4 - K3) - premium_received
    
    # Initialize array with premium received
    total_pnl = np.full_like(S_range, premium_received)
    
    # Apply conditions using masks
    mask1 = S_range <= K1
    mask2 = (K1 < S_range) & (S_range <= K2)
    mask3 = (K2 < S_range) & (S_range < K3)
    mask4 = (K3 <= S_range) & (S_range < K4)
    mask5 = S_range >= K4
    
    # Calculate P&L for each region
    total_pnl[mask1] = premium_received - max_loss
    total_pnl[mask2] = premium_received - (K2 - S_range[mask2])
    total_pnl[mask3] = premium_received
    total_pnl[mask4] = premium_received - (S_range[mask4] - K3)
    total_pnl[mask5] = premium_received - max_loss
    
    return total_pnl