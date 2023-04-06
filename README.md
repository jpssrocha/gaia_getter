# Gaia Getter

Simple tool to download and correct gaia DR3 catalogs in an easy way based on a
central location and the field size. It contains a command line script for
single use catalogs and a function to help download fields programmatically
from other codebase.

# Installation

Clone this repository, activate your virtual environment (if you work with them)
and run (inside the folder you've cloned it):
    
`$ pip install gaia_getter`

Or, if you prefer to install as a symlink:

`$ pip install -e gaia_getter`

Tip: If you install as a symlink you will be able to alter the code as you wish
and the changes you make will be available to you right away.

# Basic Usage

This package was organized to work as a CLI tool or to be used as a library.

## Using CLI tool

After installing the package a command line tool, `gaia_get`, will become
available on your environment. The best way to use it is to have an account on
[ESA](https://cas.cosmos.esa.int/cas/login?service=https%3A%2F%2Ftools.cosmos.esa.int%2Fprivacy%2Findex.php),
and have a file with the credentials such as [this one](gaia_credentials.txt.example).
To use it simply type:

`$ gaia_get <RA> <DEC> <FIELD_SIZE> <OUTPUT-NAME> --credentials-file <PATH-TO-CREDENTIALS>`

Where RA and DEC are the **central coordinates** of the field **in degrees**
and the FIELD\_SIZE is the field size **in arcminutes**, by default it will be
the **diameter** of a cone view. For example, to download a field of 1 degree
around the globular cluster M3 saving to a file named M3.csv with a credentials
file named `gaia_credentials.txt`:

`$gaia_get 205.55 28.38 60 M3 --credentials-file gaia_credentials.txt`

To use without credentials simply do:

`$gaia_get 205.55 28.38 60 M3`

The output with be limited in number of rows. To get a square field with the
diameter of the cone view as the side length, do:

`$gaia_get 205.55 28.38 60 M3 --credentials-file gaia_credentials.txt -s`

The result will come as a csv file.

## Using library components

To use its library components there are 2 modules that you may want to use:

- gaia\_getter.download - Functions to deal with interacting with the Gaia server.
- gaia\_getter.process - Functions to apply to processing steps to the dowloaded data.

### gaia\_getter.download

To download gaia data there are 3 important components: 

- FieldGeometry: enum with the options for field geometries
- gaia\_credentials: a context manager to handle the login to the gaia server 
- get\_gaia\_catalog: function to download data (it's async)

To download fields first you need to represent then using astropy objects:

```python
import astropy.units as u
from astropy.coordinates import SkyCoord

# A field centered at (280, -60) and with 10 arcminutes of size
coord = SkyCoord(ra=280, dec=-60, unit=(u.degree, u.degree), frame='icrs')
size = u.Quantity(10, u.arcminute)
```

Then to use it with the library without login:

```python
from gaia_getter.download import get_gaia_catalog

dowloaded_data = await get_gaia_catalog(coord, size)
```

To use with login:

```python
from gaia_getter.download import get_gaia_catalog, gaia_credentials

with gaia_credentials(gaia_credentials_file):
    dowloaded_data = await get_gaia_catalog(coord, size)
```

To download multiple catalogs assinchronously with login:

```python
import asyncio
from gaia_getter.download import get_gaia_catalog, gaia_credentials

# Defining helper to cast input into astropy objects
def helper(ra, dec, size):
    coord = SkyCoord(ra=ra, dec=dec, unit=(u.degree, u.degree), frame='icrs')
    size = u.Quantity(size, u.arcminute)
    return coord, size

# Defining colection of fields
fields = [
    (250, -45, 10),
    (240, -40, 30),
    (200, -10, 50)

]

fields = [helper(*field) for field in fields]


with gaia_credentials(gaia_credentials_file):
    results = await asyncio.gather(*[get_gaia_catalog(*inputs) for inputs in fields])
```

Tip 1: For those who doesn't know ... using asyncio can significantly speedup the
download process (much more than 100%). Because it utilizes resources in a better way
by doing things concurrently.

Tip 2: Just be aware that the `async.gather` command will collect all returns in
memory, and this can be a problem if you download too much fields at once. For
these cases implement a sequential loop on top of it that download a chunk and
save the results to disk before going to a second run. So make sure that the
older results are cleaned from RAM before continuing each loop!

Tip 3: Depending on the environment you run this it will be necessary to wrap all
the code on an async function and run it using the asyncio.run function:

```python

async def main():
    # The code here
    
asyncio.run(main())
```

### gaia\_getter.process

Contains just one function that apply the correction on the dowloaded catalogs as
a pandas DataFrame.

```python
from gaia_getter.process import process_gaia_data
processed_catalog = process_gaia_data(dowloaded_data)
```

# Copyright notices

This code uses code 'as is' from [Pau Ramos, University of Barcelona](https://gitlab.com/icc-ub/public/gaiadr3_zeropoint/) and 
[Anthony G.A. Brown, Leiden University](https://github.com/agabrown/gaiaedr3-flux-excess-correction).

# References

- Gaia Collaboration et al. (2016b) - Gaia mission.
- Gaia Collaboration et al. (2022k) - Gaia DR3
- Lindegren et al. (2020) - Zero point estimations
- Riello et al. (2020) - BP-BR flux excess correction
- Ginsburg, Sipőcz, Brasseur et al 2019 - Astroquery
- Astropy Collaboration (2022) - Astropy
