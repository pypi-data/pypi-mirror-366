import numpy as np
import xno.timeseries as xt

open_ = np.random.rand(100)
high = np.random.rand(100)
low = np.random.rand(100)
close = np.random.rand(100)
volume = np.random.rand(100)

adx = xt.ADX(high, low, close, timeperiod=14)
print("ADX:", adx)

# fvg = xt.FVG(open_, high, low, close, join_consecutive=True)
# print("FVG:", fvg)
#
# high_low, level = xt.SWING_HIGHS_LOWS(high, low)
# print("SWG:", high_low)
