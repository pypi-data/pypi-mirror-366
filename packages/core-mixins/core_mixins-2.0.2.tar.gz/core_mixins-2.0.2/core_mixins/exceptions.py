# -*- coding: utf-8 -*-

import sys
import traceback

from typing import Tuple, Dict, List


def get_exception_data() -> Tuple[str, str, List[Dict]]:
    """
    To retrieve the error information and the stack trace...

    Example:
        try:
            8/0

        except ZeroDivisionError as error:
            type_, message, trace = get_exception_data()

        Exception type: ZeroDivisionError
        Exception message: division by zero
        Stack trace: ...

    :return:
        The error information in a tuple like:
        (exception_type, exception_message, stack_trace)
    :rtype: Tuple[str, str, List[Dict]]
    """

    ex_type, ex_value, ex_traceback = sys.exc_info()

    stack_trace = [
        {
            "File": trace.filename,
            "Line Number": trace.lineno,
            "Line": trace.line,
            "Function": trace.name
        } for trace in traceback.extract_tb(ex_traceback)
    ]

    return ex_type.__name__, str(ex_value), stack_trace
