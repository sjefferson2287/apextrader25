# src/visualization.py

import logging
from typing import Union, List
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

def plot_pnl(
    S_range: np.ndarray,
    pnl: Union[np.ndarray, List[np.ndarray]],
    title: str,
    filename: Union[str, Path] = 'pnl_plot.png',
    labels: List[str] = None,
    show_breakeven: bool = True
) -> None:
    """
    Plots the P&L of one or multiple strategies and saves to file.

    Parameters:
    -----------
    S_range : np.ndarray
        Range of stock prices at expiration
    pnl : Union[np.ndarray, List[np.ndarray]]
        Single or multiple P&L arrays corresponding to S_range
    title : str
        Title of the plot
    filename : Union[str, Path]
        Filename to save the plot
    labels : List[str], optional
        Labels for multiple strategies
    show_breakeven : bool, optional
        Whether to show breakeven points

    Returns:
    --------
    None
    """
    try:
        # Input validation
        if not isinstance(S_range, (list, np.ndarray)):
            raise TypeError("S_range must be array-like")
        
        # Convert to numpy arrays if needed
        S_range = np.asarray(S_range)
        if isinstance(pnl, list):
            pnl = [np.asarray(p) for p in pnl]
        else:
            pnl = [np.asarray(pnl)]
            
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot each strategy
        if labels is None:
            labels = [f'Strategy {i+1}' for i in range(len(pnl))]
            
        for p, label in zip(pnl, labels):
            ax.plot(S_range, p, label=label, linewidth=2)
            
            # Add breakeven points if requested
            if show_breakeven:
                breakeven_points = S_range[np.where(np.diff(np.signbit(p)))[0]]
                if len(breakeven_points) > 0:
                    ax.scatter(
                        breakeven_points,
                        np.zeros_like(breakeven_points),
                        color='red', 
                        marker='o',
                        label=f'{label} Breakeven'
                    )
        
        # Customize plot
        ax.set_xlabel('Stock Price at Expiration', fontsize=12)
        ax.set_ylabel('Profit/Loss (P&L)', fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.axhline(0, color='black', linewidth=1, linestyle='--')
        ax.legend(fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # Save the plot
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        plt.savefig(output_path, dpi=300)
        logging.info(f"P&L plot saved as: {filename}")
        
        # Show the plot (optional)
        plt.show()
    except Exception as e:
        logging.error(f"Error in plot_pnl: {e}")
        raise e
    finally:
        # Close the plot to free resources
        plt.close(fig)  # Prevent memory leaks
