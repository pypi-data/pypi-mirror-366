
import numpy as np
import pandas as pd


def compute_max_dd(x, freq=1000000):
    if np.inf in x or -np.inf in x:
        raise ValueError("Data contains inf values")

    assert isinstance(x, np.ndarray)
    window = freq
    x = pd.DataFrame(x)
    x = np.cumprod(1 + x)
    # Calculate the max drawdown in the past window days for each day in the series.
    # Use min_periods=1 if you want to let the first 252 days data have an expanding window
    roll_max = x.rolling(window, min_periods=1).max()
    dd = x / roll_max - 1.0
    return dd.values


def returns_to_pf_values(returns):
    return np.cumprod(1 + returns) - 1
