import pandas as pd

from xno.timeseries._internal import _call_func
import numpy as np


@_call_func
def AD(high, low, close, volume):
    """
    Accumulation/Distribution Line.

    Calculates the Accumulation/Distribution Line based on high, low, close prices and volume.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param volume: array-like
        Array of trading volumes.

    :return: numpy.ndarray
        Accumulation/Distribution Line values.
    """
    pass

@_call_func
def ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10):
    """
    Chaikin A/D Oscillator.

    Calculates the Chaikin A/D Oscillator based on high, low, close prices and volume.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param volume: array-like
        Array of trading volumes.
    :param fastperiod: int, optional (default=3)
        Fast period for the oscillator calculation.
    :param slowperiod: int, optional (default=10)
        Slow period for the oscillator calculation.

    :return: numpy.ndarray
        Chaikin A/D Oscillator values.
    """
    pass

@_call_func
def OBV(close, volume):
    """
    On-Balance Volume (OBV).

    Calculates the On-Balance Volume based on closing prices and volume.

    :param close: array-like
        Array of closing prices.
    :param volume: array-like
        Array of trading volumes.

    :return: numpy.ndarray
        On-Balance Volume values.
    """
    pass


def VWAP(high, low, close, volume):
    """
    Volume Weighted Average Price (VWAP).

    Calculates the Volume Weighted Average Price based on high, low, close prices and volume.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param volume: array-like
        Array of trading volumes.

    :return: numpy.ndarray
        Volume Weighted Average Price values.
    """
    if isinstance(high, pd.Series):
        high = high.values
    if isinstance(low, pd.Series):
        low = low.values
    if isinstance(close, pd.Series):
        close = close.values
    if isinstance(volume, pd.Series):
        volume = volume.values
    # Ensure all inputs are numpy arrays
    high = np.asarray(high, dtype=np.float64)
    low = np.asarray(low, dtype=np.float64)
    close = np.asarray(close, dtype=np.float64)
    volume = np.asarray(volume, dtype=np.float64)
    # Calculate typical price
    typical_price = (high + low + close) / 3.0
    return np.cumsum(typical_price * volume) / np.cumsum(volume)

def ROLLING_VWAP(high, low, close, volume, window):
    """
    Rolling Volume Weighted Average Price (VWAP).
    """
    # Corrected isinstance checks
    if isinstance(high, pd.Series):
        high = high.values
    if isinstance(low, pd.Series):
        low = low.values
    if isinstance(close, pd.Series):
        close = close.values
    if isinstance(volume, pd.Series):
        volume = volume.values

    # Ensure all inputs are NumPy arrays
    high = np.asarray(high, dtype=np.float64)
    low = np.asarray(low, dtype=np.float64)
    close = np.asarray(close, dtype=np.float64)
    volume = np.asarray(volume, dtype=np.float64)

    # Validate window size
    if window <= 0:
        raise ValueError("Window size must be positive")

    # Calculate typical price
    typical_price = (high + low + close) / 3.0

    # Calculate weighted price
    weighted_price = typical_price * volume

    # Calculate cumulative sums
    cumsum_weighted = np.cumsum(weighted_price)
    cumsum_volume = np.cumsum(volume)

    # Initialize rolling sums
    n = len(high)
    rolling_sum_weighted = np.zeros(n)
    rolling_sum_volume = np.zeros(n)

    # Set rolling sums
    rolling_sum_weighted[:window] = cumsum_weighted[:window]
    rolling_sum_volume[:window] = cumsum_volume[:window]
    if window < n:
        rolling_sum_weighted[window:] = cumsum_weighted[window:] - cumsum_weighted[:-window]
        rolling_sum_volume[window:] = cumsum_volume[window:] - cumsum_volume[:-window]

    # Calculate rolling VWAP, handling zero volume
    rolling_vwap = np.where(rolling_sum_volume != 0, rolling_sum_weighted / rolling_sum_volume, np.nan)

    return rolling_vwap
