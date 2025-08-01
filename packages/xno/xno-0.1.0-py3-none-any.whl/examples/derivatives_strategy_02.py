
from xno.algo.dv import DerivativeAlgorithm


class MyAlgorithm(DerivativeAlgorithm):
    def __setup__(self):
        self._name = "My VN30F1M Algorithm"
        self._ticker = "VN30F1M"
        self._resolution = "60min"
        self._from_time = "2025-01-01 09:00:00"
        self._to_time = "2025-07-30 15:00:00"
        self._init_cash = 500_000_000
        self._slippage = 0.05

    def __algorithm__(self):
        # Indicators
        wma = self._features.wma(self.Close, 20)

        sell_signal = self.crossed_below(self.Close, wma)
        buy_signal = self.crossed_below(wma, self.Close)
        # Set the buy and sell signals
        self.buy(buy_signal, 1)
        self.sell(sell_signal, 1)

if __name__ == "__main__":
    algo = MyAlgorithm()
    algo.run()
    algo.visualize()
    print("Algorithm run completed.")
