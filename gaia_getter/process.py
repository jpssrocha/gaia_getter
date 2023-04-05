import pandas as pd

from gaia_getter.parallax_zero_point import zero_point_calculation_wrapper
from gaia_getter.flux_excess_correction import flux_excess_correction_wrapper

def process_gaia_data(gaia_catalog: pd.DataFrame) -> pd.DataFrame:
    """Wrapper to apply procedures to Gaia data"""
    return (
        gaia_catalog
        .pipe(zero_point_calculation_wrapper)
        .pipe(flux_excess_correction_wrapper)
    )
