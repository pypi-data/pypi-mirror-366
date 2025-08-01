# xno/algo/dv.py
from abc import abstractmethod

import numpy as np

from xno.algo._base import Algorithm, HistoryRecord


class DerivativeAlgorithm(Algorithm):
    _price_scale = 1  # Default price scale, can be overridden in subclasses

    def __init__(self):
        super().__init__()
        self._contract_price = 25_000_000
        self._max_contracts = None
        self._fixed_fee = 20_000
        self._value_per_contract = 100_000

    @abstractmethod
    def __setup__(self):
        raise NotImplementedError("DerivativeAlgorithm must implement __setup__ method")

    @abstractmethod
    def __algorithm__(self):
        raise NotImplementedError("DerivativeAlgorithm must implement __algorithm__ method")

    def __reset__(self):
        super().__reset__()
        self._max_contracts = self._init_cash // self._contract_price
        # Update the benchmark portfolio value (Buy and Hold strategy)
        self._bm_open_size = self._max_contracts
        bm_fee = self._max_contracts * self._fixed_fee
        self._bm_equity -= bm_fee

    def __step__(self, time_idx: int):
        """
        Run the trading algorithm state, which includes setting up the algorithm, generating signals, and verifying the trading signal.

        Rules enforced:
        1. Can be sell before buy, e.g. the short position.
        """
        super().__step__(time_idx)  # Call the base step method to update the current time index
        current_action = "H"  # Default action is hold
        current_signal = 0.0
        current_trade_size = 0.0
        current_fee = 0.0  # Placeholder for fee, can be updated later
        current_price = self._ht_prices[self._current_time_idx]  # Get the current price from the history prices]
        current_time = self._ht_times[self._current_time_idx]   # Current day from the timestamp
        # The signal unverified, which is the current signal at the current time index
        sig: float = self._signals.values[self._current_time_idx]
        # Calculate the benchmark shares based on initial cash and current price
        current_max_shares = sig * self._max_contracts  # Calculate the maximum shares based on the signal and max contracts

        # Get the previous price from this history
        prev_price = self._ht_prices[self._current_time_idx - 1] if self._current_time_idx > 0 else current_price
        price_diff = current_price - prev_price  # Calculate the price difference

        # Update the PnL based on the current and previous prices
        current_pnl = self._current_open_size * price_diff * self._value_per_contract
        bm_pnl = self._bm_open_size * price_diff * self._value_per_contract  # Update benchmark PnL based on current price and initial price

        # Calculate the current action based on the signal

        # Handle sell logic
        if sig == 0:
            # Skip if no change in position
            pass
        else:
            target_position = np.clip(self._current_position + sig, -1, 1)
            updated_position = target_position - self._current_position  # Calculate the change in position
            if updated_position != 0:
                current_trade_size = abs(updated_position) * self._max_contracts
                current_fee = current_trade_size * self._fixed_fee  # Calculate fee based on updated position
                current_pnl -= current_fee  # Deduct fee from current PnL
                self._current_position += updated_position  # Update the current position
                if updated_position > 0:
                    current_action = "B"
                    self._current_open_size += current_trade_size
                else:
                    current_action = "S"
                    self._current_open_size -= current_trade_size

        self._current_equity += current_pnl     # Update current equity with PnL
        self._bm_equity += bm_pnl               # Update benchmark equity with benchmark PnL
        # Update the result record the current state
        self._bt_results.append(
            HistoryRecord(
                time=current_time,
                current_tick=self._current_time_idx,
                action=current_action,
                signal=current_signal,
                amount=current_trade_size,
                price=current_price,
                value=self._current_open_size * self._contract_price,  # Current value of the open position
                fee=current_fee,
                equity=self._current_equity,
                bm_equity=self._bm_equity,
                step_ret=0,
                cum_ret= 0,
                bm_step_ret= 0,
                bm_cum_ret=0  # Placeholder for returns, will be calculated later
            )
        )
