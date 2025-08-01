# Add ta-lib functions: https://ta-lib.org/functions/
from collections import namedtuple
from functools import wraps
from typing import Union

import numpy as np
import pandas as pd
import xno.timeseries as xts
from inspect import signature, isfunction

__all__ = [
    "TimeseriesFeatures",
    "TAInput", "TAOutput",
    "ARoonResult", "MAMAResult", "MACDResult", "MACDEXTResult", "MACDFixResult",
    "BBANDSResult", "StochResult", "StochFResult", "StochRsiResult",
    "HtPhasorResult", "HtSineResult", "KDJResult", "MinMaxResult"
]


TAInput = Union[np.ndarray, pd.Series, None]
TAOutput = np.ndarray

ARoonResult = namedtuple("ARoonResult", ["aroondown", "aroonup"])
MAMAResult = namedtuple("MAMAResult", ["mama", "fama"])
MACDResult = namedtuple("MACDResult", ["macd", "signal", "hist"])
MACDEXTResult = namedtuple("MACDEXTResult", ["macd", "macdsignal", "macdhist"])
MACDFixResult = namedtuple("MACDFixResult", ["macd", "macdsignal", "macdhist"])
BBANDSResult = namedtuple("BBANDSResult", ["upperband", "middleband", "lowerband"])
StochResult = namedtuple("StochResult", ["slowk", "slowd"])
StochFResult = namedtuple("StochFResult", ["fastk", "fastd"])
StochRsiResult = namedtuple("StochRsiResult", ["fastk", "fastd"])
HtPhasorResult = namedtuple("HtPhasorResult", ["inphase", "quadrature"])
HtSineResult = namedtuple("HtSineResult", ["sine", "leadsine"])
KDJResult = namedtuple("KDResult", ["slowk", "slowd"])
MinMaxResult = namedtuple("MinMaxResult", ["min", "max"])


_DEFAULT_COLUMN_MAP = {
    'open_': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'series': 'Close'  # Optional common alias
}

def autofill(_func=None, *, columns_map=None):
    """
    - Fills None args from self.df_ticker[column] using a name map
    - Converts pd.Series to np.ndarray
    - Supports default arg names like `open_`, `high`, `close`, etc.
    """
    columns_map = columns_map or _DEFAULT_COLUMN_MAP

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            sig = signature(func)
            bound = sig.bind(self, *args, **kwargs)
            bound.apply_defaults()

            for arg_name in bound.arguments:
                val = bound.arguments[arg_name]
                if val is None and arg_name in columns_map:
                    col = columns_map[arg_name]
                    val = self.df_ticker[col]
                if isinstance(val, pd.Series):
                    val = val.values
                bound.arguments[arg_name] = val

            return func(*bound.args, **bound.kwargs)
        return wrapper

    if isfunction(_func):
        return decorator(_func)
    return decorator


