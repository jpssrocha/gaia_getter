# Gaia Getter

Simple tool to download and apply 3 corrections to gaia DR3 catalogs in an easy
way, based on a central location and the field size. It contains a command line
script for single catalogs, but the package is also organized to work as a
library so that one can use the components from this package to download many
fields programatically from other codebases.

The corrections applied are:

- Parallax zero point correction (Lindegren+2020)
- BP-RP flux excess correction (Riello+2020)
- Radial velocity correction (Katz+2022 and Bloome+2022)

Each correction will appear as a new columns named: corrected\_<column>.

# Installation

Clone this repository:

`$ git clone https://github.com/jpssrocha/gaia_getter`

Activate your virtual environment (if you work with them) and run (inside the
folder you've cloned it):
    
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

**This CLI tool was made to work with small datasets** (~2° wide for a dense
field). It won't scale well with large FoV's, because to apply the corrections
it loads all the dataset in memory, therefore if it's too large it will not be
able to allocate all the necessary memory.

To use it simply type:

`$ gaia_get <RA> <DEC> <FIELD_SIZE> <OUTPUT-NAME> --credentials-file <PATH-TO-CREDENTIALS>`

Where RA and DEC are the **central coordinates** of the field **in degrees**
and the FIELD\_SIZE is the field size **in arcminutes**, by default it will be
the **diameter** of a cone view. For example, to download a field of 1 degree
around the globular cluster M3 saving to a file named M3.csv with a credentials
file named `gaia_credentials.txt`:

`$ gaia_get 205.55 28.38 60 M3 --credentials-file gaia_credentials.txt`

To use without credentials simply do:

`$ gaia_get 205.55 28.38 60 M3`

The output with be limited in number of rows. To get a square field with the
diameter of the cone view as the side length, do:

`$ gaia_get 205.55 28.38 60 M3 --credentials-file gaia_credentials.txt -s`

The result will come as a csv file.

## Using library components

To use its library components there are 2 modules that you may want to use:

- gaia\_getter.download - Functions to deal with interacting with the Gaia server.
- gaia\_getter.process - Functions to apply to processing steps to the dowloaded data.

### gaia\_getter.download

To download gaia data there are 3 important components: 

- FieldGeometry: enum with the options for field geometries
- gaia\_credentials: a context manager to handle the login to the gaia server 
- get\_gaia\_catalog: function to download data

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

dowloaded_data = get_gaia_catalog(coord, size)
```

To use with login:

```python
from gaia_getter.download import get_gaia_catalog, gaia_credentials

gaia_credentials_file = "gaia_credentials.txt"

with gaia_credentials(gaia_credentials_file):
    dowloaded_data = get_gaia_catalog(coord, size).get_data()
```

### gaia\_getter.process

Contains just one function that apply the corrections on the dowloaded catalogs
as a pandas DataFrame.

```python
from gaia_getter.process import process_gaia_data
processed_catalog = process_gaia_data(dowloaded_data)
```

# Copyright notices

This code uses code 'as is' from [Pau Ramos, University of Barcelona](https://gitlab.com/icc-ub/public/gaiadr3_zeropoint/) and 
[Anthony G.A. Brown, Leiden University](https://github.com/agabrown/gaiaedr3-flux-excess-correction).

# On concurrent downloads

The library components of this package were created thinking on letting the
downloads be asynchronous, but the astroquery async functions won't do things
asynchronously depending on the version. So the functions were re adapted to
run sequentially.

Therefore to download multiple fields concurrently one can create a custom
function using the helpers here and run then concurrently using a ThreadPool
(present on python by default). Here is a full example on how to use it to 
download cone fields without applying corrections:

```python
from multiprocessing.pool import ThreadPool
from gaia_getter.download import get_gaia_catalog, gaia_credentials
import astropy.units as u
from astropy.coordinates import SkyCoord

def helper(ra, dec, size):
    """Prepare fields for download"""
    coord = SkyCoord(ra=ra, dec=dec, unit=(u.degree, u.degree), frame='icrs')
    size = u.Quantity(size, u.arcminute)
    return coord, size


# Defining a colection of 10 fields
fields = [(250, -46 + i, 2) for i in range(10)] 

fields = [helper(*field) for field in fields]

gaia_credentials_file = "gaia_credentials.txt"

with gaia_credentials(gaia_credentials_file):

    with ThreadPool(processes=10) as p:
        res = p.starmap_async(get_gaia_catalog, fields)

        res = [r for r in res.get()]

```

This script downloaded fields on my computer (and internet) about 20-30x faster
than sequentially.

Tip: Just be aware that the last command will collect all returns
in memory, and this can be a problem if you download too much fields at once.
For these cases, implement a sequential loop on top of it, that download a
chunk and save the results to disk before going to a second run. In short: make
sure that the older results are cleaned from RAM before continuing!

# Acknowledgments

Thanks Francisco Maia (UFRJ) and Raphael Oliveira (IAG) for sharing the initial
directions about the canonical corrections, and Mateus Angelo (CEFET) for
sharing the recipe for radial velocity corrections.

# References

- Gaia Collaboration et al. (2016b) - Gaia mission.
- Gaia Collaboration et al. (2022k) - Gaia DR3
- Lindegren et al. (2020) - Zero point estimations
- Riello et al. (2020) - BP-BR flux excess correction
- Katz et al. (2022) - Radial velocity correction for colder stars
- Blomme et al. (2022) - RV correction for hot stars 
- Ginsburg, Sipőcz, Brasseur et al 2019 - Astroquery
- Astropy Collaboration (2022) - Astropy
