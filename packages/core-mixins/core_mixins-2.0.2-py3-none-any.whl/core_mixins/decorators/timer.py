# -*- coding: utf-8 -*-

from functools import wraps
from time import perf_counter
from typing import Any
from typing import Callable
from typing import Tuple


def timer(fcn: Callable = None) -> Callable:
    """
    Using this decorator you will get a tuple in the form
    of: result, execution_time...

    :param fcn: The function being decorated.
    :type fcn: Callable
    :return: The wrapped function.
    :rtype: Callable
    """

    def decorator_timer(func):
        @wraps(func)
        def wrapper_timer(*args, **kwargs) -> Tuple[Any, float]:
            start_time, res = perf_counter(), func(*args, **kwargs)
            return res, (perf_counter() - start_time)

        return wrapper_timer

    return decorator_timer(fcn)
