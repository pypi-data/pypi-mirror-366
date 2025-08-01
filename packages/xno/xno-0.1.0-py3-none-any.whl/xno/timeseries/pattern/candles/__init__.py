import talib

def TWO_CROWS(open_, high, low, close):
    """
    Two Crows Pattern.

    Identifies the Two Crows candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Two Crows Pattern values.
    """
    return talib.CDL2CROWS(open_, high, low, close)


def THREE_BLACK_CROWS(open_, high, low, close):
    """
    Three Black Crows Pattern.

    Identifies the Three Black Crows candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Three Black Crows Pattern values.
    """
    return talib.CDL3BLACKCROWS(open_, high, low, close)


def THREE_INSIDE(open_, high, low, close):
    """
    Three Inside Pattern.

    Identifies the Three Inside candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Three Inside Pattern values.
    """
    return talib.CDL3INSIDE(open_, high, low, close)

def THREE_LINE_STRIKE(open_, high, low, close):
    """
    Three-Line Strike Pattern.

    Identifies the Three-Line Strike candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Three-Line Strike Pattern values.
    """
    return talib.CDL3LINESTRIKE(open_, high, low, close)

def THREE_OUTSIDE(open_, high, low, close):
    """
    Three Outside Pattern.

    Identifies the Three Outside candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Three Outside Pattern values.
    """
    return talib.CDL3OUTSIDE(open_, high, low, close)

def THREE_STARS_IN_THE_SOUTH(open_, high, low, close):
    """
    Three Stars in the South Pattern.

    Identifies the Three Stars in the South candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Three Stars in the South Pattern values.
    """
    return talib.CDL3STARSINSOUTH(open_, high, low, close)

def THREE_WHITE_SOLDIERS(open_, high, low, close):
    """
    Three White Soldiers Pattern.

    Identifies the Three White Soldiers candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Three White Soldiers Pattern values.
    """
    return talib.CDL3WHITESOLDIERS(open_, high, low, close)

def ABANDONED_BABY(open_, high, low, close):
    """
    Abandoned Baby Pattern.

    Identifies the Abandoned Baby candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Abandoned Baby Pattern values.
    """
    return talib.CDLABANDONEDBABY(open_, high, low, close)

def ADVANCE_BLOCK(open_, high, low, close):
    """
    Advance Block Pattern.

    Identifies the Advance Block candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Advance Block Pattern values.
    """
    return talib.CDLADVANCEBLOCK(open_, high, low, close)

def BELT_HOLD(open_, high, low, close):
    """
    Belt Hold Pattern.

    Identifies the Belt Hold candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Belt Hold Pattern values.
    """
    return talib.CDLBELTHOLD(open_, high, low, close)

def BREAKAWAY(open_, high, low, close):
    """
    Breakaway Pattern.

    Identifies the Breakaway candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Breakaway Pattern values.
    """
    return talib.CDLBREAKAWAY(open_, high, low, close)

def CLOSING_MARUBOZU(open_, high, low, close):
    """
    Closing Marubozu Pattern.

    Identifies the Closing Marubozu candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Closing Marubozu Pattern values.
    """
    return talib.CDLCLOSINGMARUBOZU(open_, high, low, close)

def CONCEAL_BABY_SWALLOW(open_, high, low, close):
    """
    Concealing Baby Swallow Pattern.

    Identifies the Concealing Baby Swallow candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Concealing Baby Swallow Pattern values.
    """
    return talib.CDLCONCEALBABYSWALL(open_, high, low, close)

def COUNTERATTACK(open_, high, low, close):
    """
    Counterattack Pattern.

    Identifies the Counterattack candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Counterattack Pattern values.
    """
    return talib.CDLCOUNTERATTACK(open_, high, low, close)

def DARK_CLOUD_COVER(open_, high, low, close):
    """
    Dark Cloud Cover Pattern.

    Identifies the Dark Cloud Cover candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Dark Cloud Cover Pattern values.
    """
    return talib.CDLDARKCLOUDCOVER(open_, high, low, close)

def DOJI(open_, high, low, close):
    """
    Doji Pattern.

    Identifies the Doji candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Doji Pattern values.
    """
    return talib.CDLDOJI(open_, high, low, close)

def DOJI_STAR(open_, high, low, close):
    """
    Doji Star Pattern.

    Identifies the Doji Star candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Doji Star Pattern values.
    """
    return talib.CDLDOJISTAR(open_, high, low, close)

