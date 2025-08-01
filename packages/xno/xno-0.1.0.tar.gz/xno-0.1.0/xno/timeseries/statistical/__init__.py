from xno.timeseries._internal import _call_func


@_call_func
def BETA(real0, real1, timeperiod=5):
    """
    Beta Coefficient.

    Calculates the Beta coefficient between two time series.

    :param real0: array-like
        First time series.
    :param real1: array-like
        Second time series.
    :param timeperiod: int, optional (default=5)
        The number of periods for the Beta calculation.

    :return: numpy.ndarray
        Beta values.
    """
    pass

@_call_func
def CORREL(real0, real1, timeperiod=30):
    """
    Pearson's Correlation Coefficient.

    Calculates the Pearson's correlation coefficient between two time series.

    :param real0: array-like
        First time series.
    :param real1: array-like
        Second time series.
    :param timeperiod: int, optional (default=30)
        The number of periods for the correlation calculation.

    :return: numpy.ndarray
        Correlation values.
    """
    pass

@_call_func
def LINEARREG(real, timeperiod=14):
    """
    Linear Regression.

    Calculates the linear regression of a time series.

    :param real: array-like
        Time series data.
    :param timeperiod: int, optional (default=14)
        The number of periods for the linear regression calculation.

    :return: numpy.ndarray
        Linear regression values.
    """
    pass

@_call_func
def LINEARREG_ANGLE(real, timeperiod=14):
    """
    Linear Regression Angle.

    Calculates the angle of the linear regression line of a time series.

    :param real: array-like
        Time series data.
    :param timeperiod: int, optional (default=14)
        The number of periods for the linear regression angle calculation.

    :return: numpy.ndarray
        Linear regression angle values.
    """
    pass

@_call_func
def LINEARREG_INTERCEPT(real, timeperiod=14):
    """
    Linear Regression Intercept.

    Calculates the intercept of the linear regression line of a time series.

    :param real: array-like
        Time series data.
    :param timeperiod: int, optional (default=14)
        The number of periods for the linear regression intercept calculation.

    :return: numpy.ndarray
        Linear regression intercept values.
    """
    pass

@_call_func
def LINEARREG_SLOPE(real, timeperiod=14):
    """
    Linear Regression Slope.

    Calculates the slope of the linear regression line of a time series.

    :param real: array-like
        Time series data.
    :param timeperiod: int, optional (default=14)
        The number of periods for the linear regression slope calculation.

    :return: numpy.ndarray
        Linear regression slope values.
    """
    pass

@_call_func
def STDDEV(real, timeperiod=30, nbdev=1):
    """
    Standard Deviation.

    Calculates the standard deviation of a time series.

    :param real: array-like
        Time series data.
    :param timeperiod: int, optional (default=30)
        The number of periods for the standard deviation calculation.
    :param nbdev: int, optional (default=1)
        Number of standard deviations to calculate.

    :return: numpy.ndarray
        Standard deviation values.
    """
    pass

@_call_func
def TSF(real, timeperiod=14):
    """
    Time Series Forecast.

    Calculates the time series forecast of a time series.

    :param real: array-like
        Time series data.
    :param timeperiod: int, optional (default=14)
        The number of periods for the time series forecast calculation.

    :return: numpy.ndarray
        Time series forecast values.
    """
    pass

@_call_func
def VAR(real, timeperiod=30, nbdev=1):
    """
    Variance.

    Calculates the variance of a time series.

    :param real: array-like
        Time series data.
    :param timeperiod: int, optional (default=30)
        The number of periods for the variance calculation.
    :param nbdev: int, optional (default=1)
        Number of deviations to calculate.

    :return: numpy.ndarray
        Variance values.
    """
    pass

