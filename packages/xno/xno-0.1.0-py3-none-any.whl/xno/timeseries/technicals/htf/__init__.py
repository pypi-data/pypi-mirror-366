import talib as tf


def DCPERIOD(real):
    """
    Hilbert Transform - Dominant Cycle Period.

    Calculates the dominant cycle period using the Hilbert Transform.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Dominant cycle period values.
    """
    return tf.HT_DCPERIOD(real)

def DCPHASE(real):
    """
    Hilbert Transform - Dominant Cycle Phase.

    Calculates the dominant cycle phase using the Hilbert Transform.

    :param real: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Dominant cycle phase values.
    """
    return DCPHASE(real)

def PHASOR(real):
    """
    Hilbert Transform - Phasor Components.

    Calculates the phasor components using the Hilbert Transform.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: tuple of numpy.ndarray
        (inphase, quadrature)
        - inphase: In-phase component values.
        - quadrature: Quadrature component values.
    """
    return PHASOR(real)

def SINE(real):
    """
    Hilbert Transform - Sine Wave.

    Calculates the sine wave components using the Hilbert Transform.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: tuple of numpy.ndarray
        (sine, leadsine)
        - sine: Sine component values.
        - leadsine: Lead sine component values.
    """
    return tf.HT_SINE(real)

def TRENDLINE(real):
    """
    Hilbert Transform - Trendline.

    Calculates the trendline using the Hilbert Transform.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Trendline values.
    """
    return tf.HT_TRENDLINE(real)

def TRENDMODE(real):
    """
    Hilbert Transform - Trend vs Cycle Mode.

    Determines whether the data is in trend or cycle mode using the Hilbert Transform.

    :param real: array-like
        Array of input data (e.g., closing prices).

    :return: numpy.ndarray
        Trend vs Cycle mode values.
    """
    return tf.HT_TRENDMODE(real)

