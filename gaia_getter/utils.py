import logging
from time import perf_counter
from typing import Callable

import pandas as pd

def logger(f: Callable) -> Callable:
    """Log info while processing a pandas df"""

    def wrapper(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:

        tic = perf_counter()
        res = f(df, *args, **kwargs)
        toc = perf_counter()

        logging.info(f"Applied: {f.__name__} | Took: {(toc-tic)/60:.2f} mins | Shape: {df.shape} ")

        return res

    return wrapper


