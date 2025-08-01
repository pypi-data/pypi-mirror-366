import time
import os
from pathlib import Path

# Load environment variables from .env file FIRST
def load_env_file():
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables before importing XNO modules
load_env_file()

from xno.data.handlers.ohlc import OHLCHandler
from xno import settings

settings.mode = "public"  # Changed from "internal" to "public" since no PostgreSQL setup

data_handler = OHLCHandler(['HPG', 'VIC', 'VHM'], resolution='D')
data_handler.load_data(from_time='2025-01-01', to_time='2025-06-21').stream()

while True:
    print(data_handler.get_datas())
    time.sleep(20)
