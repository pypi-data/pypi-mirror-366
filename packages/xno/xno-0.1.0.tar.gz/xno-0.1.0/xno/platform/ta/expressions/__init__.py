from dataclasses import dataclass

from xno import settings
import requests


@dataclass
class SubmitExpressionStatus:
    task_id: str
    strategy_id: str
    status: str


def submit_ta_expression(
    expression: str,
    symbol: str,
    resolution: str,
    from_time: str,
    to_time: str,
    initial_cash: float = 500_000_000.0,
    fee: float = 0.0015,
    strategy_name: str = "",
    recall_name: str = "",
    description: str = "",

):
    """
    Submit a technical analysis expression for backtesting.
    Args:
        expression (str): The technical analysis expression to evaluate.
        symbol (str): The stock symbol to analyze.
        resolution (str): The resolution of the data (e.g., 'D' for daily).
        from_time (str): Start date for the backtest in 'YYYY-MM-DD' format.
        to_time (str): End date for the backtest in 'YYYY-MM-DD' format.
        initial_cash (float): Initial cash amount for the backtest. Default is 500,000,000.
        fee (float): Trading fee percentage. Default is 0.0015.
        strategy_name (str): Name of the trading strategy.
        recall_name (str): Name of the recall function, if any.
        description (str): Description of the strategy or expression.
    Returns:
        dict: A task ID and strategy ID along with the status of the submission.
    """
    response = requests.post(
        settings.api_base_url + "/ta-submit/v1/expressions",
        json={
            "expression": expression,
            "symbol": symbol,
            "resolution": resolution,
            "from_time": from_time,
            "to_time": to_time,
            "initial_cash": initial_cash,
            "trading_fee": fee,
            "strategy_name": strategy_name,
            "recall_name": recall_name,
            "description": description,
        },
        headers={'Authorization': f"Bearer {settings.api_key}"}
    )
    if response.status_code != 200:
        return None
    data = response.json()['data']
    return SubmitExpressionStatus(
        task_id=data['task_id'],
        strategy_id=data['strategy_id'],
        status=data['state']
    )