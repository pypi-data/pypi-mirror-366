
from xno.algo.dv import DerivativeAlgorithm


class MyAlgorithm(DerivativeAlgorithm):
    def __setup__(self):
        self._name = "My VN30F1M Algorithm"
        self._ticker = "VN30F1M"
        self._resolution = "15min"
        self._from_time = "2025-07-04 09:00:00"
        self._to_time = "2025-07-10 15:00:00"
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
