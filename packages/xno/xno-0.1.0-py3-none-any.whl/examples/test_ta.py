# https://docs.fiinquant.vn/ham-va-cong-thuc/danh-sach-chi-so-ta
# Excel
# pip install --extra-index-url https://fiinquant.github.io/fiinquantx/simple fiinquantx
import numpy as np
import pandas
from xno.algo.features import TimeseriesFeatures

open_ = np.random.rand(10000)
high = np.random.rand(10000)
low = np.random.rand(10000)
close = np.random.rand(10000)
volume = np.random.rand(10000) * 1000


df = pandas.DataFrame({
    'Open': open_,
    'High': high,
    'Low': low,
    'Close': close,
    'Volume': volume
})

ts = TimeseriesFeatures(df)

ts.rsi(timeperiod=14)
ts.rsi(df['Close'], timeperiod=14)
