from dataclasses import dataclass
from typing import List

from xno import settings
import requests


@dataclass
class FunctionDoc:
    doc: str
    sig: str


def get_function_docs() -> List[FunctionDoc]:
    """
    Fetch the documentation for all available functions in the technical analysis API.
    :return:
    """
    response = requests.get(
        settings.api_base_url + "/ta-submit/v1/functions/docs",
        headers={'Authorization': f"Bearer {settings.api_key}"}
    )
    if response.status_code != 200:
        raise Exception(f"Failed to fetch function docs: {response.status_code} {response.text}")
    data = response.json()['data']
    return [FunctionDoc(doc=item['doc'], sig=item['sig']) for item in data]