def DRAGONFLY_DOJI(open_, high, low, close):
    """
    Dragonfly Doji Pattern.

    Identifies the Dragonfly Doji candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Dragonfly Doji Pattern values.
    """
    return talib.CDLDRAGONFLYDOJI(open_, high, low, close)

def ENGULFING(open_, high, low, close):
    """
    Engulfing Pattern.

    Identifies the Engulfing candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Engulfing Pattern values.
    """
    return talib.CDLENGULFING(open_, high, low, close)

def EVENING_DOJI_STAR(open_, high, low, close):
    """
    Evening Doji Star Pattern.

    Identifies the Evening Doji Star candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Evening Doji Star Pattern values.
    """
    return talib.CDLEVENINGDOJISTAR(open_, high, low, close)

def EVENING_STAR(open_, high, low, close):
    """
    Evening Star Pattern.

    Identifies the Evening Star candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Evening Star Pattern values.
    """
    return talib.CDLEVENINGSTAR(open_, high, low, close)

def GAP_SIDE_BY_SIDE_WHITE(open_, high, low, close):
    """
    Gap Side by Side White Pattern.

    Identifies the Gap Side by Side White candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Gap Side by Side White Pattern values.
    """
    return talib.CDLGAPSIDESIDEWHITE(open_, high, low, close)

def GRAVESTONE_DOJI(open_, high, low, close):
    """
    Gravestone Doji Pattern.

    Identifies the Gravestone Doji candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Gravestone Doji Pattern values.
    """
    return talib.CDLGRAVESTONEDOJI(open_, high, low, close)

def HAMMER(open_, high, low, close):
    """
    Hammer Pattern.

    Identifies the Hammer candlestick pattern based on open, high, low, and close prices.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Hammer Pattern values.
    """
    return talib.CDLHAMMER(open_, high, low, close)

def HANGING_MAN(open_, high, low, close):
    """
    Hanging Man Pattern.

    Identifies the Hanging Man candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs at the top of an uptrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Hanging Man Pattern values.
        Positive values indicate a detected Hanging Man pattern.
    """
    return talib.CDLHANGINGMAN(open_, high, low, close)

def HARAMI(open_, high, low, close):
    """
    Harami Pattern.

    Identifies the Harami candlestick pattern based on open, high, low, and close prices.
    A Harami pattern consists of a large candle followed by a smaller candle that is contained within the range of the larger candle.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Harami Pattern values.
        Positive values indicate a detected Harami pattern.
    """
    return talib.CDLHARAMI(open_, high, low, close)

def HARAMI_CROSS(open_, high, low, close):
    """
    Harami Cross Pattern.

    Identifies the Harami Cross candlestick pattern based on open, high, low, and close prices.
    A Harami Cross is a variation of the Harami pattern where the second candle is a Doji.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Harami Cross Pattern values.
        Positive values indicate a detected Harami Cross pattern.
    """
    return talib.CDLHARAMICROSS(open_, high, low, close)

def HIGH_WAVE(open_, high, low, close):
    """
    High Wave Pattern.

    Identifies the High Wave candlestick pattern based on open, high, low, and close prices.
    A High Wave pattern is characterized by long upper and lower shadows with a small body.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        High Wave Pattern values.
        Positive values indicate a detected High Wave pattern.
    """
    return talib.CDLHIGHWAVE(open_, high, low, close)

def HIKKAKE(open_, high, low, close):
    """
    Hikkake Pattern.

    Identifies the Hikkake candlestick pattern based on open, high, low, and close prices.
    A Hikkake pattern is a false breakout pattern that can indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Hikkake Pattern values.
        Positive values indicate a detected Hikkake pattern.
    """
    return talib.CDLHIKKAKE(open_, high, low, close)

def HIKKAKE_MOD(open_, high, low, close):
    """
    Modified Hikkake Pattern.

    Identifies the Modified Hikkake candlestick pattern based on open, high, low, and close prices.
    This is a variation of the Hikkake pattern that may provide additional confirmation signals.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Modified Hikkake Pattern values.
        Positive values indicate a detected Modified Hikkake pattern.
    """
    return talib.CDLHIKKAKEMOD(open_, high, low, close)

def HOMING_PIGEON(open_, high, low, close):
    """
    Homing Pigeon Pattern.

    Identifies the Homing Pigeon candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs after a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Homing Pigeon Pattern values.
        Positive values indicate a detected Homing Pigeon pattern.
    """
    return talib.CDLHOMINGPIGEON(open_, high, low, close)

