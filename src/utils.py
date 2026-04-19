import time
import functools
import logging

logger = logging.getLogger(__name__)

def time_it(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"Method {func.__name__} took { (end - start) * 1000:.2f} ms")
        return result
    return wrapper
