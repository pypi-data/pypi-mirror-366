import functools
from .core import Pocketwatch


def stopwatch(*args, **kwargs):
    """Lightweight decorator for timing functions."""
    if args and callable(args[0]) and not kwargs:
        fn = args[0]

        @functools.wraps(fn)
        def wrapper(*a, **kw):
            with Pocketwatch(fn.__name__):
                return fn(*a, **kw)

        return wrapper

    def decorator(fn):
        msg = kwargs.pop("msg", fn.__name__)

        @functools.wraps(fn)
        def wrapper(*a, **kw):
            with Pocketwatch(msg, **kwargs):
                return fn(*a, **kw)

        return wrapper

    return decorator
