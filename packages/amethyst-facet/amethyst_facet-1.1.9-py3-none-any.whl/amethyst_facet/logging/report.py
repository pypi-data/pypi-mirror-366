from contextlib import contextmanager
import logging
from typing import *

@contextmanager
def report(start: str = None, end: str = None, level: Any = logging.DEBUG, exception: Exception = None):
    if start is not None:
        logging.log(level=level, msg=start)
    try:
        yield
    except Exception as e:
        if exception:
            raise exception from e
        else:
            raise e
    if end is not None:
        logging.log(level=level, msg=end)
