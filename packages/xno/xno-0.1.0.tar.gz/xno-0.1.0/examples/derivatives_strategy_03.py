
from xno.algo.dv import DerivativeAlgorithm


class RsiMeanReversion(DerivativeAlgorithm):
    def __setup__(self):
        self._name = "RSI Mean Reversion"
        self._ticker = "VN30F1M"
        self._resolution = "5min"
        self._from_time = "2025-01-01 09:00:00"
        self._to_time = "2025-08-31 15:00:00"
        self._init_cash = 500_000_000
        self._slippage = 0.05

    def __algorithm__(self):
        rsi = self._features.rsi(self.Close, 14)
        buy_signal = self.crossed_below(rsi, 30)
        sell_signal = self.crossed_above(rsi, 70)
        self.buy(buy_signal, 1)
        self.sell(sell_signal, 1)


if __name__ == "__main__":
    algo = RsiMeanReversion()
    algo.run()
    algo.visualize()
    print("Algorithm run completed.")
