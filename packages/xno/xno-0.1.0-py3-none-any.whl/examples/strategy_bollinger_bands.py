import os
from pathlib import Path

# Load environment variables from .env file FIRST, before any XNO imports
def load_env_file():
    env_path = Path(__file__).parent.parent / '.env'  # Go up one level to project root
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables before importing XNO modules
load_env_file()

from xno.algo.st import StockAlgorithm

class BollingerBandStrategy(StockAlgorithm):
    """
    Bollinger Band mean reversion strategy
    Buy when price touches lower band with RSI oversold
    Sell when price touches upper band with RSI overbought
    """
    def __setup__(self):
        self._name = "Bollinger Band Reversion"
        self._ticker = "HPG"
        self._resolution = "D"
        self._from_time = "2021-01-01"
        self._to_time = "2025-07-30"
        self._init_cash = 800_000_000
        self._slippage = 0.04

    def __algorithm__(self):
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._features.bbands(timeperiod=20, nbdevup=2, nbdevdn=2)
        
        # RSI for confirmation
        rsi = self._features.rsi(timeperiod=14)
        
        # MACD for trend confirmation
        macd, macd_signal, macd_hist = self._features.macd()
        
        # Price relative to bands - use Close property
        close = self.Close
        
        # Buy signals: Price near lower band + oversold RSI + bullish MACD
        buy_signal = (
            (self.current(close) <= self.current(bb_lower) * 1.02) &  # Near lower band
            (self.current(rsi) < 30) &  # Oversold
            (self.current(macd_hist) > self.previous(macd_hist))  # MACD improving
        )
        
        # Sell signals: Price near upper band + overbought RSI
        sell_signal = (
            (self.current(close) >= self.current(bb_upper) * 0.98) &  # Near upper band
            (self.current(rsi) > 70)  # Overbought
        )
        
        # Execute trades
        self.buy(buy_signal, 1)
        self.sell(sell_signal, 1)

if __name__ == "__main__":
    algo = BollingerBandStrategy()
    algo.run()
    algo.visualize()
    print("Bollinger Band Strategy completed.")
