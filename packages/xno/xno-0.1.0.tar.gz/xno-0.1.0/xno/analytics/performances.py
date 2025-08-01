import numpy as np
import pandas as pd
import quantstats as qs

class StrategyPerformance:
    def __init__(self, returns: pd.Series | np.ndarray):
        """
        Initialize the performance metrics with the returns data.

        :param returns: A pandas Series or numpy array of returns.
        """
        if isinstance(returns, np.ndarray):
            returns = pd.Series(returns)

        if not isinstance(returns, pd.Series):
            raise TypeError("Returns must be a pandas Series or numpy array.")

        # Clean returns
        self.returns = returns.replace([np.inf, -np.inf], np.nan).dropna()
        self.trading_days = 252

    @property
    def summary(self):
        """
        Generate a summary of the performance metrics.
        """
        return {
            "avg_return": qs.stats.avg_return(self.returns),
            "cumulative_return": qs.stats.comp(self.returns),
            "cvar": qs.stats.cvar(self.returns),
            "gain_to_pain_ratio": qs.stats.gain_to_pain_ratio(self.returns),
            "kelly_criterion": qs.stats.kelly_criterion(self.returns),
            "max_drawdown": qs.stats.max_drawdown(self.returns),
            "omega": qs.stats.omega(self.returns),
            "profit_factor": qs.stats.profit_factor(self.returns),
            "recovery_factor": qs.stats.recovery_factor(self.returns),
            "sharpe": qs.stats.sharpe(self.returns),
            "sortino": qs.stats.sortino(self.returns),
            "tail_ratio": qs.stats.tail_ratio(self.returns),
            "ulcer_index": qs.stats.ulcer_index(self.returns),
            "var": qs.stats.value_at_risk(self.returns),
            "volatility": qs.stats.volatility(self.returns),
            "win_loss_ratio": qs.stats.win_loss_ratio(self.returns),
            "win_rate": qs.stats.win_rate(self.returns),
        }
