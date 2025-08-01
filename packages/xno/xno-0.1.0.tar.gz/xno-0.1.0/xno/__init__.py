import os
import logging
from typing import TYPE_CHECKING

os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
_log_level = os.environ.get('LOG_LEVEL', 'info').upper()

if TYPE_CHECKING:
    from xno.algo import features  # Only imported for type hinting/doc build
    from xno import timeseries
    from xno.data.handlers.ohlc import OHLCHandler
    from xno.config import settings
else:
    from xno.algo.features import *
    from xno.timeseries import *
    from xno.config import settings
    from xno.data.handlers.ohlc import OHLCHandler
    import pandas as pd
    pd.option_context("display.multi_sparse", False)

__all__ = [
    "OHLCHandler",
    "settings",
]

logging.basicConfig(
    level=_log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
