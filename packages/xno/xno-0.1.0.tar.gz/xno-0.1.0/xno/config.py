import os
from typing import Optional


class DatabaseConfiguration:
    def __init__(self):
        self.db_host: str = os.environ['POSTGRES_HOST']
        self.db_port: str = os.environ['POSTGRES_PORT']
        self.db_user: str = os.environ['POSTGRES_USER']
        self.db_password: str = os.environ['POSTGRES_PASSWORD']
        self.db_name: str = os.environ['POSTGRES_DB']

class RedisConfiguration:
    def __init__(self):
        self.redis_host: str = os.environ['REDIS_HOST']
        self.redis_port: int = int(os.environ['REDIS_PORT'])
        self.redis_password: str = os.environ['REDIS_PASSWORD']
        self.redis_db: int = int(os.environ.get('REDIS_DB', 0))


class XNOSettings:
    api_key: Optional[str] = os.environ.get('XNO_API_KEY', None)

    mode: str = "public"
    environment: str = os.environ.get('XNO_ENV', 'live')
    # Upstream REST API (public)
    api_base_url: str = "https://api-v2.xno.vn" if environment == 'live' else "https://dev-api-v2.xno.vn"
    # api_base_url: str = "http://127.0.0.1:3000"
    date_format = "%Y-%m-%d %H:%M:%S"

# Create a global settings instance
settings = XNOSettings()