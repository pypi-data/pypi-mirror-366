import random
import time

from tqdm import tqdm

from xno.platform.ta.docs import get_function_docs
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

from xno.platform.ta.expressions import submit_ta_expression
from xno.platform.ta.stocks import get_available_stocks


exps = [
    "IF(OR("
    "AND("
    "Close > HIGHEST(Close, 20) * 0.985, "
    "Low <= LOWEST(Low, 10), "
    "Close > Open, "
    "Volume > MA(Volume, 20) * 1.5, "
    "RSI(Close, 14) > 35, RSI(Close, 14) < 65"
    "), "
    "AND("
    "Close > EMA(Close, 21), "
    "Low > LOWEST(Low, 5), "
    "Close > REF(High, 2), "
    "Volume > MA(Volume, 10) * 1.3, "
    "STOCH_K(High, Low, Close) < 80"
    "), "
    "AND("
    "Low < LOWEST(Low, 15), "
    "Close > (High + Low) / 2, "
    "Close > REF(Close, 1), "
    "Volume > MA(Volume, 20) * 2.0, "
    "RSI(Close, 14) < 50"
    "), "
    "AND("
    "Close > HIGHEST(Close, 10), "
    "Close > HIGHEST(High, 5), "
    "Volume > MA(Volume, 20) * 1.4, "
    "RSI(Close, 14) > 40, RSI(Close, 14) < 70, "
    "EMA(Close, 9) > EMA(Close, 21)"
    ")"
    "), 3, "
    "IF(OR("
    "AND("
    "Close < LOWEST(Close, 20) * 1.015, "
    "High >= HIGHEST(High, 10), "
    "Close < Open, "
    "Volume > MA(Volume, 20) * 1.5, "
    "RSI(Close, 14) > 35, RSI(Close, 14) < 65"
    "), "
    "AND("
    "Close < EMA(Close, 21), "
    "High < HIGHEST(High, 5), "
    "Close < REF(Low, 2), "
    "Volume > MA(Volume, 10) * 1.3, "
    "STOCH_K(High, Low, Close) > 20"
    "), "
    "AND("
    "High > HIGHEST(High, 15), "
    "Close < (High + Low) / 2, "
    "Close < REF(Close, 1), "
    "Volume > MA(Volume, 20) * 2.0, "
    "RSI(Close, 14) > 50"
    "), "
    "AND("
    "Close < LOWEST(Close, 10), "
    "Close < LOWEST(Low, 5), "
    "Volume > MA(Volume, 20) * 1.4, "
    "RSI(Close, 14) > 30, RSI(Close, 14) < 60, "
    "EMA(Close, 9) < EMA(Close, 21)"
    ")"
    "), -3, "
    "IF(OR("
    "AND("
    "Close > EMA(Close, 50), "
    "RSI(Close, 14) < 45, "
    "Close > EMA(Close, 21), "
    "Volume > MA(Volume, 20) * 1.2, "
    "STOCH_K(High, Low, Close) < 50"
    "), "
    "AND("
    "Close < EMA(Close, 50) * 1.02, "
    "Close > EMA(Close, 50) * 0.98, "
    "RSI(Close, 14) < 40, "
    "Volume > MA(Volume, 15) * 1.1, "
    "Close > REF(Close, 1)"
    "), "
    "AND("
    "Close > LOWEST(Close, 20) * 1.01, "
    "Volume > MA(Volume, 10) * 1.6, "
    "RSI(Close, 14) > 30, RSI(Close, 14) < 55, "
    "Close > (Open + Close) / 2"
    ")"
    "), 2, "
    "IF(OR("
    "AND("
    "Close < EMA(Close, 50), "
    "RSI(Close, 14) > 55, "
    "Close < EMA(Close, 21), "
    "Volume > MA(Volume, 20) * 1.2, "
    "STOCH_K(High, Low, Close) > 50"
    "), "
    "AND("
    "Close > EMA(Close, 50) * 0.98, "
    "Close < EMA(Close, 50) * 1.02, "
    "RSI(Close, 14) > 60, "
    "Volume > MA(Volume, 15) * 1.1, "
    "Close < REF(Close, 1)"
    "), "
    "AND("
    "Close < HIGHEST(Close, 20) * 0.99, "
    "Volume > MA(Volume, 10) * 1.6, "
    "RSI(Close, 14) > 45, RSI(Close, 14) < 70, "
    "Close < (Open + Close) / 2"
    ")"
    "), -2, "
    "IF(OR("
    "AND("
    "EMA(Close, 9) > EMA(Close, 21), "
    "RSI(Close, 14) > 40, RSI(Close, 14) < 60, "
    "Volume > MA(Volume, 20), "
    "Close > REF(Close, 2)"
    "), "
    "AND("
    "ABS(Close - Open) < (High - Low) * 0.3, "
    "Volume > MA(Volume, 10) * 1.1, "
    "RSI(Close, 14) > 35, RSI(Close, 14) < 65"
    ")"
    "), 1, "
    "IF(OR("
    "AND("
    "EMA(Close, 9) < EMA(Close, 21), "
    "RSI(Close, 14) > 40, RSI(Close, 14) < 60, "
    "Volume > MA(Volume, 20), "
    "Close < REF(Close, 2)"
    "), "
    "AND("
    "ABS(Close - Open) < (High - Low) * 0.3, "
    "Volume > MA(Volume, 10) * 1.1, "
    "Close < EMA(Close, 21)"
    ")"
    "), -1, 0))))))"
]

def main():
    # call several times for unique ideas
    for stock_symbol in tqdm(get_available_stocks()):
        rs = submit_ta_expression(
            expression=exps[0],
            symbol=stock_symbol,
            resolution="D",
            from_time="2020-01-01",
            to_time="2024-01-01",
            strategy_name="SMC Technical Alpha",
            description="A novel trading strategy based on SMC principles and technical indicators.",
        )
        time.sleep(0.1)



if __name__ == "__main__":
    main()
