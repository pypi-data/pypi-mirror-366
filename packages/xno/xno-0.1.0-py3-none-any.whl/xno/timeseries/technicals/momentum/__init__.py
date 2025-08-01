from xno.timeseries._internal import _call_func


@_call_func
def ADX(high, low, close, timeperiod=14):
    """
    Average Directional Index (ADX).

    Measures the strength of a trend based on high, low, and close prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the ADX calculation.

    :return: numpy.ndarray
        ADX values.
    """
    pass

@_call_func
def ADXR(high, low, close, timeperiod=14):
    """
    Average Directional Index Rating (ADXR).

    Provides a smoothed version of the ADX, indicating trend strength.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the ADXR calculation.

    :return: numpy.ndarray
        ADXR values.
    """
    pass

@_call_func
def APO(real, fastperiod=12, slowperiod=26, matype=0):
    """
    Absolute Price Oscillator (APO).

    Measures the difference between two moving averages of a price series.

    :param real: array-like
        Input data.
    :param fastperiod: int, optional (default=12)
        Period for the fast moving average.
    :param slowperiod: int, optional (default=26)
        Period for the slow moving average.
    :param matype: int, optional (default=0)
        Type of moving average to use (0 for simple, 1 for exponential, etc.).

    :return: numpy.ndarray
        APO values.
    """
    pass

@_call_func
def AROON(high, low, timeperiod=14):
    """
    Aroon Indicator.

    Measures the time since the highest high and lowest low over a specified period.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the Aroon calculation.

    :return: tuple of numpy.ndarray
        Aroon Up and Aroon Down values.
    """
    pass

@_call_func
def AROONOSC(high, low, timeperiod=14):
    """
    Aroon Oscillator.

    The difference between the Aroon Up and Aroon Down indicators.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the Aroon Oscillator calculation.

    :return: numpy.ndarray
        Aroon Oscillator values.
    """
    pass

@_call_func
def BOP(open_, high, low, close):
    """
    Balance of Power (BOP).

    Measures the strength of buyers versus sellers based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        BOP values.
    """
    pass

@_call_func
def CCI(high, low, close, timeperiod=14):
    """
    Commodity Channel Index (CCI).

    Measures the deviation of the price from its average over a specified period.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the CCI calculation.

    :return: numpy.ndarray
        CCI values.
    """
    pass

@_call_func
def CMO(real, timeperiod=14):
    """
    Chande Momentum Oscillator (CMO).

    Measures the momentum of a price series, providing insight into overbought or oversold conditions.

    :param real: array-like
        Input data.
    :param timeperiod: int, optional (default=14)
        The number of periods for the CMO calculation.

    :return: numpy.ndarray
        CMO values.
    """
    pass

@_call_func
def DX(high, low, close, timeperiod=14):
    """
    Directional Movement Index (DX).

    Measures the strength of a trend based on high, low, and close prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the DX calculation.

    :return: numpy.ndarray
        DX values.
    """
    pass

@_call_func
def MACD(real, fastperiod=12, slowperiod=26, signalperiod=9):
    """
    Moving Average Convergence Divergence (MACD).

    Measures the difference between two moving averages of a price series and includes a signal line.

    :param real: array-like
        Input data.
    :param fastperiod: int, optional (default=12)
        Period for the fast moving average.
    :param slowperiod: int, optional (default=26)
        Period for the slow moving average.
    :param signalperiod: int, optional (default=9)
        Period for the signal line.

    :return: tuple of numpy.ndarray
        MACD line, signal line, and MACD histogram values.
    """
    pass

@_call_func
def MACDEXT(real, fastperiod=12, fastmatype=0, slowperiod=26, slowmatype=0, signalperiod=9, signalmatype=0):
    """
    MACD with Extended Moving Averages.

    Similar to MACD but allows for different types of moving averages for the fast and slow periods.

    :param real: array-like
        Input data.
    :param fastperiod: int, optional (default=12)
        Period for the fast moving average.
    :param fastmatype: int, optional (default=0)
        Type of moving average for the fast period.
    :param slowperiod: int, optional (default=26)
        Period for the slow moving average.
    :param slowmatype: int, optional (default=0)
        Type of moving average for the slow period.
    :param signalperiod: int, optional (default=9)
        Period for the signal line.
    :param signalmatype: int, optional (default=0)
        Type of moving average for the signal line.

    :return: tuple of numpy.ndarray
        MACD line, signal line, and MACD histogram values.
    """
    pass

