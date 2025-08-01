# xno/data/handlers/__init__.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Union, Any, Type, Optional
import pandas as pd

from xno.data.datasources import BaseDataSource


class DataHandler(ABC):
    def __init__(self, symbols: Union[str, List[str]]):
        """
        Initialize the data handler with a list of symbols.
        If a single symbol is provided as a string, it is converted to a list.
        :param symbols:
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        self.symbols = symbols
        self.source: Optional[Union[BaseDataSource, Type[BaseDataSource]]] = None

    def get_datas(self) -> pd.DataFrame:
        """
        Get the current DataFrame.
        :return: DataFrame containing the data.
        """
        self.source.commit_buffer()
        return self.source.datas.sort_index()

    def get_data(self, symbol: Union[str, List[str]]) -> pd.DataFrame:
        """
        Get data for a specific symbol or list of symbols.

        :param symbol: A single symbol or a list of symbols to retrieve data for.
        :return: MultiIndex DataFrame with index ["Symbol", "Time"].
        """
        if isinstance(symbol, str):
            symbol = [symbol]

        self.get_datas()
        df = self.source.datas

        # Select data using MultiIndex filtering
        df_filtered = df.loc[df.index.get_level_values("Symbol").isin(symbol)]

        # Ensure MultiIndex is kept
        df_filtered = df_filtered.sort_index()

        return df_filtered

    @abstractmethod
    def load_data(
        self,
        from_time: Union[str, datetime],
        to_time: Union[str, datetime]
    ) -> pd.DataFrame:
        """
        Load data for the specified time range.
        :param from_time:
        :param to_time:
        :return:
        """

    @abstractmethod
    def stream(self) -> Any:
        return self.source.stream(
            symbols=self.symbols,
            commit_batch_size=125,
            daemon=True,
            thread_id="data_handler_stream",
        )
