# xno/algo/st.py
from abc import abstractmethod
from xno.algo._base import Algorithm, HistoryRecord
import logging


def round_to_lot(value, lot_size):
    """Round value to the nearest lot size."""
    remainder = value % lot_size
    if remainder < lot_size / 2:
        return int(value - remainder)
    else:
        return int(value + (lot_size - remainder))


class StockAlgorithm(Algorithm):
    _stock_lot_size = 100  # Default stock lot size, can be overridden in subclasses
    _price_scale = 1000  # Default price scale, can be overridden in subclasses

    def __init__(self):
        super().__init__()
        # Init the state of stock algorithm
        self._init_fee = 0.001
        self._t0_size: float = 0.0            # T+0 position size
        self._t1_size: float = 0.0            # T+1 position size
        self._t2_size: float = 0.0            # T+2 position size
        self._sell_size: float = 0.0          # Sell position size
        self._pending_sell_pos: float = 0.0  # Track if there is a pending sell position to be executed later

    @abstractmethod
    def __setup__(self):
        raise NotImplementedError("StockAlgorithm must implement __setup__ method")

    @abstractmethod
    def __algorithm__(self):
        raise NotImplementedError("StockAlgorithm must implement __algorithm__ method")

    def __reset__(self):
        super().__reset__()
        # Update the benchmark portfolio value (Buy and Hold strategy)
        self._bm_open_size = round_to_lot(self._init_cash // self._init_price, self._stock_lot_size)  # Calculate benchmark shares based on initial cash and current price
        bm_fee = self._init_price * self._bm_open_size * self._init_fee  # Recalculate benchmark fee based on shares and initial price
        self._bm_equity -= bm_fee

    def __step__(self, time_idx: int):
        """
        Run the trading algorithm state, which includes setting up the algorithm, generating signals, and verifying the trading signal.

        Rules enforced:
        1. Cannot sell more than the current open position.
        2. Cannot sell before any buying has occurred.
        3. Sell is only allowed after holding for at least 3 days (T+3 logic).
        4. Shares are rounded down to the nearest stock lot size.
        5. Shares are computed based on the initial cash, current price, and lot size.
        6. If conditions for selling are not met, the signal is ignored until eligible.
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
        current_max_shares = round_to_lot(self._init_cash // current_price, self._stock_lot_size)

        # Get the previous price from this history
        prev_price = self._ht_prices[self._current_time_idx - 1] if self._current_time_idx > 0 else current_price
        # Update the PnL based on the current and previous prices
        current_pnl = self._current_open_size * (current_price - prev_price) # Calculate PnL based on current and previous prices
        bm_pnl = self._bm_open_size * (current_price - prev_price)  # Update benchmark PnL based on current price and initial price

        # Calculate day difference AND update T0, T1, T2 positions based on the previous day
        prev_time = self._ht_times[self._current_time_idx - 1]  if self._current_time_idx > 0 else current_time  # Previous day for the first iteration
        day_diff = (current_time - prev_time).days
        if day_diff > 0:
            logging.debug(f"Update T0, T1, T2 for {current_time}, T0: {self._t0_size}, T1: {self._t1_size}, T2: {self._t2_size}, Sell Position: {self._sell_size}")
            # Consecutive prev_day days
            self._sell_size += self._t2_size
            self._t2_size = self._t1_size
            self._t1_size = self._t0_size
            self._t0_size = 0

        # Calculate the current action based on the signal
        if sig > 0:
            updated_position = min(sig - self._current_position, 1 - self._current_position)
        elif sig < 0:
            if self._current_position > 0:
                updated_position = max(sig - self._current_position, -self._current_position)  # Can reduce or reverse only what we own
            else:
                updated_position = 0.0  # Can't sell if we have no position
        else:
            updated_position = 0.0

        # Handle sell logic
        if updated_position == 0:
            # Skip if no change in position
            pass
        elif updated_position < 0 or self._pending_sell_pos > 0:
            logging.debug(f"Entering sell logic at {current_time} with weight {sig}")
            if self._sell_size == 0:
                logging.warning(f"Sell position is 0, but trying to sell {sig} at {current_time}. This will be ignored, please waiting for the next timestamp to sell.")
                self._pending_sell_pos += abs(sig)  # Track pending sell position
            else:
                can_sell_position = max(self._pending_sell_pos, abs(updated_position))
                current_trade_size = min(
                    self._sell_size,
                    round_to_lot(can_sell_position * self._current_open_size, self._stock_lot_size)
                )  # Ensure we don't sell more than we have
                self._sell_size -= current_trade_size
                self._current_open_size -= current_trade_size  # Update total shares held
                current_signal = -can_sell_position
                self._current_position -= can_sell_position
                self._pending_sell_pos = max(self._pending_sell_pos - can_sell_position, 0)  # Reduce pending sell position
                current_action = "S"  # Set action to sell
                current_fee = current_price * current_trade_size * self._init_fee  # Calculate fee based on trade size
                current_pnl -= current_fee
        elif updated_position > 0: # Handle buy logic
            logging.debug(f"Entering buy logic at {current_time} with weight {sig}")
            self._current_position += updated_position  # Update current position
            current_trade_size = round_to_lot(updated_position * current_max_shares, self._stock_lot_size)
            self._t0_size += current_trade_size  # Update T0 position
            self._current_open_size += current_trade_size  # Update total shares held
            current_action = "B"  # Set action to buy
            current_signal = updated_position  # Update current signal
            current_fee = current_price * current_trade_size * self._init_fee  # Calculate fee based on trade size
            current_pnl -= current_fee

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
                value=self._current_open_size * current_price,  # Current value of the open position
                fee=current_fee,
                equity=self._current_equity,
                bm_equity=self._bm_equity,
                step_ret=0, cum_ret= 0, bm_step_ret= 0, bm_cum_ret=0  # Placeholder for returns, will be calculated later
            )
        )
