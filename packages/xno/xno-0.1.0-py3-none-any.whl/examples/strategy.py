import os
from pathlib import Path

# Load environment variables from .env file FIRST, before any XNO imports
def load_env_file():
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables before importing XNO modules
load_env_file()

# Now import XNO modules after environment is loaded
from xno.algo.st import StockAlgorithm


class MyAlgorithm(StockAlgorithm):
    def __setup__(self):
        self._name = "My SHB Algorithm"
        self._ticker = "SHB"
        self._resolution = "D"
        self._from_time = "2020-01-01"
        self._to_time = "2025-07-04"
        self._init_cash = 500_000_000
        self._slippage = 0.05

    def __algorithm__(self):
        # Indicators
        rsi = self._features.rsi()
        adx = self._features.adx()

        # The logical AND operator can be used directly by using `&` or `self.And()`
        buy_signal = (self.current(rsi) > self.previous(rsi)) & (self.current(adx) < self.previous(adx))

        # you can also use `self.And()` for logical AND
        sell_signal = self.And(self.current(rsi) < self.previous(rsi), self.current(adx) > self.previous(adx))

        # Set the buy and sell signals
        self.buy(buy_signal, 1)
        self.sell(sell_signal, 1)

if __name__ == "__main__":
    algo = MyAlgorithm()
    algo.run()
    algo.visualize()
    print("Algorithm run completed.")
