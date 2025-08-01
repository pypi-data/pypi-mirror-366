from typing import Tuple
import numpy as np
import pandas as pd
from numba import njit


def OB(
    open_: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray,
    swing_highs_lows: pd.DataFrame,
    close_mitigation: bool = False,
) -> pd.DataFrame:
    swing = swing_highs_lows["HighLow"].values

    (
        ob,
        top_arr,
        bottom_arr,
        ob_volume,
        mitigated_index,
        percentage,
    ) = _compute_order_blocks(
        open_, high, low, close, volume, swing, close_mitigation
    )

    return pd.DataFrame(
        {
            "OB": ob,
            "Top": top_arr,
            "Bottom": bottom_arr,
            "OBVolume": ob_volume,
            "MitigatedIndex": mitigated_index,
            "Percentage": percentage,
        }
    )


@njit
def _compute_order_blocks(
    open_, high, low, close, volume, swing, close_mitigation: bool
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    size = open_.size

    ob = np.full(size, np.nan)
    top_arr = np.full(size, np.nan)
    bottom_arr = np.full(size, np.nan)
    ob_volume = np.full(size, np.nan)
    mitigated_index = np.full(size, np.nan)
    percentage = np.full(size, np.nan)

    crossed = np.zeros(size, dtype=np.bool_)
    breaker = np.zeros(size, dtype=np.bool_)

    swing_high = np.where(swing == 1)[0]
    swing_low = np.where(swing == -1)[0]

    active_bull = []
    active_bear = []

    for i in range(size):
        # ====================
        # Update active bullish OBs
        for idx in active_bull[:]:
            if breaker[idx]:
                if high[i] > top_arr[idx]:
                    _reset_ob(idx, ob, top_arr, bottom_arr, ob_volume, mitigated_index, percentage)
                    active_bull.remove(idx)
            else:
                if (not close_mitigation and low[i] < bottom_arr[idx]) or (
                    close_mitigation and min(open_[i], close[i]) < bottom_arr[idx]
                ):
                    breaker[idx] = True
                    mitigated_index[idx] = i

        # Detect new bullish OB
        last_high = _last_before(swing_high, i)
        if last_high != -1 and close[i] > high[last_high] and not crossed[last_high]:
            crossed[last_high] = True
            ob_index = _find_min_index(low, last_high + 1, i)
            if ob_index == -1:
                ob_index = i - 1
            bottom = low[ob_index]
            top = high[ob_index]

            ob[ob_index] = 1
            top_arr[ob_index] = top
            bottom_arr[ob_index] = bottom

            v0 = volume[i]
            v1 = volume[i - 1] if i >= 1 else 0.0
            v2 = volume[i - 2] if i >= 2 else 0.0
            ob_volume[ob_index] = v0 + v1 + v2
            low_v = v2
            high_v = v0 + v1
            max_v = max(low_v, high_v)
            percentage[ob_index] = (min(low_v, high_v) / max_v * 100.0) if max_v != 0 else 100.0
            active_bull.append(ob_index)

        # ====================
        # Update active bearish OBs
        for idx in active_bear[:]:
            if breaker[idx]:
                if low[i] < bottom_arr[idx]:
                    _reset_ob(idx, ob, top_arr, bottom_arr, ob_volume, mitigated_index, percentage)
                    active_bear.remove(idx)
            else:
                if (not close_mitigation and high[i] > top_arr[idx]) or (
                    close_mitigation and max(open_[i], close[i]) > top_arr[idx]
                ):
                    breaker[idx] = True
                    mitigated_index[idx] = i

        # Detect new bearish OB
        last_low = _last_before(swing_low, i)
        if last_low != -1 and close[i] < low[last_low] and not crossed[last_low]:
            crossed[last_low] = True
            ob_index = _find_max_index(high, last_low + 1, i)
            if ob_index == -1:
                ob_index = i - 1
            top = high[ob_index]
            bottom = low[ob_index]

            ob[ob_index] = -1
            top_arr[ob_index] = top
            bottom_arr[ob_index] = bottom

            v0 = volume[i]
            v1 = volume[i - 1] if i >= 1 else 0.0
            v2 = volume[i - 2] if i >= 2 else 0.0
            ob_volume[ob_index] = v0 + v1 + v2
            low_v = v0 + v1
            high_v = v2
            max_v = max(low_v, high_v)
            percentage[ob_index] = (min(low_v, high_v) / max_v * 100.0) if max_v != 0 else 100.0
            active_bear.append(ob_index)

    return ob, top_arr, bottom_arr, ob_volume, mitigated_index, percentage


@njit
def _reset_ob(idx, ob, top_arr, bottom_arr, ob_volume, mitigated_index, percentage):
    ob[idx] = np.nan
    top_arr[idx] = np.nan
    bottom_arr[idx] = np.nan
    ob_volume[idx] = np.nan
    mitigated_index[idx] = np.nan
    percentage[idx] = np.nan


@njit
def _last_before(arr: np.ndarray, val: int) -> int:
    # Binary search for last value in arr < val
    left, right = 0, arr.size - 1
    res = -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] < val:
            res = arr[mid]
            left = mid + 1
        else:
            right = mid - 1
    return res


@njit
def _find_min_index(arr: np.ndarray, start: int, end: int) -> int:
    if end <= start:
        return -1
    min_val = arr[start]
    idx = start
    for i in range(start + 1, end):
        if arr[i] <= min_val:
            min_val = arr[i]
            idx = i
    return idx


@njit
def _find_max_index(arr: np.ndarray, start: int, end: int) -> int:
    if end <= start:
        return -1
    max_val = arr[start]
    idx = start
    for i in range(start + 1, end):
        if arr[i] >= max_val:
            max_val = arr[i]
            idx = i
    return idx
