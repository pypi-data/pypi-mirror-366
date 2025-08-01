import os

from xno import settings
from xno.platform.ta.docs import get_function_docs
import xno

xno.AD
if __name__ == "__main__":
    docs = get_function_docs()
    for doc in docs:
        print(f"- {doc.sig}")