def auto_numpy(func):
    """
    - Converts pd.Series to np.ndarray
    - Converts np.int64 / np.float64 to native int / float for Numba compatibility
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        sig = signature(func)
        bound = sig.bind(self, *args, **kwargs)
        bound.apply_defaults()

        for k, v in bound.arguments.items():
            if isinstance(v, pd.Series):
                bound.arguments[k] = v.values
            elif isinstance(v, (np.integer, np.int_)):
                bound.arguments[k] = int(v)
            elif isinstance(v, (np.floating, np.float_)):
                bound.arguments[k] = float(v)

        return func(*bound.args, **bound.kwargs)

    return wrapper



class TimeseriesFeatures:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the feature with the provided data.
        """
        self.df_ticker = df

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def adx(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        timeperiod=14
    ) -> TAOutput:
        return xts.ADX(high, low, close, timeperiod)

    @autofill(columns_map={"close": "Close"})
    def sma(self, close: TAInput = None, timeperiod=30) -> TAOutput:
        return xts.SMA(close, timeperiod)

    @autofill(columns_map={"close": "Close"})
    def macd(self, close: TAInput = None, fastperiod=12, slowperiod=26, signalperiod=9) -> MACDResult:
        macd, signal, hist = xts.MACD(close, fastperiod, slowperiod, signalperiod)
        return MACDResult(macd, signal, hist)

    @autofill(columns_map={"close": "Close"})
    def roc(self, close: TAInput = None, timeperiod=10) -> TAOutput:
        return xts.ROC(close, timeperiod)

    @autofill(columns_map={"close": "Close"})
    def lag(self, close: TAInput = None, periods=1) -> TAOutput:
        return xts.LAG(close, periods)

    @autofill
    def rsi(self, close: TAInput = None, timeperiod=14) -> TAOutput:
        return xts.RSI(close, timeperiod)

    @autofill(columns_map={"close": "Close", "volume": "Volume"})
    def obv(self, close: TAInput = None, volume: TAInput = None) -> TAOutput:
        return xts.OBV(close, volume)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
    def vwap(self, high: TAInput, low: TAInput, close: TAInput, volume: TAInput) -> TAOutput:
        """
        Calculate the Volume Weighted Average Price (VWAP).
        """
        return xts.VWAP(high, low, close, volume)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
    def rolling_vwap(self, high: TAInput, low: TAInput, close: TAInput, volume: TAInput, window=20) -> TAOutput:
        """
        Calculate the rolling Volume Weighted Average Price (VWAP) over a specified window.
        """
        return xts.ROLLING_VWAP(high, low, close, volume, window)

    @autofill(columns_map={"close": "Close"})
    def bbands(
        self,
        close: TAInput = None,
        timeperiod=5,
        nbdevup=2,
        nbdevdn=2,
        matype=0,
    ) -> BBANDSResult:
        upperband, middleband, lowerband = xts.BBANDS(
            close, timeperiod, nbdevup, nbdevdn, matype
        )
        return BBANDSResult(upperband, middleband, lowerband)

    @autofill(columns_map={"series": "Close"})
    def dema(self, series: TAInput = None, timeperiod=30) -> TAOutput:
        return xts.DEMA(series, timeperiod)

    @autofill(columns_map={"series": "Close"})
    def ema(self, series: TAInput = None, timeperiod=30) -> TAOutput:
        return xts.EMA(series, timeperiod)

    @autofill(columns_map={"series": "Close"})
    def ht_trendline(self, series: TAInput = None) -> TAOutput:
        return xts.TRENDLINE(series)

    @autofill(columns_map={"series": "Close"})
    def kama(self, series: TAInput = None, timeperiod=30) -> TAOutput:
        return xts.KAMA(series, timeperiod)

    @autofill(columns_map={"series": "Close"})
    def ma(self, series: TAInput = None, timeperiod=30, matype=0) -> TAOutput:
        return xts.MA(series, timeperiod, matype)

    @autofill(columns_map={"series": "Close"})
    def mama(self, series: TAInput = None, fastlimit=0, slowlimit=0) -> MAMAResult:
        return xts.MAMA(series, fastlimit, slowlimit)

    @autofill(columns_map={"series": "Close", "periods": None})
    def mavp(
        self,
        series: TAInput = None,
        periods: TAInput = None,
        minperiod=2,
        maxperiod=30,
        matype=0,
    ) -> TAOutput:
        if periods is None:
            periods = np.full(series.size, 14)
        return xts.MAVP(series, periods, minperiod, maxperiod, matype)

    @autofill(columns_map={"series": "Close"})
    def midpoint(self, series: TAInput = None, timeperiod=14) -> TAOutput:
        return xts.MIDPOINT(series, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low"})
    def midprice(self, high: TAInput = None, low: TAInput = None, timeperiod=14) -> TAOutput:
        return xts.MIDPRICE(high, low, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low"})
    def sar(self, high: TAInput = None, low: TAInput = None, acceleration=0, maximum=0) -> TAOutput:
        return xts.SAR(high, low, acceleration, maximum)

    @autofill(columns_map={"high": "High", "low": "Low"})
    def sarext(
            self,
            high: TAInput = None,
            low: TAInput = None,
            startvalue=0,
            offsetonreverse=0,
            accelerationinitlong=0,
            accelerationlong=0,
            accelerationmaxlong=0,
            accelerationinitshort=0,
            accelerationshort=0,
            accelerationmaxshort=0,
    ) -> TAOutput:
        return xts.SAREXT(
            high, low,
            startvalue, offsetonreverse,
            accelerationinitlong, accelerationlong, accelerationmaxlong,
            accelerationinitshort, accelerationshort, accelerationmaxshort
        )

    @autofill(columns_map={"series": "Close"})
    def t3(self, series: TAInput = None, timeperiod=5, vfactor=0) -> TAOutput:
        return xts.T3(series, timeperiod, vfactor)

    @autofill(columns_map={"series": "Close"})
    def tema(self, series: TAInput = None, timeperiod=30) -> TAOutput:
        return xts.TEMA(series, timeperiod)

    @autofill(columns_map={"series": "Close"})
    def trima(self, series: TAInput = None, timeperiod=30) -> TAOutput:
        return xts.TRIMA(series, timeperiod)

    @autofill(columns_map={"series": "Close"})
    def wma(self, series: TAInput = None, timeperiod=30) -> TAOutput:
        return xts.WMA(series, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def adxr(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        timeperiod=14
    ) -> TAOutput:
        return xts.ADXR(high, low, close, timeperiod)

    @autofill(columns_map={"series": "Close"})
    def apo(self, series: TAInput = None, fastperiod=12, slowperiod=26, matype=0) -> TAOutput:
        return xts.APO(series, fastperiod, slowperiod, matype)

    @autofill(columns_map={"high": "High", "low": "Low"})
    def aroon(self, high: TAInput = None, low: TAInput = None, timeperiod=14) -> ARoonResult:
        return ARoonResult(*xts.AROON(high, low, timeperiod))

    @autofill(columns_map={"high": "High", "low": "Low"})
    def aroonosc(self, high: TAInput = None, low: TAInput = None, timeperiod=14) -> TAOutput:
        return xts.AROONOSC(high, low, timeperiod)

    @autofill(columns_map={"open_": "Open", "high": "High", "low": "Low", "close": "Close"})
    def bop(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.BOP(open_, high, low, close)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def cci(self, high: TAInput = None, low: TAInput = None, close: TAInput = None, timeperiod=14) -> TAOutput:
        return xts.CCI(high, low, close, timeperiod)

    @autofill(columns_map={"series": "Close"})
    def cmo(self, series: TAInput = None, timeperiod=14) -> TAOutput:
        return xts.CMO(series, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def dx(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        timeperiod=14
    ) -> TAOutput:
        return xts.DX(high, low, close, timeperiod)

    @autofill(columns_map={"series": "Close"})
    def macdext(
        self,
        series: TAInput = None,
        fastperiod=12,
        fastmatype=0,
        slowperiod=26,
        slowmatype=0,
        signalperiod=9,
        signalmatype=0
    ) -> MACDEXTResult:
        macd, signal, hist = xts.MACDEXT(series, fastperiod, fastmatype, slowperiod, slowmatype, signalperiod, signalmatype)
        return MACDEXTResult(macd, signal, hist)

    @autofill(columns_map={"series": "Close"})
    def macdfix(
        self,
        series: TAInput = None,
        signalperiod=9
    ) -> MACDFixResult:
        macd, signal, hist = xts.MACDFIX(series, signalperiod)
        return MACDFixResult(macd, signal, hist)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
    def mfi(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        volume: TAInput = None,
        timeperiod=14
    ) -> TAOutput:
        return xts.MFI(high, low, close, volume, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def minus_di(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        timeperiod=14
    ) -> TAOutput:
        return xts.MINUS_DI(high, low, close, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low"})
    def minus_dm(self, high: TAInput = None, low: TAInput = None, timeperiod=14) -> TAOutput:
        return xts.MINUS_DM(high, low, timeperiod)

    @autofill(columns_map={"series": "Close"})
    def mom(self, series: TAInput = None, timeperiod=10) -> TAOutput:
        return xts.MOM(series, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def plus_di(self, high: TAInput = None, low: TAInput = None, close: TAInput = None, timeperiod=14) -> TAOutput:
        return xts.PLUS_DI(high, low, close, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low"})
    def plus_dm(self, high: TAInput = None, low: TAInput = None, timeperiod=14) -> TAOutput:
        return xts.PLUS_DM(high, low, timeperiod)

    @autofill(columns_map={"series": "Close"})
    def ppo(self, series: TAInput = None, fastperiod=12, slowperiod=26, matype=0) -> TAOutput:
        return xts.PPO(series, fastperiod, slowperiod, matype)

    @autofill(columns_map={"series": "Close"})
    def rocp(self, series: TAInput = None, timeperiod=10) -> TAOutput:
        return xts.ROCP(series, timeperiod)

    @autofill(columns_map={"series": "Close"})
    def rocr(self, series: TAInput = None, timeperiod=10) -> TAOutput:
        return xts.ROCR(series, timeperiod)

    @autofill(columns_map={"series": "Close"})
    def rocr100(self, series: TAInput = None, timeperiod=10) -> TAOutput:
        return xts.ROCR100(series, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def stoch(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        fastk_period=5,
        slowk_period=3,
        slowk_matype=0,
        slowd_period=3,
        slowd_matype=0
    ) -> StochResult:
        slowk, slowd = xts.STOCH(high, low, close, fastk_period, slowk_period, slowk_matype, slowd_period, slowd_matype)
        return StochResult(slowk, slowd)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def stochf(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        fastk_period=5,
        fastd_period=3,
        fastd_matype=0
    ) -> StochFResult:
        fastk, fastd = xts.STOCHF(high, low, close, fastk_period, fastd_period, fastd_matype)
        return StochFResult(fastk, fastd)

    @autofill(columns_map={"series": "Close"})
    def stochrsi(
        self,
        series: TAInput = None,
        timeperiod=14,
        fastk_period=5,
        fastd_period=3,
        fastd_matype=0
    ) -> StochRsiResult:
        fastk, fastd = xts.STOCHRSI(series, timeperiod, fastk_period, fastd_period, fastd_matype)
        return StochRsiResult(fastk, fastd)

    @autofill(columns_map={"close": "Close"})
    def trix(self, close: TAInput = None, timeperiod=30) -> TAOutput:
        return xts.TRIX(close, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def ultosc(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        timeperiod1=7,
        timeperiod2=14,
        timeperiod3=28,
    ) -> TAOutput:
        return xts.ULTOSC(high, low, close, timeperiod1, timeperiod2, timeperiod3)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def willr(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        timeperiod=14,
    ) -> TAOutput:
        return xts.WILLR(high, low, close, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
    def ad(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        volume: TAInput = None
    ) -> TAOutput:
        return xts.AD(high, low, close, volume)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
    def adosc(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        volume: TAInput = None,
        fastperiod=3,
        slowperiod=10
    ) -> TAOutput:
        return xts.ADOSC(high, low, close, volume, fastperiod, slowperiod)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def atr(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        timeperiod: int = 14
    ) -> TAOutput:
        return xts.ATR(high, low, close, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def natr(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None,
        timeperiod: int = 14
    ) -> TAOutput:
        return xts.NATR(high, low, close, timeperiod)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def trange(
        self,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None
    ) -> TAOutput:
        return xts.TRANGE(high, low, close)

    @autofill(columns_map={"close": "Close"})
    def dcperiod(self, close: TAInput = None) -> TAOutput:
        return xts.DCPERIOD(close)

    @autofill(columns_map={"close": "Close"})
    def dcphase(self, close: TAInput = None) -> TAOutput:
        return xts.DCPHASE(close)

    @autofill(columns_map={"close": "Close"})
    def phasor(self, close: TAInput = None) -> HtPhasorResult:
        inphase, quadrature = xts.PHASOR(close)
        return HtPhasorResult(inphase, quadrature)

    @autofill(columns_map={"close": "Close"})
    def sine(self, close: TAInput) -> HtSineResult:
        sine, leadsine = xts.SINE(close)
        return HtSineResult(sine, leadsine)

    @autofill(columns_map={"close": "Close"})
    def trendmode(self, close: TAInput = None) -> TAOutput:
        return xts.TRENDMODE(close)

    @autofill(columns_map={"open_": "Open", "high": "High", "low": "Low", "close": "Close"})
    def avgprice(
        self,
        open_: TAInput = None,
        high: TAInput = None,
        low: TAInput = None,
        close: TAInput = None
    ) -> TAOutput:
        return xts.AVGPRICE(open_, high, low, close)

    @autofill(columns_map={"high": "High", "low": "Low"})
    def medprice(self, high: TAInput = None, low: TAInput = None) -> TAOutput:
        return xts.MEDPRICE(high, low)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def typprice(self, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.TYPPRICE(high, low, close)

    @autofill(columns_map={"high": "High", "low": "Low", "close": "Close"})
    def wclprice(self, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.WCLPRICE(high, low, close)

    # Mathematical Functions
    @auto_numpy
    def beta(self, s1: TAInput, s2: TAOutput, timeperiod=5) -> TAOutput:
        return xts.BETA(s1, s2, timeperiod)

    @auto_numpy
    def correl(self, s1: TAInput, s2: TAOutput, timeperiod=30) -> TAOutput:
        return xts.CORREL(s1, s2, timeperiod)

    @auto_numpy
    def linearreg(self, s1: TAInput, timeperiod=14) -> TAOutput:
        return xts.LINEARREG(s1, timeperiod)

    @auto_numpy
    def linearreg_angle(self, s1: TAInput, timeperiod=14) -> TAOutput:
        return xts.LINEARREG_ANGLE(s1, timeperiod)

    @auto_numpy
    def linearreg_intercept(self, s1: TAInput, timeperiod=14) -> TAOutput:
        return xts.LINEARREG_INTERCEPT(s1, timeperiod)

    @auto_numpy
    def linearreg_slope(self, s1: TAInput, timeperiod=14) -> TAOutput:
        return xts.LINEARREG_SLOPE(s1, timeperiod)

    @auto_numpy
    def stddev(self, s1: TAInput, timeperiod=5, nbdev=1) -> TAOutput:
        return xts.STDDEV(s1, timeperiod, nbdev)

    @auto_numpy
    def tsf(self, s1: TAInput, timeperiod=14) -> TAOutput:
        return xts.TSF(s1, timeperiod)

    @auto_numpy
    def var(self, s1: TAInput, timeperiod=5, nbdev=1) -> TAOutput:
        return xts.VAR(s1, timeperiod, nbdev)

    @auto_numpy
    def acos(self, s1: TAInput) -> TAOutput:
        return xts.ACOS(s1)

    @auto_numpy
    def asin(self, s1: TAInput) -> TAOutput:
        return xts.ASIN(s1)

    @auto_numpy
    def atan(self, s1: TAInput) -> TAOutput:
        return xts.ATAN(s1)

    @auto_numpy
    def ceil(self, s1: TAInput) -> TAOutput:
        return xts.CEIL(s1)

    @auto_numpy
    def cos(self, s1: TAInput) -> TAOutput:
        return xts.COS(s1)

    @auto_numpy
    def cosh(self, s1: TAInput) -> TAOutput:
        return xts.COSH(s1)

    @auto_numpy
    def exp(self, s1: TAInput) -> TAOutput:
        return xts.EXP(s1)

    @auto_numpy
    def floor(self, s1: TAInput) -> TAOutput:
        return xts.FLOOR(s1)

    @auto_numpy
    def ln(self, s1: TAInput) -> TAOutput:
        return xts.LN(s1)

    @auto_numpy
    def log10(self, s1: TAInput) -> TAOutput:
        return xts.LOG10(s1)

    @auto_numpy
    def sin(self, s1: TAInput) -> TAOutput:
        return xts.SIN(s1)

    @auto_numpy
    def sinh(self, s1: TAInput) -> TAOutput:
        return xts.SINH(s1)

    @auto_numpy
    def sqrt(self, s1: TAInput) -> TAOutput:
        return xts.SQRT(s1)

    @auto_numpy
    def tan(self, s1: TAInput) -> TAOutput:
        return xts.TAN(s1)

    @auto_numpy
    def tanh(self, s1: TAInput) -> TAOutput:
        return xts.TANH(s1)

    @auto_numpy
    def add(self, s1: TAInput, s2: TAInput) -> TAOutput:
        return xts.ADD(s1, s2)

    @auto_numpy
    def div(self, s1: TAInput, s2: TAInput) -> TAOutput:
        return xts.DIV(s1, s2)

    @auto_numpy
    def max(self, s1: TAInput, timeperiod=30) -> TAOutput:
        return xts.MAX(s1, timeperiod)

    @auto_numpy
    def maxindex(self, s1: TAInput, timeperiod=30) -> TAOutput:
        return xts.MAXINDEX(s1, timeperiod)

    @auto_numpy
    def min(self, s1: TAInput, timeperiod=30) -> TAOutput:
        return xts.MIN(s1, timeperiod)

    @auto_numpy
    def minindex(self, s1: TAInput, timeperiod=30) -> TAOutput:
        return xts.MININDEX(s1, timeperiod)

    @auto_numpy
    def minmax(self, s1: TAInput, timeperiod=30) -> MinMaxResult:
        min_, max_ = xts.MINMAX(s1, timeperiod)
        return MinMaxResult(min_, max_)

    @auto_numpy
    def minmaxindex(self, s1: TAInput, timeperiod=30) -> TAOutput:
        return xts.MINMAXINDEX(s1, timeperiod)

    @auto_numpy
    def mult(self, s1: TAInput, s2: TAInput) -> TAOutput:
        return xts.MULT(s1, s2)

    @auto_numpy
    def sub(self, s1: TAInput, s2: TAInput) -> TAOutput:
        return xts.SUB(s1, s2)

    @auto_numpy
    def sum(self, s1: TAInput, timeperiod=30) -> TAOutput:
        return xts.SUM(s1, timeperiod)

    @auto_numpy
    def rolling_mean(self, s1: TAInput, window=20) -> TAOutput:
        return xts.ROLLING_MEAN(s1, window)

    @auto_numpy
    def rolling_max(self, s1: TAInput, window=20) -> TAOutput:
        return xts.ROLLING_MAX(s1, window)

    @auto_numpy
    def rolling_min(self, s1: TAInput, window=20) -> TAOutput:
        return xts.ROLLING_MIN(s1, window)

    @auto_numpy
    def rolling_std(self, s1: TAInput, window=20) -> TAOutput:
        return xts.ROLLING_STD(s1, window)

    @auto_numpy
    def rolling_sum(self, s1: TAInput, window=20) -> TAOutput:
        return xts.ROLLING_SUM(s1, window)

    @auto_numpy
    def rolling_prod(self, s1: TAInput, window=20) -> TAOutput:
        return xts.ROLLING_PROD(s1, window)

    @auto_numpy
    def rolling_rank(self, s1: TAInput, window=20) -> TAOutput:
        return xts.ROLLING_RANK(s1, window)

    @auto_numpy
    def rolling_correlation(self, s1: TAInput, s2: TAInput, window=20) -> TAOutput:
        return xts.ROLLING_CORRELATION(s1, s2, window)

    @auto_numpy
    def rolling_covariance(self, s1: TAInput, s2: TAInput, window=20) -> TAOutput:
        return xts.ROLLING_COVARIANCE(s1, s2, window)

    @auto_numpy
    def rolling_median(self, s1: TAInput, window=20) -> TAOutput:
        return xts.ROLLING_MEDIAN(s1, window)

    # CANDLESTICK PATTERNS (I just added it here)
    @autofill
    def two_crows(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.TWO_CROWS(open_, high, low, close)

    @autofill
    def three_black_crows(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.THREE_BLACK_CROWS(open_, high, low, close)

    @autofill
    def three_inside_up_down(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.THREE_INSIDE(open_, high, low, close)

    @autofill
    def three_line_strike(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.THREE_LINE_STRIKE(open_, high, low, close)

    @autofill
    def three_outside_up_down(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.THREE_OUTSIDE(open_, high, low, close)

    @autofill
    def three_stars_in_south(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.THREE_STARS_IN_THE_SOUTH(open_, high, low, close)

    @autofill
    def three_white_soldiers(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.THREE_WHITE_SOLDIERS(open_, high, low, close)

    @autofill
    def abandoned_baby(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.ABANDONED_BABY(open_, high, low, close)

    @autofill
    def advance_block(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.ADVANCE_BLOCK(open_, high, low, close)

    @autofill
    def belt_hold(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.BELT_HOLD(open_, high, low, close)

    @autofill
    def breakaway(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.BREAKAWAY(open_, high, low, close)

    @autofill
    def closing_marubozu(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.CLOSING_MARUBOZU(open_, high, low, close)

    @autofill
    def concealing_baby_swallow(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.CONCEAL_BABY_SWALLOW(open_, high, low, close)

    @autofill
    def counterattack(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.COUNTERATTACK(open_, high, low, close)

    @autofill
    def dark_cloud_cover(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.DARK_CLOUD_COVER(open_, high, low, close)

    @autofill
    def doji(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.DOJI(open_, high, low, close)

    @autofill
    def doji_star(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.DOJI_STAR(open_, high, low, close)

    @autofill
    def dragonfly_doji(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.DRAGONFLY_DOJI(open_, high, low, close)

    @autofill
    def engulfing_pattern(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.ENGULFING(open_, high, low, close)

    @autofill
    def evening_doji_star(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.EVENING_DOJI_STAR(open_, high, low, close)

    @autofill
    def evening_star(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.EVENING_STAR(open_, high, low, close)

    @autofill
    def gap_sidesidewhite(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.GAP_SIDE_BY_SIDE_WHITE(open_, high, low, close)

    @autofill
    def gravestone_doji(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.GRAVESTONE_DOJI(open_, high, low, close)

    @autofill
    def hammer(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.HAMMER(open_, high, low, close)

    @autofill
    def hanging_man(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.HANGING_MAN(open_, high, low, close)

    @autofill
    def harami_pattern(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.HARAMI(open_, high, low, close)

    @autofill
    def harami_cross_pattern(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.HARAMI_CROSS(open_, high, low, close)

    @autofill
    def high_wave_candle(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.HIGH_WAVE(open_, high, low, close)

    @autofill
    def hikkake_pattern(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.HIKKAKE(open_, high, low, close)

    @autofill
    def modified_hikkake_pattern(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.HIKKAKE_MOD(open_, high, low, close)

    @autofill
    def homing_pigeon(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.HOMING_PIGEON(open_, high, low, close)

    @autofill
    def identical_three_crows(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.IDENTICAL_3_CROWS(open_, high, low, close)

    @autofill
    def in_neck_pattern(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.INNECK(open_, high, low, close)

    @autofill
    def inverted_hammer(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.INVERTED_HAMMER(open_, high, low, close)

    @autofill
    def kicking(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.KICKING(open_, high, low, close)

    @autofill
    def kicking_by_length(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.KICKING_BY_LENGTH(open_, high, low, close)

    @autofill
    def ladder_bottom(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.LADDER_BOTTOM(open_, high, low, close)

    @autofill
    def long_legged_doji(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.LONG_LEGGED_DOJI(open_, high, low, close)

    @autofill
    def long_line_candle(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.LONG_LINE_CANDLE(open_, high, low, close)

    @autofill
    def marubozu(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.MARUBOZU(open_, high, low, close)

    @autofill
    def matching_low(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.MATCHING_LOW(open_, high, low, close)

    @autofill
    def mat_hold(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.MAT_HOLD(open_, high, low, close)

    @autofill
    def morning_doji_star(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.MORNING_DOJI_STAR(open_, high, low, close)

    @autofill
    def morning_star(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.MORNING_STAR(open_, high, low, close)

    @autofill
    def on_neck_pattern(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.ON_NECK(open_, high, low, close)

    @autofill
    def piercing_pattern(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.PIERCING(open_, high, low, close)

    @autofill
    def rickshaw_man(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.RICKSHAW_MAN(open_, high, low, close)

    @autofill
    def rising_falling_three_methods(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.RISING_FALLING_THREE_METHODS(open_, high, low, close)

    @autofill
    def separating_lines(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.SEPARATING_LINES(open_, high, low, close)

    @autofill
    def shooting_star(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.SHOOTING_STAR(open_, high, low, close)

    @autofill
    def short_line_candle(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.SHORT_LINE_CANDLE(open_, high, low, close)

    @autofill
    def spinning_top(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.SPINNING_TOP(open_, high, low, close)

    @autofill
    def stalled_pattern(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.STALLEDPATTERN(open_, high, low, close)

    @autofill
    def stick_sandwich(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.STICK_SANDWICH(open_, high, low, close)

    @autofill
    def takuri(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.TAKURI(open_, high, low, close)

    @autofill
    def thrusting_pattern(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.THRUSTING(open_, high, low, close)

    @autofill
    def tristar_pattern(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.TRISTAR(open_, high, low, close)

    @autofill
    def unique_3_river(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.UNIQUE_3_RIVER(open_, high, low, close)

    @autofill
    def upside_gap_two_crows(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.UPSIDE_GAP_TWO_CROWS(open_, high, low, close)

    @autofill
    def xside_gap_3methods(self, open_: TAInput = None, high: TAInput = None, low: TAInput = None, close: TAInput = None) -> TAOutput:
        return xts.X_SIDE_GAP_3_METHODS(open_, high, low, close)
