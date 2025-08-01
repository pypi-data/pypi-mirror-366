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

class MultiIndicatorStrategy(StockAlgorithm):
    """
    Advanced multi-indicator strategy combining trend, momentum, and volatility
    Uses ensemble approach for signal generation
    """
    def __setup__(self):
        self._name = "Multi-Indicator Ensemble"
        self._ticker = "VNM"
        self._resolution = "D"
        self._from_time = "2020-01-01"
        self._to_time = "2025-07-30"
        self._init_cash = 1_500_000_000
        self._slippage = 0.02

    def __algorithm__(self):
        # Trend indicators
        ema_fast = self._features.ema(timeperiod=12)
        ema_slow = self._features.ema(timeperiod=26)
        adx = self._features.adx(timeperiod=14)
        
        # Momentum indicators
        rsi = self._features.rsi(timeperiod=14)
        macd, macd_signal, macd_hist = self._features.macd()
        stoch_k, stoch_d = self._features.stoch()
        
        # Volatility indicators
        bb_upper, bb_middle, bb_lower = self._features.bbands(timeperiod=20)
        atr = self._features.atr(timeperiod=14)
        
        # Price action - use property method
        close = self.Close
        
        # Define individual signal conditions using boolean operators
        # Trend signals
        uptrend = self.current(ema_fast) > self.current(ema_slow)
        strong_trend = self.current(adx) > 25
        
        # Momentum signals  
        bullish_rsi = (self.current(rsi) > 50) & (self.current(rsi) < 70)
        macd_bullish = self.current(macd_hist) > 0
        
        # Volatility signals
        above_bb_middle = self.current(close) > self.current(bb_middle)
        stoch_good_range = (self.current(stoch_k) > 20) & (self.current(stoch_k) < 80)
        
        # Buy signal: Need multiple confirmations
        buy_signal = self.And(
            uptrend,
            strong_trend,
            bullish_rsi,
            macd_bullish
        )
        
        # Sell conditions
        downtrend = self.current(ema_fast) < self.current(ema_slow)
        weak_trend = self.current(adx) < 20
        rsi_extreme = (self.current(rsi) > 70) | (self.current(rsi) < 30)
        macd_bearish = self.current(macd_hist) < 0
        below_bb_lower = self.current(close) < self.current(bb_lower)
        stoch_overbought = self.current(stoch_k) > 80
        
        # Sell signal: Any major warning sign
        sell_signal = downtrend | weak_trend | rsi_extreme | below_bb_lower | stoch_overbought
        
        # Execute trades
        self.buy(buy_signal, 1)
        self.sell(sell_signal, 1)

if __name__ == "__main__":
    algo = MultiIndicatorStrategy()
    algo.run()
    algo.visualize()
    print("Multi-Indicator Strategy completed.")
