
import os
import time
from pathlib import Path

# Load environment variables from .env file FIRST, before any XNO imports
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

from xno import OHLCHandler
from xno import settings

#
# or
# settings.api_key = 'your_api_key_here'  # Replace with your actual API key


data_handler = OHLCHandler([
    'VN30F1M', 'VN30F2M'
], resolution='m')
data_handler.load_data(from_time='2025-07-01', to_time='2025-12-31').stream()
print(data_handler.get_datas())
#
while True:
    print("Current DataFrame:")
    print(data_handler.get_datas())
    print("Data for VN30F1M:")
    print(data_handler.get_data('VN30F1M'))
    time.sleep(20)
