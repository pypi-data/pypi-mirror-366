from xno.timeseries._internal import _call_func


@_call_func
def ATR(high, low, close, timeperiod=14):
    """
    Average True Range (ATR).

    Calculates the Average True Range based on high, low, and close prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=14)
        Time period for the ATR calculation.

    :return: numpy.ndarray
        Average True Range values.
    """
    pass

@_call_func
def NATR(high, low, close, timeperiod=14):
    """
    Normalized Average True Range (NATR).

    Calculates the Normalized Average True Range based on high, low, and close prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.
    :param timeperiod: int, optional (default=14)
        Time period for the NATR calculation.

    :return: numpy.ndarray
        Normalized Average True Range values.
    """
    pass

@_call_func
def TRANGE(high, low, close):
    """
    True Range (TRANGE).

    Calculates the True Range based on high, low, and close prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        True Range values.
    """
    pass