@_call_func
def MACDFIX(real, signalperiod=9):
    """
    Fixed MACD.

    A variant of MACD with a fixed signal period.

    :param real: array-like
        Input data.
    :param signalperiod: int, optional (default=9)
        Period for the signal line.

    :return: tuple of numpy.ndarray
        MACD line, signal line, and MACD histogram values.
    """
    pass

@_call_func
def MFI(high, low, close, volume, timeperiod=14):
    """
    Money Flow Index (MFI).

    Measures the buying and selling pressure based on high, low, close prices and volume.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param volume: array-like
        Array of trading volumes.
    :param timeperiod: int, optional (default=14)
        The number of periods for the MFI calculation.

    :return: numpy.ndarray
        MFI values.
    """
    pass

@_call_func
def MINUS_DI(high, low, close, timeperiod=14):
    """
    Minus Directional Indicator (-DI).

    Measures the strength of downward price movement based on high, low, and close prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the -DI calculation.

    :return: numpy.ndarray
        -DI values.
    """
    pass

@_call_func
def MINUS_DM(high, low, timeperiod=14):
    """
    Minus Directional Movement (-DM).

    Measures the downward price movement based on high and low prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the -DM calculation.

    :return: numpy.ndarray
        -DM values.
    """
    pass

@_call_func
def MOM(real, timeperiod=10):
    """
    Momentum.

    Measures the rate of change of a price series over a specified period.

    :param real: array-like
        Input data.
    :param timeperiod: int, optional (default=10)
        The number of periods for the momentum calculation.

    :return: numpy.ndarray
        Momentum values.
    """
    pass

@_call_func
def PLUS_DI(high, low, close, timeperiod=14):
    """
    Plus Directional Indicator (+DI).

    Measures the strength of upward price movement based on high, low, and close prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the +DI calculation.

    :return: numpy.ndarray
        +DI values.
    """
    pass

@_call_func
def PLUS_DM(high, low, timeperiod=14):
    """
    Plus Directional Movement (+DM).

    Measures the upward price movement based on high and low prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the +DM calculation.

    :return: numpy.ndarray
        +DM values.
    """
    pass

@_call_func
def PPO(real, fastperiod=12, slowperiod=26, matype=0):
    """
    Percentage Price Oscillator (PPO).

    Measures the difference between two moving averages of a price series expressed as a percentage.

    :param real: array-like
        Input data.
    :param fastperiod: int, optional (default=12)
        Period for the fast moving average.
    :param slowperiod: int, optional (default=26)
        Period for the slow moving average.
    :param matype: int, optional (default=0)
        Type of moving average to use (0 for simple, 1 for exponential, etc.).

    :return: numpy.ndarray
        PPO values.
    """
    pass

@_call_func
def ROC(real, timeperiod=10):
    """
    Rate of Change (ROC).

    Measures the percentage change in a price series over a specified period.

    :param real: array-like
        Input data.
    :param timeperiod: int, optional (default=10)
        The number of periods for the ROC calculation.

    :return: numpy.ndarray
        ROC values.
    """
    pass

@_call_func
def ROCP(real, timeperiod=10):
    """
    Rate of Change Percentage (ROCP).

    Measures the percentage change in a price series over a specified period.

    :param real: array-like
        Input data.
    :param timeperiod: int, optional (default=10)
        The number of periods for the ROCP calculation.

    :return: numpy.ndarray
        ROCP values.
    """
    pass

@_call_func
def ROCR(real, timeperiod=10):
    """
    Rate of Change Ratio (ROCR).

    Measures the ratio of the current price to the price from a specified period ago.

    :param real: array-like
        Input data.
    :param timeperiod: int, optional (default=10)
        The number of periods for the ROCR calculation.

    :return: numpy.ndarray
        ROCR values.
    """
    pass

