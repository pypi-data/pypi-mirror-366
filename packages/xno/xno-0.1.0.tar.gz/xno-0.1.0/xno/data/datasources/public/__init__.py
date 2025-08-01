import logging
from abc import ABC, abstractmethod
import websocket
from xno.config import settings
from xno.data.datasources import BaseDataSource


class PublicDataSource(BaseDataSource, ABC):
    """
    Shared infrastructure for all public datasources: lazy, process‑wide
    """

    def __init__(self):
        super().__init__()
        self.ws_url = settings.api_base_url.replace("http", "ws") + "/xdata/v1/market"
        self.commit_batch_size = 125

    @abstractmethod
    def create_ws_subscribe_message(self, symbols) -> str:
        raise NotImplementedError

    def on_message(self, ws, message):
        try:
            payload = self.data_transform_func(message)
            if payload is not None:
                self.data_buffer.append(payload)
                self.total_messages += 1
                if self.total_messages % self.commit_batch_size == 0:
                    # commit buffered messages to the data source
                    logging.debug(f"Committing {len(self.data_buffer)} buffered messages. Total consume messages {self.total_messages}")
            return None

        except Exception as ex:
            logging.error("Failed to decode message: %s", ex)
            return

    def _stream(self, symbols):
        if isinstance(symbols, str):
            symbols = [symbols]
        if not symbols:
            raise ValueError("Symbols list cannot be empty.")

        logging.debug("Starting WebSocket stream for symbols: %s", symbols)

        def on_open(ws):
            subscribe_msg = self.create_ws_subscribe_message(symbols)
            logging.debug(f"WebSocket opened [{self.ws_url}]. Sending subscription message: %s", subscribe_msg)
            ws.send(subscribe_msg)

        def on_ping(ws, message):
            logging.debug("Ping received, responding with pong...")
            ws.send("1")  # Or ws.pong(message)

        ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self.on_message,
            on_open=on_open,
            on_ping=on_ping,
        )
        ws.run_forever(ping_interval=60, ping_timeout=10)
