from typing import Tuple

import numpy as np
from numba import njit


def FVG(open_: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray, join_consecutive: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Fair Value Gap (FVG) Indicator.

    A fair value gap is when the previous high is lower than the next low if the current candle is bullish,
    or when the previous low is higher than the next high if the current candle is bearish.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param join_consecutive: bool, optional (default=False)
        If there are multiple FVGs in a row, they will be merged using the highest top and the lowest bottom.

    :return: tuple of numpy.ndarray
        (fvg, top, bottom, mitigated_index)
        - fvg: 1 if bullish FVG, -1 if bearish FVG, nan otherwise
        - top: Top of the fair value gap
        - bottom: Bottom of the fair value gap
        - mitigated_index: Index of the candle that mitigated the FVG
    """
    length = open_.size
    fvg = np.full(length, np.nan)
    top = np.full(length, np.nan)
    bottom = np.full(length, np.nan)

    # Bullish FVG condition: close > open and prev high < next low
    bull_mask = (close[1:-1] > open_[1:-1]) & (high[:-2] < low[2:])
    fvg[1:-1][bull_mask] = 1
    top[1:-1][bull_mask] = low[2:][bull_mask]
    bottom[1:-1][bull_mask] = high[:-2][bull_mask]

    # Bearish FVG condition: close < open and prev low > next high
    bear_mask = (close[1:-1] < open_[1:-1]) & (low[:-2] > high[2:])
    fvg[1:-1][bear_mask] = -1
    top[1:-1][bear_mask] = low[:-2][bear_mask]
    bottom[1:-1][bear_mask] = high[2:][bear_mask]

    if join_consecutive:
        fvg, top, bottom = _join_consecutive(fvg, top, bottom)

    mitigated_index = _compute_mitigation_indices(fvg, top, bottom, low, high)

    return fvg, top, bottom, mitigated_index


@njit
def _join_consecutive(fvg, top, bottom):
    for i in range(fvg.size - 1):
        if not np.isnan(fvg[i]) and fvg[i] == fvg[i + 1]:
            top[i + 1] = max(top[i], top[i + 1])
            bottom[i + 1] = min(bottom[i], bottom[i + 1])
            fvg[i] = top[i] = bottom[i] = np.nan
    return fvg, top, bottom


@njit
def _compute_mitigation_indices(fvg, top, bottom, low, high):
    length = fvg.size
    mitigated_index = np.full(length, np.nan)

    for i in range(length):
        if np.isnan(fvg[i]):
            continue
        if fvg[i] == 1:
            for j in range(i + 2, length):
                if low[j] <= top[i]:
                    mitigated_index[i] = j
                    break
        elif fvg[i] == -1:
            for j in range(i + 2, length):
                if high[j] >= bottom[i]:
                    mitigated_index[i] = j
                    break
    return mitigated_index
