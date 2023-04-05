"""
Module containing function to deal with interacting with the Gaia TAP server
and download Gaia data.
"""
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
from enum import Enum

import astropy
from astroquery.gaia import Gaia
import pandas as pd

# Set configuration
logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] - %(asctime)s - %(name)s - %(message)s"
)

# Explicitly set the source to DR3 (this tool is made to work with it)
Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"  
Gaia.ROW_LIMIT = -1

class FieldGeometry(Enum):
    """Enumeration of field geometry types accepted by dowloader function"""
    CONE = "cone"
    SQUARE = "square"


@contextmanager
def gaia_credentials(credentials_file: str | Path = "gaia_credentials.txt") -> Generator:
    try:
        Gaia.login(credentials_file=credentials_file)
        yield
    finally:
        Gaia.logout()


async def get_gaia_catalog(
    center_coord: astropy.coordinates.SkyCoord,
    size: astropy.units.Quantity,
    field_geometry: FieldGeometry = FieldGeometry.CONE
    ) -> pd.DataFrame:
    """
    Get Gaia field as a pandas DataFrame given the central coordinate and the field size.
    By default it will take a cone view with a diameter as `size`, the other view geometries
    suported are enumerated on FieldGeometry.

    OBS: The function is async to allow for multiple simultaneous downloads.
    Remember to "await" the result for a single request. For example:

        > data = await get_gaia_catalog(center, size)

    
    Parameters
    ----------
    
    center_coord: astropy.coordinates.SkyCoord
        Central coordinate of the desired field as a SkyCoord object.
    
    size: astropy.units.Quantity
        Size of the field around the center coordinate as a angular Quantity object.
    
    field_geometry: FieldGeometry = FieldGeometry.CONE
        Type of field geometry to recover on the FieldGeometry enumeration.
        
    Returns
    -------
        data: pd.DataFrame
            DataFrame with the recovered field
    
    """

    logging.info(
            f"Downloading data - Field size = {size} - RA = {center_coord.ra} - DEC = {center_coord.dec}"
    )

    if field_geometry == FieldGeometry.SQUARE:
        r = Gaia.query_object_async(coordinate=center_coord, width=size, height=size)

    elif field_geometry == FieldGeometry.CONE:
        r = Gaia.cone_search_async(center_coord, radius=size/2).get_results()

    data = r.to_pandas()
    
    return data
