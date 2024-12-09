# src/feature_selection.py
from sklearn.feature_selection import mutual_info_regression
import pandas as pd
import logging

def select_features(data, target, method='mutual_info', threshold=0.1):
    """Select features based on the specified method."""
    # Ensure only numeric columns are used
    numeric_data = data.select_dtypes(include=[float, int])
    
    if method == 'mutual_info':
        mi = mutual_info_regression(numeric_data, target)
        feature_scores = pd.Series(mi, index=numeric_data.columns)
        selected_features = feature_scores[feature_scores > threshold].index.tolist()
        logging.info(f"Selected features based on mutual information: {selected_features}")
        return selected_features
    elif method == 'correlation':
        correlation_matrix = numeric_data.corr()
        high_corr = correlation_matrix['target'].abs() > threshold
        selected_features = correlation_matrix.columns[high_corr].tolist()
        logging.info(f"Selected features based on correlation: {selected_features}")
        return selected_features
    else:
        logging.warning(f"Feature selection method {method} not recognized.")
        return numeric_data.columns.tolist()