from xno.timeseries._internal import _call_func


@_call_func
def AVGPRICE(open_, high, low, close):
    """
    Average Price.

    Calculates the average price based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Average Price values.
    """
    pass

@_call_func
def MEDPRICE(high, low):
    """
    Median Price.

    Calculates the median price based on high and low prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.

    :return: numpy.ndarray
        Median Price values.
    """
    pass

@_call_func
def TYPPRICE(high, low, close):
    """
    Typical Price.

    Calculates the typical price based on high, low, and close prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Typical Price values.
    """
    pass

@_call_func
def WCLPRICE(high, low, close):
    """
    Weighted Close Price.

    Calculates the weighted close price based on high, low, and close prices.

    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Weighted Close Price values.
    """
    pass
