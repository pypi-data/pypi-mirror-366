import random
import time

from xno.platform.ta.docs import get_function_docs
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

from xno.platform.ta.expressions import submit_ta_expression
from xno.platform.ta.stocks import get_available_stocks


class TechnicalAlphaModel(BaseModel):
    idea: str = Field(..., description="A brief description of the trading strategy idea in 1-3 sentences.")
    name: str = Field(..., description="A short and descriptive name for the strategy, under 5 words.")
    formula: str = Field(..., description="The trading strategy formula in a single line without any line breaks or extra formatting.")


prompt = f"""
You are an expert in technical analysis and trading strategies, specializing in using technical indicators to create actionable trading plans. Your task is to provide trading strategies based on the provided technical indicators, functions, and their parameters. You must follow the following rules:  
**Rules**:  
    - Respond in English.  
    - Always provide a strategy idea in 1-3 sentences.  
    - Always provide a strategy name, which is a short and descriptive name for the strategy, under 5 words.  
    - Only use the provided technical indicators and their parameters to create the strategy. Do not use or make up your own indicators or parameters.  
    - Provide the strategy in a single line without any line breaks or extra formatting.  
    - Follow the examples format, which is similar to Microsoft Excel formulas. The function must be in UPPER_CASE, and the parameters must be lowercase and separated by commas.  
    - The series only accept Open, High, Low, Close, Volume. The name of the series must be capitalized (e.g., Open, High, Low, Close, Volume).  
    - You can create derived series, such as (High + Low) / 2 or (High + Low + Close) / 3, but these must be used as inputs to the provided indicators or functions.  
=========  
**Examples**:  
    - Name: Dual MA Price Mix  
    - Idea: Go long when the 10-period moving average of the mid-price (High + Low) crosses above the 50-period moving average of the close, and short when the 50-period MA of the close crosses above the 10-period MA of the close.  
    - Formula: `IF(CROSS(MA((High + Low) / 2, timeperiod=10), MA(Close, timeperiod=50)), 1, IF(CROSS(MA(Close, timeperiod=50), MA(Close, timeperiod=10)), -1, 0))`
    
    - Name: Volatility Squeeze Play  
    - Idea: Go long when the close crosses above the upper Bollinger Band of the average price, indicating a breakout after a squeeze, and go short when the close drops below the lower Bollinger Band.  
    - Formula: `IF(CROSS(Close, BBANDS_UP((High + Low + Close) / 3, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)), 1, IF(CROSS(BBANDS_LOW((High + Low + Close) / 3, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0), Close), -1, 0))`
    
    - Name: Momentum RSI Shift  
    - Idea: Go long when the RSI crosses above 30 indicating a bullish momentum shift, and go short when RSI crosses below 70 indicating bearish reversal from overbought levels.  
    - Formula: `IF(CROSS(RSI(Close, timeperiod=14), 30), 1, IF(CROSS(70, RSI(Close, timeperiod=14)), -1, 0))`
    
    - Name: Mean Reversion Zone  
    - Idea: Go long when the Close price crosses above its 10-window rolling minimum, indicating recovery from a short-term bottom; short when it crosses below the 10-window rolling maximum.  
    - Formula: `IF(CROSS(Close, ROLLING_MIN(Close, window=10)), 1, IF(CROSS(ROLLING_MAX(Close, window=10), Close), -1, 0))`
    
    - Name: MACD Trend Reversal  
    - Idea: Go long when the MACD histogram crosses above zero showing bullish reversal, and short when it crosses below zero indicating bearish momentum.  
    - Formula: `IF(CROSS(MACD_HIST(Close, fastperiod=12, slowperiod=26, signalperiod=9), 0), 1, IF(CROSS(0, MACD_HIST(Close, fastperiod=12, slowperiod=26, signalperiod=9)), -1, 0))`
    
    - Name: Rolling Mean Flip  
    - Idea: Enter long when the Close price rises above its 20-period rolling mean, signalling upward momentum; enter short when the Close drops below the same rolling mean, indicating a potential downturn.  
    - Formula: `IF(CROSS(Close, ROLLING_MEAN(Close, window=20)), 1, IF(CROSS(ROLLING_MEAN(Close, window=20), Close), -1, 0))`
    
    - Name: ADX Momentum Filter  
    - Idea: Go long when the 14-period RSI crosses above 50 while ADX is above 25, signaling strong bullish momentum; go short when RSI crosses below 50 under the same ADX condition.  
    - Formula: `IF(AND(ADX(High, Low, Close, timeperiod=14) > 25, CROSS(RSI(Close, timeperiod=14), 50)), 1, IF(AND(ADX(High, Low, Close, timeperiod=14) > 25, CROSS(50, RSI(Close, timeperiod=14))), -1, 0))`
    
    - Name: StochRSI Mean Break  
    - Idea: Go long when StochRSI_D crosses above 20 from below, indicating a rebound from oversold; short when it crosses below 80, signaling a drop from overbought levels.  
    - Formula: `IF(CROSS(STOCHRSI_D(Close, timeperiod=14, fastk_period=5, fastd_period=3), 20), 1, IF(CROSS(80, STOCHRSI_D(Close, timeperiod=14, fastk_period=5, fastd_period=3)), -1, 0))`
    
    - Name: OBV Trend Confirmation  
    - Idea: Go long when OBV rises above its 30-period EMA and price closes above its 20-period MA; short when OBV falls below EMA and price closes below the MA.  
    - Formula: `IF(AND(OBV(Close, Volume) > EMA(OBV(Close, Volume), timeperiod=30), Close > MA(Close, timeperiod=20)), 1, IF(AND(OBV(Close, Volume) < EMA(OBV(Close, Volume), timeperiod=30), Close < MA(Close, timeperiod=20)), -1, 0))`
    
    - Name: Volume Spike Reversal  
    - Idea: Go long when Close rises above its 10-period minimum during a volume surge (150% above 20-period average); short when Close falls below its 10-period maximum under the same volume condition.  
    - Formula: `IF(Volume > ROLLING_MEAN(Volume, window=20) * 1.5, IF(CROSS(Close, ROLLING_MIN(Close, window=10)), 1, IF(CROSS(ROLLING_MAX(Close, window=10), Close), -1, 0)), 0)`

    - Name: ATR Breakout Pulse
    - Idea: Go long when Close rises above its previous day’s close by more than 1.5× ATR, signaling a volatility-based breakout; go short when the drop exceeds 1.5× ATR.
    - Formula: IF(Close - REF(Close, periods=1) > ATR(High, Low, Close, timeperiod=14) * 1.5, 1, IF(REF(Close, periods=1) - Close > ATR(High, Low, Close, timeperiod=14) * 1.5, -1, 0))

    - Name: Decay Momentum Entry
    - Idea: Go long when DECAY_LINEAR of ROC turns up sharply after declining, indicating short-term momentum pickup; short when it turns down.
    - Formula: IF(CROSS(DECAY_LINEAR(ROC(Close, timeperiod=10), window=10), REF(DECAY_LINEAR(ROC(Close, timeperiod=10), window=10), periods=1)), 1, IF(CROSS(REF(DECAY_LINEAR(ROC(Close, timeperiod=10), window=10), periods=1), DECAY_LINEAR(ROC(Close, timeperiod=10), window=10)), -1, 0))
=========  
**Available Indicators and Functions**:  
    {'\n'.join([f'- Signature: {x.sig}\n' for x in get_function_docs()])}
=========  
Using the provided indicators and functions, create unique trading strategy that adheres to the rules and format specified above. Ensure the strategy is novel and not a repetition of the examples provided.  
**Response**:
"""

print(prompt)

def main(runs):
    # call several times for unique ideas
    for i in range(runs):
        list_symbols = [s.strip() for s in open("stocks.txt", 'r').readlines()]
        # list_symbols = ['GEE']
        print("=========================")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=1,  # more creative
        )
        structured_llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=1,  # more creative
        )
        structured_llm = structured_llm.with_structured_output(TechnicalAlphaModel)
        rp = llm.invoke(prompt)
        result = structured_llm.invoke(rp.content)
        print(f"\nRun {i+1}")
        print(f"- Name: {result.name}")
        print(f"- Idea: {result.idea}")
        print(f"- Formula: {result.formula}")
        for stock in list_symbols:
            rs = submit_ta_expression(
                expression=result.formula,
                symbol=stock,
                resolution="D",
                from_time="2020-01-01",
                to_time="2024-01-01",
                strategy_name=result.name,
                description=result.idea,
                initial_cash=100_000_000.0,  # initial cash
            )
            print(f"Submit to XNO, symbol = {stock}. Success = {True if rs is not None else False}")

            time.sleep(0.1)


if __name__ == "__main__":
    main(runs=100)
