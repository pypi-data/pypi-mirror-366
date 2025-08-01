from setuptools import setup, find_packages

VERSION = '1.0.0' 
DESCRIPTION = 'Climxtract'
LONG_DESCRIPTION = 'ClimXtract: A Python Toolkit for Standardizing High-Resolution Climate Datasets for Austria'

setup(
        name="climxtract",
        version=VERSION,
        author="Maximilian Meindl",
        author_email="<maximilian.meinndl@univie.ac.at>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        url = "https://github.com/meindlm97/ClimXtract",
        install_requires=['numpy', 'xarray', 'wget', 'cdsapi', 'cdo', 'polytope-client', 'lxml', 'conflator', 'rasterio', 'cf-units', 'esgf-pyclient', 'netcdf4', 'cfgrib', 'eccodes'],
        include_package_data=True,
        keywords=['python', 'climate', 'interpolation', 'geospatial data', 'modeling'],
        classifiers= [
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ],
        packages=find_packages(exclude=["example_notebooks"]),
        python_requires=">=3.10",
)
