# src/stress_testing.py
import logging
import pandas as pd
import numpy as np

def stress_test(strategy_fn, S, K, premium, shocks):
    """
    Stress test a strategy under different market shocks with enhanced error handling
    and logging.
    """
    logging.info(f"Starting stress test with S={S}, K={K}, premium={premium}")
    results = []
    
    for shock in shocks:
        try:
            # Calculate shocked price
            S_shocked = S * (1 + shock)
            logging.info(f"Testing shock={shock:.2%}, S_shocked={S_shocked:.2f}")
            
            # Run strategy with single price point
            pnl = strategy_fn(S, K, premium, np.array([S_shocked]))
            
            # Handle different return types
            if isinstance(pnl, (list, np.ndarray)):
                pnl = pnl[0]
            elif isinstance(pnl, pd.Series):
                pnl = pnl.iloc[0]
                
            logging.info(f"Calculated PnL={pnl:.2f}")
            results.append({
                'Shock': shock,
                'Shocked_Price': S_shocked,
                'P&L': pnl
            })
            
        except Exception as e:
            logging.error(f"Error processing shock {shock}: {str(e)}")
            raise
            
    return pd.DataFrame(results)