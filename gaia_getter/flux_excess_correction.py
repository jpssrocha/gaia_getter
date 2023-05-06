"""
Corrections for BP-RP flux excess factor [Riello et al. (2020)] w/ wrapper to
easily apply to DataFrame on a df.pipe operation.
"""
import pandas as pd
import numpy as np

from gaia_getter.utils import logger


def correct_flux_excess_factor(bp_rp: np.ndarray, phot_bp_rp_excess_factor: np.ndarray):
    """
    Calculate the corrected flux excess factor for the input Gaia (E)DR3 data.
    

    Source: https://github.com/agabrown/gaiaedr3-flux-excess-correction
    Reference: Riello et al. (2020).
    Copyright: Anthony G.A. Brown, Leiden University


    Parameters
    ----------
    
    bp_rp: numpy.ndarray
        The (BP-RP) colour listed in the Gaia (E)DR3 archive.

    phot_bp_rp_excess_factor: numpy.ndarray
        The flux excess factor listed in the Gaia (E)DR3 archive.
        
    Returns
    -------

    np.ndarray:
    
        The corrected value for the flux excess factor, which is zero for
        "normal" stars.
    
    Example
    -------
    
    phot_bp_rp_excess_factor_corr = correct_flux_excess_factor(bp_rp, phot_bp_rp_flux_excess_factor)
    """
    
    if bp_rp.shape != phot_bp_rp_excess_factor.shape:
        raise ValueError('Function parameters must be of the same shape!')
        
    do_not_correct = np.isnan(bp_rp)
    bluerange = np.logical_not(do_not_correct) & (bp_rp < 0.5)
    greenrange = np.logical_not(do_not_correct) & (bp_rp >= 0.5) & (bp_rp < 4.0)
    redrange = np.logical_not(do_not_correct) & (bp_rp >= 4.0)
    
    correction = np.zeros_like(bp_rp)
    correction[bluerange] = 1.154360 + 0.033772*bp_rp[bluerange] + 0.032277*np.power(bp_rp[bluerange], 2)
    correction[greenrange] = 1.162004 + 0.011464*bp_rp[greenrange] + 0.049255*np.power(bp_rp[greenrange], 2) \
        - 0.005879*np.power(bp_rp[greenrange], 3)
    correction[redrange] = 1.057572 + 0.140537*bp_rp[redrange]
    
    return phot_bp_rp_excess_factor - correction


@logger
def flux_excess_correction_wrapper(df: pd.DataFrame) -> pd.DataFrame:
    """
    Wrapper function to correct the BP-RP flux given a DataFrame constructed from Gaia DR3
    """
    df.phot_bp_rp_excess_factor = correct_flux_excess_factor(df.bp_rp, df.phot_bp_rp_excess_factor)
    return df
