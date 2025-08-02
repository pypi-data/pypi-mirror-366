# -*- coding: utf-8 -*-

from functools import wraps
from typing import Callable


def cache(fcn: Callable) -> Callable:
    """
    It maintains a cache of previous function call results that can be
    used to optimize the performance...

    :param fcn: The function being decorated.
    :type fcn: Callable
    :return: The wrapped function.
    :rtype: Callable
    """

    @wraps(fcn)
    def wrapper_cache(*args, **kwargs):
        cache_key = args + tuple(kwargs.items())
        if cache_key not in wrapper_cache.cache:
            wrapper_cache.cache[cache_key] = fcn(*args, **kwargs)

        return wrapper_cache.cache[cache_key]

    wrapper_cache.cache = dict()
    return wrapper_cache
