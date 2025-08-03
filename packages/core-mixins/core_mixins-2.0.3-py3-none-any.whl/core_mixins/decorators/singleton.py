# -*- coding: utf-8 -*-

from functools import wraps
from typing import Callable, Type


def singleton(cls: Type) -> Callable:
    """
    Make a class a Singleton class (only one instance)

    :param cls: The class being decorated.
    :type cls: ``Type``
    :return: The wrapped function.
    :rtype: Callable
    """

    @wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if not wrapper_singleton.instance:
            wrapper_singleton.instance = cls(*args, **kwargs)

        return wrapper_singleton.instance

    wrapper_singleton.instance = None
    return wrapper_singleton
