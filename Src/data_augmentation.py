# src/data_augmentation.py
import numpy as np
import pandas as pd
import logging

def add_noise(data, noise_level=0.01):
    """Add random noise to the data."""
    noise = np.random.normal(0, noise_level, size=data.shape)
    return data + noise

def scale_data(data, scale_factor=1.05):
    """Scale the data by a specific factor."""
    return data * scale_factor

def time_shift(data, shift=1):
    """Shift the data by a number of periods."""
    return data.shift(shift)