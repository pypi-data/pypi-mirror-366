from xno.timeseries._internal import _call_func


@_call_func
def ACOS(real):
    """
    Arc Cosine.

    Calculates the arc cosine of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Arc cosine values.
    """
    pass

@_call_func
def ASIN(real):
    """
    Arc Sine.

    Calculates the arc sine of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Arc sine values.
    """
    pass

@_call_func
def ATAN(real):
    """
    Arc Tangent.

    Calculates the arc tangent of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Arc tangent values.
    """
    pass

@_call_func
def CEIL(real):
    """
    Ceiling Function.

    Returns the smallest integer greater than or equal to the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Ceiling values.
    """
    pass

@_call_func
def COS(real):
    """
    Cosine.

    Calculates the cosine of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Cosine values.
    """
    pass

@_call_func
def COSH(real):
    """
    Hyperbolic Cosine.

    Calculates the hyperbolic cosine of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Hyperbolic cosine values.
    """
    pass

@_call_func
def EXP(real):
    """
    Exponential Function.

    Calculates the exponential of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Exponential values.
    """
    pass

@_call_func
def FLOOR(real):
    """
    Floor Function.

    Returns the largest integer less than or equal to the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Floor values.
    """
    pass

@_call_func
def LN(real):
    """
    Natural Logarithm.

    Calculates the natural logarithm of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Natural logarithm values.
    """
    pass

@_call_func
def LOG10(real):
    """
    Base-10 Logarithm.

    Calculates the base-10 logarithm of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Base-10 logarithm values.
    """
    pass

@_call_func
def SIN(real):
    """
    Sine.

    Calculates the sine of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Sine values.
    """
    pass

@_call_func
def SINH(real):
    """
    Hyperbolic Sine.

    Calculates the hyperbolic sine of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Hyperbolic sine values.
    """
    pass

@_call_func
def SQRT(real):
    """
    Square Root.

    Calculates the square root of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Square root values.
    """
    pass

@_call_func
def TAN(real):
    """
    Tangent.

    Calculates the tangent of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Tangent values.
    """
    pass

@_call_func
def TANH(real):
    """
    Hyperbolic Tangent.

    Calculates the hyperbolic tangent of the input data.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Hyperbolic tangent values.
    """
    pass

@_call_func
def ADD(real0, real1):
    """
    Addition.

    Adds two arrays element-wise.

    :param real0: array-like
        First array of input data (e.g., closing prices).
    :param real1: array-like
        Second array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Element-wise addition values.
    """
    pass

@_call_func
def DIV(real0, real1):
    """
    Division.

    Divides two arrays element-wise.

    :param real0: array-like
        Numerator array of input data (e.g., closing prices).
    :param real1: array-like
        Denominator array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Element-wise division values.
    """
    pass

@_call_func
def MAX(real, timeperiod=30):
    """
    Maximum Value over Period.

    Returns the maximum value in the input data over a specified period.

    :param real: array-like
        Array of input data (e.g., closing prices).
    :param timeperiod: int, optional (default=30)
        The number of periods to consider for finding the maximum value.

    :return: numpy.ndarray
        Maximum values.
    """
    pass

@_call_func
def MAXINDEX(real, timeperiod=30):
    """
    Maximum Index over Period.

    Returns the index of the maximum value in the input data over a specified period.

    :param real: array-like
        Array of input data (e.g., closing prices).
    :param timeperiod: int, optional (default=30)
        The number of periods to consider for finding the maximum index.

    :return: numpy.ndarray
        Indices of the maximum values.
    """
    pass

@_call_func
def MIN(real, timeperiod=30):
    """
    Minimum Value over Period.

    Returns the minimum value in the input data over a specified period.

    :param real: array-like
        Array of input data (e.g., closing prices).
    :param timeperiod: int, optional (default=30)
        The number of periods to consider for finding the minimum value.

    :return: numpy.ndarray
        Minimum values.
    """
    pass

@_call_func
def MININDEX(real, timeperiod=30):
    """
    Minimum Index over Period.

    Returns the index of the minimum value in the input data over a specified period.

    :param real: array-like
        Array of input data (e.g., closing prices).
    :param timeperiod: int, optional (default=30)
        The number of periods to consider for finding the minimum index.

    :return: numpy.ndarray
        Indices of the minimum values.
    """
    pass

@_call_func
def MINMAX(real, timeperiod=30):
    """
    Minimum and Maximum Values over Period.

    Returns the minimum and maximum values in the input data over a specified period.

    :param real: array-like
        Array of input data (e.g., closing prices).
    :param timeperiod: int, optional (default=30)
        The number of periods to consider for finding the minimum and maximum values.

    :return: tuple of numpy.ndarray
        (min_values, max_values)
        - min_values: Minimum values.
        - max_values: Maximum values.
    """
    pass

@_call_func
def MINMAXINDEX(real, timeperiod=30):
    """
    Minimum and Maximum Indices over Period.

    Returns the indices of the minimum and maximum values in the input data over a specified period.

    :param real: array-like
        Array of input data (e.g., closing prices).
    :param timeperiod: int, optional (default=30)
        The number of periods to consider for finding the minimum and maximum indices.

    :return: tuple of numpy.ndarray
        (min_indices, max_indices)
        - min_indices: Indices of the minimum values.
        - max_indices: Indices of the maximum values.
    """
    pass

@_call_func
def MULT(real0, real1):
    """
    Multiplication.

    Multiplies two arrays element-wise.

    :param real0: array-like
        First array of input data (e.g., closing prices).
    :param real1: array-like
        Second array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Element-wise multiplication values.
    """
    pass

@_call_func
def SUB(real0, real1):
    """
    Subtraction.

    Subtracts the second array from the first array element-wise.

    :param real0: array-like
        First array of input data (e.g., closing prices).
    :param real1: array-like
        Second array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Element-wise subtraction values.
    """
    pass

@_call_func
def SUM(real, timeperiod=30):
    """
    Sum over Period.

    Returns the sum of the input data over a specified period.

    :param real: array-like
        Array of input data (e.g., closing prices).
    :param timeperiod: int, optional (default=30)
        The number of periods to consider for summation.

    :return: numpy.ndarray
        Sum values.
    """
    pass
