import time
from functools import wraps

def retry(max_retries=3, delay=1, exceptions=(Exception,)):
    """
    Decorator to retry a function if it raises specified exceptions.
    :param max_retries: Number of times to retry
    :param delay: Delay between retries (in seconds)
    :param exceptions: Tuple of exception types to catch
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt == max_retries:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator


def retry_with_backoff(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(base_delay * (2 ** attempt))  # exponential backoff
        return wrapper
    return decorator


