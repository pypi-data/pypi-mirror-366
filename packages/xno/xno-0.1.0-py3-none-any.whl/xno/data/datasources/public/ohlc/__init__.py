import base64
import json
import logging
from datetime import datetime

import requests
from dateutil import parser as date_parser
from dateutil.tz import UTC
from tqdm import tqdm

from xno import settings
import pandas as pd

from xno.data.datasources.public import PublicDataSource
from xno.protoc.websocket_message_pb2 import StockOHLCVMessage

_resolution_maps = {
    "MIN": "m", "HOUR1": "h", "DAY": "D"
}

class PublicOhlcDatasource(PublicDataSource):
    def data_transform_func(self, record: bytes) -> dict | None:
        message_type = record[0:2]
        if message_type != "OH":
            logging.warning("Received non-OHLC message: %s", record)
            return None

        msg_bytes = base64.b64decode(record[2:])
        msg = StockOHLCVMessage()
        msg.ParseFromString(msg_bytes)
        if _resolution_maps.get(msg.resolution) is None:
            logging.warning("Unsupported resolution: %s", msg.resolution)
            return None

        payload = {
            "Symbol": msg.symbol,
            "Time": datetime.fromtimestamp(msg.time).strftime("%Y-%m-%d %H:%M:%S"),
            "Open": msg.open,
            "High": msg.high,
            "Low": msg.low,
            "Close": msg.close,
            "Volume": msg.volume,
        }
        return payload

    def __init__(self):
        """
        Initialize the internal OHLC datasource.
        """
        super().__init__()
        self.datas = pd.DataFrame(
            columns=["Symbol", "Time", "Open", "High", "Low", "Close", "Volume"]
        ).set_index(["Time", "Symbol"])
        self.resolution = None  # Placeholder for resolution, to be set during fetch

    def create_ws_subscribe_message(self, symbols) -> str:
        """
        Create a WebSocket topic message for the given symbols.
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        return json.dumps({
              "action": "subscribe",
              "topic": "OH",
              "values": symbols
            })

    def _stream_request(self, symbol: str, from_ts: int, to_ts: int):
        """
        Prepare the request for streaming OHLC data.
        """
        with requests.get(
                f"{settings.api_base_url}/quant-data/v1/ohlcv",
                headers={"Authorization": f"{settings.api_key}"},
                params={
                    "symbol": symbol,
                    "from": from_ts,
                    "to": to_ts,
                    "resolution": self.resolution,
                },
                stream=True,
        ) as resp:
            resp.raise_for_status()

            for line in resp.iter_lines():  # already decompressed by requests
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    logging.error(f"Failed to decode JSON: {e}")
                    continue
                for o, h, l, c, v, t in zip(obj["o"], obj["h"], obj["l"], obj["c"], obj["v"], obj["t"]):
                    yield {
                        "Symbol": symbol,
                        "Time": datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%d %H:%M:%S"),
                        "Open": o,
                        "High": h,
                        "Low": l,
                        "Close": c,
                        "Volume": v,
                    }


    def fetch(self, symbols, from_time, to_time, **kwargs):
        self.resolution = kwargs.get("resolution")
        if not self.resolution:
            raise ValueError("resolution=… is required")

        from_ts = int(date_parser.parse(from_time).timestamp())
        to_ts = int(date_parser.parse(to_time).timestamp())

        for symbol in symbols:
            datas = []
            for row in tqdm(self._stream_request(
                    symbol=symbol,
                    from_ts=from_ts,
                    to_ts=to_ts,
            ), desc=f"Fetching {symbol} OHLCV data", unit=" records"):
                datas.append(row)
            if datas:
                logging.debug("Fetched %d rows for %s", len(datas), symbol)
                self.append_df_rows(datas)
