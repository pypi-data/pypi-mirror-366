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

class MomentumBreakoutStrategy(StockAlgorithm):
    """
    Momentum breakout strategy using multiple timeframes
    Buy on breakout above resistance with volume confirmation
    Sell on momentum exhaustion or stop loss
    """
    def __setup__(self):
        self._name = "Momentum Breakout Strategy"
        self._ticker = "VIC"
        self._resolution = "D"
        self._from_time = "2021-06-01"
        self._to_time = "2025-07-30"
        self._init_cash = 1_200_000_000
        self._slippage = 0.025

    def __algorithm__(self):
        # Price data - use property methods
        close = self.Close
        high = self.High
        
        # Momentum indicators
        roc = self._features.roc(timeperiod=10)  # Rate of change
        rsi = self._features.rsi(timeperiod=14)
        
        # Volatility
        atr = self._features.atr(timeperiod=14)
        
        # Resistance levels (highest high in last 20 periods)
        resistance = self._features.max(high, timeperiod=20)
        
        # Breakout conditions
        breakout = self.current(high) > self.previous(resistance)
        momentum_strong = self.current(roc) > 5  # 5% rate of change
        rsi_not_overbought = self.current(rsi) < 80
        
        # Buy on breakout with confirmations
        buy_signal = breakout & momentum_strong & rsi_not_overbought
        
        # Sell conditions
        momentum_weak = self.current(roc) < -3  # Negative momentum
        rsi_overbought = self.current(rsi) > 85
        
        sell_signal = momentum_weak | rsi_overbought
        
        # Execute trades
        self.buy(buy_signal, 1)
        self.sell(sell_signal, 1)

if __name__ == "__main__":
    algo = MomentumBreakoutStrategy()
    algo.run()
    algo.visualize()
    print("Momentum Breakout Strategy completed.")
