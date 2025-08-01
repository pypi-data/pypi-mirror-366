import numpy as np
from numba import njit
from typing import Tuple

def SWING_HIGHS_LOWS(
    high: np.ndarray,
    low: np.ndarray,
    swing_length: int = 50
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Detects swing highs and swing lows.

    A swing high is the highest high within a window; a swing low is the lowest low within a window.

    :param high: High prices
    :param low: Low prices
    :param swing_length: Number of candles (total) to look for highs/lows
SWING_HIGHS_LOWS
    :return: Tuple (high_low, level)
        high_low: 1 for swing high, -1 for swing low, NaN otherwise
        level: The high/low value at each swing point
    """
    size = high.size
    half = swing_length // 2
    high_low = np.full(size, np.nan)
    level = np.full(size, np.nan)

    for i in range(half, size - half):
        win_high = high[i - half:i + half + 1]
        win_low = low[i - half:i + half + 1]

        if high[i] == np.max(win_high):
            high_low[i] = 1
            level[i] = high[i]
        elif low[i] == np.min(win_low):
            high_low[i] = -1
            level[i] = low[i]

    return _clean_swings(high_low, high, low, level)

@njit
def _clean_swings(high_low, high, low, level):
    changed = True

    while changed:
        changed = False
        idx = np.where(~np.isnan(high_low))[0]

        for i in range(len(idx) - 1):
            a, b = idx[i], idx[i + 1]
            if high_low[a] == high_low[b]:
                if high_low[a] == 1:
                    if high[a] < high[b]:
                        high_low[a] = level[a] = np.nan
                    else:
                        high_low[b] = level[b] = np.nan
                    changed = True
                elif high_low[a] == -1:
                    if low[a] > low[b]:
                        high_low[a] = level[a] = np.nan
                    else:
                        high_low[b] = level[b] = np.nan
                    changed = True

    # Ensure start/end have alternating values
    idx = np.where(~np.isnan(high_low))[0]
    if idx.size > 0:
        high_low[0] = -high_low[idx[0]]
        level[0] = low[0] if high_low[0] == -1 else high[0]

        high_low[-1] = -high_low[idx[-1]]
        level[-1] = low[-1] if high_low[-1] == -1 else high[-1]

    return high_low, level