def IDENTICAL_3_CROWS(open_, high, low, close):
    """
    Identical Three Crows Pattern.

    Identifies the Identical Three Crows candlestick pattern based on open, high, low, and close prices.
    This pattern is a bearish reversal pattern that typically occurs after an uptrend.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Identical Three Crows Pattern values.
    """
    return talib.CDLIDENTICAL3CROWS(open_, high, low, close)

def INNECK(open_, high, low, close):
    """
    In-Neck Pattern.

    Identifies the In-Neck candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs after a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        In-Neck Pattern values.
    """
    return talib.CDLINNECK(open_, high, low, close)

def INVERTED_HAMMER(open_, high, low, close):
    """
    Inverted Hammer Pattern.

    Identifies the Inverted Hammer candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs at the bottom of a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Inverted Hammer Pattern values.
    """
    return talib.CDLINVERTEDHAMMER(open_, high, low, close)

def KICKING(open_, high, low, close):
    """
    Kicking Pattern.

    Identifies the Kicking candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs at the end of a trend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Kicking Pattern values.
    """
    return talib.CDLKICKING(open_, high, low, close)

def KICKING_BY_LENGTH(open_, high, low, close):
    """
    Kicking by Length Pattern.

    Identifies the Kicking by Length candlestick pattern based on open, high, low, and close prices.
    This pattern is a variation of the Kicking pattern that may provide additional confirmation signals.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Kicking by Length Pattern values.
    """
    return talib.CDLKICKINGBYLENGTH(open_, high, low, close)

def LADDER_BOTTOM(open_, high, low, close):
    """
    Ladder Bottom Pattern.

    Identifies the Ladder Bottom candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs at the bottom of a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Ladder Bottom Pattern values.
    """
    return talib.CDLLADDERBOTTOM(open_, high, low, close)

def LONG_LEGGED_DOJI(open_, high, low, close):
    """
    Long Legged Doji Pattern.

    Identifies the Long Legged Doji candlestick pattern based on open, high, low, and close prices.
    This pattern is characterized by long upper and lower shadows with a small body.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Long Legged Doji Pattern values.
    """
    return talib.CDLLONGLEGGEDDOJI(open_, high, low, close)

def LONG_LINE_CANDLE(open_, high, low, close):
    """
    Long Line Candle Pattern.

    Identifies the Long Line Candle candlestick pattern based on open, high, low, and close prices.
    This pattern is characterized by a long body with little or no shadow.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Long Line Candle Pattern values.
    """
    return talib.CDLLONGLINE(open_, high, low, close)

def MARUBOZU(open_, high, low, close):
    """
    Marubozu Pattern.

    Identifies the Marubozu candlestick pattern based on open, high, low, and close prices.
    A Marubozu is a candle with no shadow, indicating strong buying or selling pressure.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Marubozu Pattern values.
    """
    return talib.CDLMARUBOZU(open_, high, low, close)

def MATCHING_LOW(open_, high, low, close):
    """
    Matching Low Pattern.

    Identifies the Matching Low candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs at the bottom of a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Matching Low Pattern values.
    """
    return talib.CDLMATCHINGLOW(open_, high, low, close)

def MAT_HOLD(open_, high, low, close):
    """
    Mat Hold Pattern.

    Identifies the Mat Hold candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs after a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Mat Hold Pattern values.
    """
    return talib.CDLMATHOLD(open_, high, low, close)

def MORNING_DOJI_STAR(open_, high, low, close):
    """
    Morning Doji Star Pattern.

    Identifies the Morning Doji Star candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs at the bottom of a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Morning Doji Star Pattern values.
    """
    return talib.CDLMORNINGDOJISTAR(open_, high, low, close)

def MORNING_STAR(open_, high, low, close):
    """
    Morning Star Pattern.

    Identifies the Morning Star candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs at the bottom of a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Morning Star Pattern values.
    """
    return talib.CDLMORNINGSTAR(open_, high, low, close)

def ON_NECK(open_, high, low, close):
    """
    On-Neck Pattern.

    Identifies the On-Neck candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs after a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        On-Neck Pattern values.
    """
    return talib.CDLONNECK(open_, high, low, close)

def PIERCING(open_, high, low, close):
    """
    Piercing Pattern.

    Identifies the Piercing candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs after a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Piercing Pattern values.
    """
    return talib.CDLPIERCING(open_, high, low, close)

def RICKSHAW_MAN(open_, high, low, close):
    """
    Rickshaw Man Pattern.

    Identifies the Rickshaw Man candlestick pattern based on open, high, low, and close prices.
    This pattern is a type of doji with long upper and lower shadows, often signaling market indecision.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Rickshaw Man Pattern values.
    """
    return talib.CDLRICKSHAWMAN(open_, high, low, close)

