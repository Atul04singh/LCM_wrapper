import asyncio
import functools
import time
from typing import Callable, Any

def retry(retries: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Retry decorator with exponential backoff.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            _retries, _delay = retries, delay
            while _retries > 1:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if hasattr(args[0], 'config') and args[0].config.verbose:
                        print(f"⚠️ Attempt failed: {e}. Retrying in {_delay}s...")
                    await asyncio.sleep(_delay)
                    _retries -= 1
                    _delay *= backoff
            return await func(*args, **kwargs)
        return wrapper
    return decorator
