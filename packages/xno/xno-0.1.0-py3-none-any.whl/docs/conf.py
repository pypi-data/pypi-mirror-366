# docs/conf.py

import os
import sys
sys.path.insert(0, os.path.abspath('../'))          # your top-level project dir
sys.path.insert(0, os.path.abspath('../xno'))       # add the actual package path

project = "xno-vn-docs"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # for Google or NumPy style docstrings
    'sphinx.ext.viewcode',  # optional, for source code links
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
]
autodoc_mock_imports = [
    "pandas",
    "talib",
    "numpy",
    "scipy",
    "sklearn",
    "numba"
]
