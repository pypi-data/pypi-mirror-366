# -*- coding: utf-8 -*-

from functools import wraps
from typing import Callable


def repeat(fcn: Callable = None, *, times: int = 2) -> Callable:
    """
    Repeat n times the function and return the list of returned values...

    :param fcn: The function being decorated.
    :type fcn: Callable
    :param times: Number of times the function will be invoked.
    :type times: int

    :return: The wrapped function.
    :rtype: Callable
    """

    def decorator_repeat(func):
        @wraps(func)
        def wrapper_repeat(*args, **kwargs):
            values = []
            for _ in range(times):
                values.append(func(*args, **kwargs))

            return values

        return wrapper_repeat

    if not fcn:
        return decorator_repeat

    return decorator_repeat(fcn)
