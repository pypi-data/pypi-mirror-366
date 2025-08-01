from xno.timeseries._internal import _call_func


@_call_func
def BBANDS(real, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0):
    """
    Bollinger Bands indicator.

    Calculates the upper, middle, and lower bands using the Bollinger Bands
    method on a moving average of the `close` price.

    :param real: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=5)
        The number of periods for the moving average calculation.
    :param nbdevup: float, optional (default=2)
        Number of standard deviations above the moving average (upper band).
    :param nbdevdn: float, optional (default=2)
        Number of standard deviations below the moving average (lower band).
    :param matype: int, optional (default=0)
        Type of moving average (0=SMA, 1=EMA, etc. — see TA-Lib docs).

    :return: tuple of numpy.ndarray
        (upperband, middleband, lowerband)
        - upperband: Upper Bollinger Band values.
        - middleband: Moving average values.
        - lowerband: Lower Bollinger Band values.
    """
    pass

@_call_func
def DEMA(real, timeperiod=30):
    """
    Double Exponential Moving Average (DEMA).

    Calculates the DEMA of the `close` price over a specified period.

    :param real: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=30)
        The number of periods for the DEMA calculation.

    :return: numpy.ndarray
        DEMA values.
    """
    pass

@_call_func
def EMA(real, timeperiod=30):
    """
    Exponential Moving Average (EMA).

    Calculates the EMA of the `close` price over a specified period.

    :param real: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=30)
        The number of periods for the EMA calculation.

    :return: numpy.ndarray
        EMA values.
    """
    pass

@_call_func
def KAMA(real, timeperiod=30):
    """
    Kaufman's Adaptive Moving Average (KAMA).

    Calculates the KAMA of the `close` price over a specified period.

    :param real: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=30)
        The number of periods for the KAMA calculation.

    :return: numpy.ndarray
        KAMA values.
    """
    pass

@_call_func
def MA(real, timeperiod=30, matype=0):
    """
    Moving Average (MA).

    Calculates the moving average of the `close` price over a specified period.

    :param real: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=30)
        The number of periods for the moving average calculation.
    :param matype: int, optional (default=0)
        Type of moving average (0=SMA, 1=EMA, etc. — see TA-Lib docs).

    :return: numpy.ndarray
        Moving average values.
    """
    pass

@_call_func
def MAMA(real, fastlimit=0, slowlimit=0):
    """
    MESA Adaptive Moving Average (MAMA).

    Calculates the MAMA of the `close` price with specified fast and slow limits.

    :param real: array-like
        Array of closing prices.
    :param fastlimit: float, optional (default=0)
        Fast limit for the MAMA calculation.
    :param slowlimit: float, optional (default=0)
        Slow limit for the MAMA calculation.

    :return: tuple of numpy.ndarray
        (mama, fama)
        - mama: MAMA values.
        - fama: FAMA values.
    """
    pass

@_call_func
def MAVP(real, periods, minperiod=2, maxperiod=30, matype=0):
    """
    Moving Average with Variable Periods (MAVP).

    Calculates moving averages for the `close` price over variable periods.

    :param real: array-like
        Array of closing prices.
    :param periods: array-like
        Array of periods for the moving average calculation.
    :param minperiod: int, optional (default=2)
        Minimum period for the moving average.
    :param maxperiod: int, optional (default=30)
        Maximum period for the moving average.
    :param matype: int, optional (default=0)
        Type of moving average (0=SMA, 1=EMA, etc. — see TA-Lib docs).

    :return: numpy.ndarray
        Moving average values for each specified period.
    """
    pass

@_call_func
def MIDPOINT(real, timeperiod=14):
    """
    MidPoint over period.

    Calculates the midpoint of the `close` price over a specified period.

    :param real: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the midpoint calculation.

    :return: numpy.ndarray
        Midpoint values.
    """
    pass

@_call_func
def MIDPRICE(high, low, timeperiod=14):
    """
    MidPrice over period.

    Calculates the midpoint price between high and low over a specified period.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param timeperiod: int, optional (default=14)
        The number of periods for the midpoint price calculation.

    :return: numpy.ndarray
        Midpoint price values.
    """
    pass

@_call_func
def SAR(high, low, acceleration=0, maximum=0):
    """
    Parabolic SAR (Stop and Reverse).

    Calculates the Parabolic SAR based on high and low prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param acceleration: float, optional (default=0)
        Acceleration factor for the SAR calculation.
    :param maximum: float, optional (default=0)
        Maximum value for the acceleration factor.

    :return: numpy.ndarray
        Parabolic SAR values.
    """
    pass

@_call_func
def SAREXT(high, low, startvalue=0, offsetonreverse=0, accelerationinitlong=0, accelerationlong=0, accelerationmaxlong=0, accelerationinitshort=0, accelerationshort=0, accelerationmaxshort=0):
    """
    Extended Parabolic SAR (Stop and Reverse).

    Calculates the extended Parabolic SAR based on high and low prices with additional parameters.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param startvalue: float, optional (default=0)
        Starting value for the SAR calculation.
    :param offsetonreverse: float, optional (default=0)
        Offset applied when reversing direction.
    :param accelerationinitlong: float, optional (default=0)
        Initial acceleration factor for long positions.
    :param accelerationlong: float, optional (default=0)
        Acceleration factor for long positions.
    :param accelerationmaxlong: float, optional (default=0)
        Maximum acceleration factor for long positions.
    :param accelerationinitshort: float, optional (default=0)
        Initial acceleration factor for short positions.
    :param accelerationshort: float, optional (default=0)
        Acceleration factor for short positions.
    :param accelerationmaxshort: float, optional (default=0)
        Maximum acceleration factor for short positions.

    :return: numpy.ndarray
        Extended Parabolic SAR values.
    """
    pass

@_call_func
def SMA(real, timeperiod=30):
    """
    Simple Moving Average (SMA).

    Calculates the SMA of the `close` price over a specified period.

    :param real: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=30)
        The number of periods for the SMA calculation.

    :return: numpy.ndarray
        SMA values.
    """
    pass

@_call_func
def T3(real, timeperiod=5, vfactor=0):
    """
    Triple Exponential Moving Average (T3).

    Calculates the T3 of the `close` price over a specified period with a volume factor.

    :param real: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=5)
        The number of periods for the T3 calculation.
    :param vfactor: float, optional (default=0)
        Volume factor for the T3 calculation.

    :return: numpy.ndarray
        T3 values.
    """
    pass

@_call_func
def TEMA(real, timeperiod=30):
    """
    Triple Exponential Moving Average (TEMA).

    Calculates the TEMA of the `close` price over a specified period.

    :param real: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=30)
        The number of periods for the TEMA calculation.

    :return: numpy.ndarray
        TEMA values.
    """
    pass

@_call_func
def TRIMA(real, timeperiod=30):
    """
    Triangular Moving Average (TRIMA).

    Calculates the TRIMA of the `close` price over a specified period.

    :param real: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=30)
        The number of periods for the TRIMA calculation.

    :return: numpy.ndarray
        TRIMA values.
    """
    pass

@_call_func
def WMA(real, timeperiod=30):
    """
    Weighted Moving Average (WMA).

    Calculates the WMA of the `close` price over a specified period.

    :param real: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=30)
        The number of periods for the WMA calculation.

    :return: numpy.ndarray
        WMA values.
    """
    pass
