
from xno import settings
from xno.data.datasources.internal.ohlc import InternalOhlcDatasource
from xno.data.datasources.public.ohlc import PublicOhlcDatasource
from xno.data.handlers import DataHandler


class OHLCHandler(DataHandler):
    def __init__(self, symbols, resolution):
        super().__init__(symbols)
        self.resolution = resolution
        self.source = PublicOhlcDatasource() if settings.mode == "public" else InternalOhlcDatasource()

    def load_data(self, from_time, to_time):
        self.source.fetch(symbols=self.symbols, from_time=from_time, to_time=to_time, resolution=self.resolution)
        return self

    def stream(self):
        return self.source.stream(
            self.symbols,
            commit_batch_size=10,
            daemon=True,
            resolution=self.resolution,
            thread_id="ohlc_handler_stream"
        )