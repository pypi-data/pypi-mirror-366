import os
from pathlib import Path
import numpy as np

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

class MovingAverageCrossoverStrategy(StockAlgorithm):
    """
    Strategy using SMA crossover signals
    Buy when fast SMA crosses above slow SMA
    Sell when fast SMA crosses below slow SMA
    """
    def __setup__(self):
        self._name = "SMA Crossover Strategy"
        self._ticker = "VHM"
        self._resolution = "D"
        self._from_time = "2022-01-01"
        self._to_time = "2025-07-30"
        self._init_cash = 1_000_000_000
        self._slippage = 0.03

    def __algorithm__(self):
        # Moving averages
        sma_fast = self._features.sma(timeperiod=10)
        sma_slow = self._features.sma(timeperiod=30)
        
        # Simple crossover signals (removing volume confirmation for now)
        buy_signal = self.crossed_above(sma_fast, sma_slow)
        sell_signal = self.crossed_below(sma_fast, sma_slow)
        
        # Execute trades
        self.buy(buy_signal, 1)
        self.sell(sell_signal, 1)

if __name__ == "__main__":
    algo = MovingAverageCrossoverStrategy()
    algo.run()
    algo.visualize()
    print("Moving Average Crossover Strategy completed.")
