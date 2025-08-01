# xno/data/datasources/internal/ohlc/__init__.py
import pandas as pd
from xno.data.datasources.internal import InternalDataSource


_query_template = """
SELECT 
    time as "Time", 
    symbol as "Symbol", 
    open as "Open",
    high as "High", 
    low as "Low", 
    close as "Close", 
    volume as "Volume" 
FROM trading.stock_ohlcv_history
WHERE (
    symbol = ANY(:symbols) AND resolution = :resolution
    AND time >= :from_time
    AND time < :to_time
)
"""



class InternalOhlcDatasource(InternalDataSource):
    def data_transform_func(self, record: dict) -> dict | None:
        # Do not process records that do not match the resolution
        if record.get('resolution') != self.resolution:
            return None
        return {
            "Time": record["time"].split(".")[0],
            "Symbol": record["symbol"],
            "Open": record["open"],
            "High": record["high"],
            "Low": record["low"],
            "Close": record["close"],
            "Volume": record["volume"],
        }

    def __init__(self):
        """
        Initialize the internal OHLC datasource.
        """
        super().__init__()
        self.datas = pd.DataFrame(
            columns=["Symbol", "Time", "Open", "High", "Low", "Close", "Volume"]
        ).set_index(["Time", "Symbol"])
        self.resolution = None  # Placeholder for resolution, to be set during fetch
        self._realtime_topic_template = "data.quant.{symbol}.ohlc"

    def fetch(self, symbols, from_time, to_time, **kwargs):
        """
        Fetch OHLC data for a given symbol and time range using the internal datasource.

        :param symbols: The tickers to fetch data for.
        :param from_time: Start time for the data fetch.
        :param to_time: End time for the data fetch.
        :return: DataFrame containing OHLC data.
        """

        self.resolution = kwargs.get("resolution", None)
        if self.resolution is None:
            raise ValueError("Resolution must be specified for fetching OHLC data.")

        for chunk_df in self._query_db(
            query_template=_query_template,
            chunk_size=self._yield_records,
            params={
                "symbols": symbols,
                "resolution": self.resolution,
                "from_time": from_time,
                "to_time": to_time,
            }
        ):
            self.append_df_rows(chunk_df)
