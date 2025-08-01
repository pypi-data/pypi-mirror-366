from typing import List

from xno import settings
import requests


def get_available_stocks() -> List[str]:
    """
    Fetch the documentation for all available functions in the technical analysis API.
    :return:
    """
    response = requests.get(
        settings.api_base_url + "/ta-submit/v1/stocks",
        headers={'Authorization': f"Bearer {settings.api_key}"}
    )
    if response.status_code != 200:
        raise Exception(f"Failed to fetch available stocks: {response.status_code} {response.text}")
    data = response.json()['data']
    return data