@_call_func
def ROCR100(real, timeperiod=10):
    """
    Rate of Change Ratio 100 (ROCR100).

    Measures the ratio of the current price to the price from a specified period ago, expressed as a percentage.

    :param real: array-like
        Input data.
    :param timeperiod: int, optional (default=10)
        The number of periods for the ROCR100 calculation.

    :return: numpy.ndarray
        ROCR100 values.
    """
    pass

@_call_func
def RSI(real, timeperiod=14):
    """
    Relative Strength Index (RSI).

    Measures the speed and change of price movements, indicating overbought or oversold conditions.

    :param real: array-like
        Input data.
    :param timeperiod: int, optional (default=14)
        The number of periods for the RSI calculation.

    :return: numpy.ndarray
        RSI values.
    """
    pass

@_call_func
def STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0):
    """
    Stochastic Oscillator.

    Measures the current price relative to its price range over a specified period.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param fastk_period: int, optional (default=5)
        Period for the fast %K.
    :param slowk_period: int, optional (default=3)
        Period for the slow %K.
    :param slowk_matype: int, optional (default=0)
        Type of moving average for the slow %K.
    :param slowd_period: int, optional (default=3)
        Period for the slow %D.
    :param slowd_matype: int, optional (default=0)
        Type of moving average for the slow %D.

    :return: tuple of numpy.ndarray
        Fast %K and Slow %D values.
    """
    pass

@_call_func
def STOCHF(high, low, close, fastk_period=5, fastd_period=3, fastd_matype=0):
    """
    Stochastic Fast Oscillator.

    Measures the current price relative to its price range over a specified period, with fast %K and %D.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param fastk_period: int, optional (default=5)
        Period for the fast %K.
    :param fastd_period: int, optional (default=3)
        Period for the slow %D.
    :param fastd_matype: int, optional (default=0)
        Type of moving average for the slow %D.

    :return: tuple of numpy.ndarray
        Fast %K and Slow %D values.
    """
    pass

@_call_func
def STOCHRSI(real, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0):
    """
    Stochastic Relative Strength Index (StochRSI).

    Measures the RSI relative to its range over a specified period, providing insight into overbought or oversold conditions.

    :param real: array-like
        Input data.
    :param timeperiod: int, optional (default=14)
        The number of periods for the RSI calculation.
    :param fastk_period: int, optional (default=5)
        Period for the fast %K.
    :param fastd_period: int, optional (default=3)
        Period for the slow %D.
    :param fastd_matype: int, optional (default=0)
        Type of moving average for the slow %D.

    :return: tuple of numpy.ndarray
        Fast %K and Slow %D values.
    """
    pass

@_call_func
def TRIX(real, timeperiod=30):
    """
    Triple Exponential Moving Average (TRIX).

    Measures the rate of change of a triple smoothed moving average, providing insight into trend direction and strength.

    :param real: array-like
        Input data.
    :param timeperiod: int, optional (default=30)
        The number of periods for the TRIX calculation.

    :return: numpy.ndarray
        TRIX values.
    """
    pass

@_call_func
def ULTOSC(high, low, close, timeperiod1=7, timeperiod2=14, timeperiod3=28):
    """
    Ultimate Oscillator (ULTOSC).

    Combines three different time periods to measure the momentum of price movements.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param timeperiod1: int, optional (default=7)
        First time period for the calculation.
    :param timeperiod2: int, optional (default=14)
        Second time period for the calculation.
    :param timeperiod3: int, optional (default=28)
        Third time period for the calculation.

    :return: numpy.ndarray
        ULTOSC values.
    """
    pass

@_call_func
def WILLR(high, low, close, timeperiod=14):
    """
    Williams %R (WILLR).

    Measures overbought or oversold conditions based on the current price relative to its high-low range over a specified period.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the WILLR calculation.

    :return: numpy.ndarray
        WILLR values.
    """
    pass
