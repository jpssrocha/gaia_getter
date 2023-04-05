from setuptools import setup

setup(
    name="gaia_getter",
    version="0.1",
    description="simple tool to download and correct gaia data",
    url="https://github.com/jpssrocha/gaia_getter",
    author="João Pedro Rocha",
    author_email="joaopedro0498@hotmail.com",
    license="MIT",
    packages=["gaia_getter"],
    install_requires=[
      "numpy",
      "pandas",
      "astropy",
      "astroquery",
    ],
    scripts=['bin/gaia_get'],
    include_package_data=True,
    zip_safe=False,
)
