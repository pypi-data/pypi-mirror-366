# -*- coding: utf-8 -*-

from functools import update_wrapper, wraps
from typing import Callable


class CountCalls:
    """ It provides the mechanism to count invocations -- class decorator """

    def __init__(self, fcn: Callable):
        update_wrapper(self, fcn)
        self.calls_number = 0
        self.fcn = fcn

    def __call__(self, *args, **kwargs):
        self.calls_number += 1
        return self.fcn(*args, **kwargs)


def count_calls(fcn: Callable) -> Callable:
    """
    It provides the mechanism to count invocations...

    :param fcn: The function being decorated.
    :type fcn: Callable
    :return: The wrapped function.
    :rtype: Callable
    """

    @wraps(fcn)
    def wrapper_count_calls(*args, **kwargs):
        wrapper_count_calls.calls_number += 1
        return fcn(*args, **kwargs)

    wrapper_count_calls.calls_number = 0
    return wrapper_count_calls
