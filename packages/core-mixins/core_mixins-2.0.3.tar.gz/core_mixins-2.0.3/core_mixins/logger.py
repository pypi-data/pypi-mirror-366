# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
import sys
import typing


def get_logger(
        logger_name: str = None, log_level: int = logging.INFO, propagate: bool = True,
        stream_handler: typing.TextIO | None = sys.stdout, formatter: str = "[%(levelname)s] %(message)s",
        reset_handlers: bool = False) -> logging.Logger:

    """
    It returns a logger or create it if it doesn't exist. If the logger name
    is not specified, it returns the root logger....

    :param logger_name: Logger's name or None for root logger.
    :param log_level:  The logging level (CRITICAL = 50, ERROR = 40, WARNING = 30, INFO = 20)
    :param stream_handler: A handler which writes logging records, appropriately formatted to a stream.

    :param formatter:
        It specifies the layout of log records in the final output. It defines the structure
        of log messages by specifying a format string that includes placeholders for
        various attributes of a log record, such as timestamp, log level,
        logger name, and the log message itself...

    :param propagate:
        It determines whether a log message should be passed to the handlers of
        higher-level (ancestor) loggers.This can be useful in situations where you want
        to control the flow of log messages and avoid duplication in the
        log output (like Lambda Functions)...

    :param reset_handlers:
        In case we want to remove all handlers and create a new one
        with the new stream...

    :return: The logger.
    """

    logger = logging.getLogger(logger_name)
    logger.propagate = propagate
    logger.setLevel(log_level)

    if reset_handlers:
        logger.handlers = []

    handler = logging.StreamHandler(stream=stream_handler)
    handler.setFormatter(logging.Formatter(formatter))
    handler.setLevel(log_level)
    logger.addHandler(handler)

    return logger
