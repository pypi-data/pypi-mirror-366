import talib
import functools

def _call_func(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        talib_func = getattr(talib, func.__name__)
        return talib_func(*args, **kwargs)
    return wrapper
