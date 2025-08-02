import warnings
from functools import wraps
from typing import Optional


def deprecated(reason: Optional[str] = None, version: Optional[str] = None):
    def decorator(func):
        message = f"{func.__name__} is deprecated"
        message += (
            f" since version {version} and may be removed in the future"
            if version
            else " and may be removed in the future"
        )
        message += f" | {reason}" if reason else "."

        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(message, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator
