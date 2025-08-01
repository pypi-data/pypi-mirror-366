from typing import Tuple
import numpy as np
from numba import njit


def BOS_CHOCH(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    swing_highlow: np.ndarray,
    swing_level: np.ndarray,
    close_break: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Break of Structure (BoS) and Change of Character (CHoCH) Detection.
    Detects break of structure and change of character based on swing highs/lows and levels.
    A BoS occurs when a swing high/low is broken by the price, while a CHoCH indicates a change in market structure.
    The function returns arrays indicating the BoS, CHoCH, level of the swing, and the index of the break.
    :param high:
    :param low:
    :param close:
    :param swing_highlow:
    :param swing_level:
    :param close_break:
    :return:
    """
    bos, choch, level = _detect_bos_choch_core(swing_highlow, swing_level)

    broken = _detect_breaks(
        bos, choch,
        close if close_break else high,
        close if close_break else low,
        level,
    )

    valid = broken != -1
    bos = np.where(valid, bos, np.nan)
    choch = np.where(valid, choch, np.nan)
    level = np.where(valid, level, np.nan)
    broken = np.where(valid, broken, np.nan)

    return bos, choch, level, broken


@njit
def _detect_bos_choch_core(highlow: np.ndarray, level: np.ndarray):
    size = highlow.size
    bos = np.zeros(size, dtype=np.float32)
    choch = np.zeros(size, dtype=np.float32)
    lvl = np.zeros(size, dtype=np.float32)

    levels = np.empty(4, dtype=np.float32)
    types = np.empty(4, dtype=np.int8)
    last_positions = np.empty(4, dtype=np.int32)
    count = 0

    for i in range(size):
        if not np.isnan(highlow[i]):
            if count < 4:
                levels[count] = level[i]
                types[count] = highlow[i]
                last_positions[count] = i
                count += 1
            else:
                levels[:-1] = levels[1:]
                levels[-1] = level[i]
                types[:-1] = types[1:]
                types[-1] = highlow[i]
                last_positions[:-1] = last_positions[1:]
                last_positions[-1] = i

            if count == 4:
                a, b, c, d = types
                la, lb, lc, ld = levels
                idx = last_positions[2]

                # bullish BOS
                if a == -1 and b == 1 and c == -1 and d == 1:
                    if la < lc < lb < ld:
                        bos[idx] = 1
                        lvl[idx] = lc

                # bearish BOS
                elif a == 1 and b == -1 and c == 1 and d == -1:
                    if la > lc > lb > ld:
                        bos[idx] = -1
                        lvl[idx] = lc

                # bullish CHoCH
                if a == -1 and b == 1 and c == -1 and d == 1:
                    if ld > lb > la > lc:
                        choch[idx] = 1
                        lvl[idx] = lc

                # bearish CHoCH
                elif a == 1 and b == -1 and c == 1 and d == -1:
                    if ld < lb < la < lc:
                        choch[idx] = -1
                        lvl[idx] = lc

    return bos, choch, lvl


@njit
def _detect_breaks(
    bos: np.ndarray,
    choch: np.ndarray,
    bull: np.ndarray,
    bear: np.ndarray,
    level: np.ndarray,
) -> np.ndarray:
    size = bos.size
    broken = np.full(size, -1, dtype=np.int32)
    indices = np.where((bos != 0) | (choch != 0))[0]

    for idx in indices:
        lvl = level[idx]
        src = bull if (bos[idx] == 1 or choch[idx] == 1) else bear
        op = src[idx + 2:] > lvl if (bos[idx] == 1 or choch[idx] == 1) else src[idx + 2:] < lvl

        if np.any(op):
            j = np.argmax(op) + idx + 2
            broken[idx] = j

            # clear earlier breaks that are invalidated
            for k in indices:
                if k < idx and broken[k] >= j:
                    bos[k] = 0
                    choch[k] = 0
                    level[k] = 0

    return broken
