"""
This module implements the corrections on RV for cold (Katz+2022) and hot stars
(Blomme+2022).
"""
import pandas as pd
import numpy as np
from gaia_getter.utils import logger

def valid_sources(data: pd.DataFrame) -> pd.Series:
    """
    Given a dataframe of gaia (e)DR3 returns a boolean mask with highlighting
    only sources with all the necessary information to apply the RV corrections.
    """

    # Sources missing the necessary information for applying the corrections
    no_info = (data.rv_template_teff.isna() | data.grvs_mag.isna())

    # Sources not valid for Blomme+2022 correction
    outside_range = ( 
        ((data.grvs_mag > 12) | (data.grvs_mag < 6)) 
        & (data.rv_template_teff >= 8500) 
    )

    return (~outside_range) & (~no_info)


def RV_corr_line(line: pd.Series) -> float:
    """Apply the corrections from Blomme+2022 and Katz+2022 for a line"""
    
    grvs = line.grvs_mag
    rv = line.radial_velocity

    # Correct for hot stars (Blomme+2022)
    if line.rv_template_teff >= 8500:
        return rv - 7.98 + 1.135*grvs
    
    # Correction for cold stars (Katz+2022)
    if grvs < 11:
        return rv
    
    return rv - (
          0.02755*grvs**2
        - 0.55863*grvs
        + 2.81129
    )


@logger
def rv_correction_wrapper(data: pd.DataFrame) -> pd.DataFrame:
    """
    Apply rv corrections from Blomme+2022 and Katz+2022.
    """

    # Initialize rv correcte column
    data["corrected_radial_velocity"] = np.nan

    # Get mask for valid lines
    valid_sources_mask = valid_sources(data)

    data.loc[valid_sources_mask, "corrected_radial_velocity"] = data.loc[valid_sources_mask, :].apply(RV_corr_line, axis=1)
     
    return data