def RISING_FALLING_THREE_METHODS(open_, high, low, close):
    """
    Rising/Falling Three Methods Pattern.

    Identifies the Rising or Falling Three Methods candlestick pattern based on open, high, low, and close prices.
    This pattern typically indicates a continuation of the current trend.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Rising/Falling Three Methods Pattern values.
    """
    return talib.CDLRISEFALL3METHODS(open_, high, low, close)

def SEPARATING_LINES(open_, high, low, close):
    """
    Separating Lines Pattern.

    Identifies the Separating Lines candlestick pattern based on open, high, low, and close prices.
    This pattern typically indicates a continuation of the current trend.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Separating Lines Pattern values.
    """
    return talib.CDLSEPARATINGLINES(open_, high, low, close)

def SHOOTING_STAR(open_, high, low, close):
    """
    Shooting Star Pattern.

    Identifies the Shooting Star candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs at the top of an uptrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Shooting Star Pattern values.
    """
    return talib.CDLSHOOTINGSTAR(open_, high, low, close)

def SHORT_LINE_CANDLE(open_, high, low, close):
    """
    Short Line Candle Pattern.

    Identifies the Short Line Candle candlestick pattern based on open, high, low, and close prices.
    This pattern is characterized by a small body with little or no shadow, indicating indecision in the market.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Short Line Candle Pattern values.
    """
    return talib.CDLSHORTLINE(open_, high, low, close)

def SPINNING_TOP(open_, high, low, close):
    """
    Spinning Top Pattern.

    Identifies the Spinning Top candlestick pattern based on open, high, low, and close prices.
    This pattern is characterized by a small body with long upper and lower shadows, indicating indecision in the market.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Spinning Top Pattern values.
    """
    return talib.CDLSPINNINGTOP(open_, high, low, close)

def STALLEDPATTERN(open_, high, low, close):
    """
    Stalled Pattern.

    Identifies the Stalled candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs at the top of an uptrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Stalled Pattern values.
    """
    return talib.CDLSTALLEDPATTERN(open_, high, low, close)

def STICK_SANDWICH(open_, high, low, close):
    """
    Stick Sandwich Pattern.

    Identifies the Stick Sandwich candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs after a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Stick Sandwich Pattern values.
    """
    return talib.CDLSTICKSANDWICH(open_, high, low, close)

def TAKURI(open_, high, low, close):
    """
    Takuri Pattern.

    Identifies the Takuri candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs at the bottom of a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Takuri Pattern values.
    """
    return talib.CDLTASUKIGAP(open_, high, low, close)

def THRUSTING(open_, high, low, close):
    """
    Thrusting Pattern.

    Identifies the Thrusting candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs after a downtrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Thrusting Pattern values.
    """
    return talib.CDLTHRUSTING(open_, high, low, close)

def TRISTAR(open_, high, low, close):
    """
    Tristar Pattern.

    Identifies the Tristar candlestick pattern based on open, high, low, and close prices.
    This pattern typically consists of three Doji candles and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Tristar Pattern values.
    """
    return talib.CDLTRISTAR(open_, high, low, close)

def UNIQUE_3_RIVER(open_, high, low, close):
    """
    Unique 3 River Pattern.

    Identifies the Unique 3 River candlestick pattern based on open, high, low, and close prices.
    This pattern typically consists of three candles and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Unique 3 River Pattern values.
    """
    return talib.CDLUNIQUE3RIVER(open_, high, low, close)

def UPSIDE_GAP_TWO_CROWS(open_, high, low, close):
    """
    Upside Gap Two Crows Pattern.

    Identifies the Upside Gap Two Crows candlestick pattern based on open, high, low, and close prices.
    This pattern typically occurs after an uptrend and may indicate a potential reversal.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        Upside Gap Two Crows Pattern values.
    """
    return talib.CDLUPSIDEGAP2CROWS(open_, high, low, close)

def X_SIDE_GAP_3_METHODS(open_, high, low, close):
    """
    X-Side Gap Three Methods Pattern.

    Identifies the X-Side Gap Three Methods candlestick pattern based on open, high, low, and close prices.
    This pattern typically indicates a continuation of the current trend.

    :param open_: array-like
        Array of opening prices.
    :param high: array-like
        Array of high prices.
    :param low: array-like
        Array of low prices.
    :param close: array-like
        Array of closing prices.

    :return: numpy.ndarray
        X-Side Gap Three Methods Pattern values.
    """
    return talib.CDLXSIDEGAP3METHODS(open_, high, low, close)