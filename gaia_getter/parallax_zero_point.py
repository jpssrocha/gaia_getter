"""
Zero point correction code (Lindegren et al. 2020).

This is a simple wrapper for the code on:

> https://gitlab.com/icc-ub/public/gaiadr3_zeropoint

Copyright: Pau Ramos, University of Barcelona
"""
import pandas as pd
from gaia_getter.zero_point import zpt

def zero_point_calculation_wrapper(df: pd.DataFrame) -> pd.DataFrame:
    """Wrapper code for zero point correction"""

    zpt.load_tables()
    df = df.query("astrometric_params_solved > 3")  # Filter entries that can't be processed
    df.zpt = df.apply(zpt.zpt_wrapper, axis=1)

    return df
