# xno/data/datasources/internal/__init__.py
import json
import logging
from abc import ABC
from typing import Iterable, Union, List
from tqdm import tqdm
import pandas as pd
import redis
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.pool import QueuePool

from xno.config import RedisConfiguration, DatabaseConfiguration
from xno.data.datasources import BaseDataSource


class InternalDataSource(BaseDataSource, ABC):
    """
    Shared infrastructure for all internal datasources: lazy, process‑wide
    Engine / Session registry + Redis connection.
    """
    _redis_client: Union[redis.StrictRedis, None] = None
    _SessionFactory: Union[scoped_session, None] = None

    def __init__(self):
        """
        Initialize the internal datasource.
        This class should not be instantiated directly.
        """
        super().__init__()
        self._realtime_topic_template = None
        self._yield_records = 5_000

    @classmethod
    def _create_session_factory(cls) -> scoped_session:
        pg = DatabaseConfiguration()
        url = (
            f"postgresql+psycopg2://{pg.db_user}:{pg.db_password}"
            f"@{pg.db_host}:{pg.db_port}/{pg.db_name}"
        )

        engine = create_engine(
            url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1_800,
            pool_pre_ping=True,
            echo=False,
        )
        factory = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
        return factory

    @classmethod
    def db(cls) -> Session:
        """
        Thread‑safe accessor that returns *a session instance*.
        Usage:
            with InternalDataSource.db() as session:
                ...
        """
        if cls._SessionFactory is None:
            cls._SessionFactory = cls._create_session_factory()
        return cls._SessionFactory()

    @classmethod
    def redis(cls) -> redis.StrictRedis:
        if cls._redis_client is None:
            cfg = RedisConfiguration()
            logging.info("Connecting to Redis @ %s:%s/%s",
                         cfg.redis_host, cfg.redis_port, cfg.redis_db)
            cls._redis_client = redis.StrictRedis(
                host=cfg.redis_host,
                port=cfg.redis_port,
                db=cfg.redis_db,
                password=cfg.redis_password,
                decode_responses=True,   # optional: str instead of bytes
            )
        return cls._redis_client

    @classmethod
    def _query_db(
        cls,
        query_template: str,
        chunk_size: int,
        params: dict
    ) -> Iterable[pd.DataFrame]:
        """
        Yield DataFrames in *chunk_size* batches.
        """
        sql = text(query_template)

        with cls.db() as session:
            for chunk_df in tqdm(pd.read_sql_query(sql, session.bind, params=params, chunksize=chunk_size,)):
                logging.info("Yielding chunk of size %d", len(chunk_df))
                yield chunk_df

    def _stream(self, symbols):
        """
        Stream data from Redis Pub/Sub for the specified symbols.
        :param symbols: List of symbols to subscribe to.
        """
        # normalise input
        if isinstance(symbols, str):
            symbols = [symbols]

        channels = [
            self._realtime_topic_template.format(symbol=sym) for sym in symbols
        ]

        pubsub = self.redis().pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(*channels)
        total_messages = 0
        try:
            for msg in pubsub.listen():
                if msg["type"] != "message":
                    continue

                try:
                    payload = self.data_transform_func(json.loads(msg["data"]))
                    if payload is not None:
                        self.data_buffer.append(payload)

                    total_messages += 1
                    if total_messages % self.commit_batch_size == 0:
                        # commit buffered messages to the data source
                        logging.debug(f"Committing {len(self.data_buffer)} buffered messages. Total consume messages {total_messages}")
                        self.commit_buffer()
                except json.JSONDecodeError as exc:
                    logging.warning("Bad JSON on %s: %s", msg["channel"], exc)
                    continue
        finally:
            # clean shutdown
            pubsub.close()
