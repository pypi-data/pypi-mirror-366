# cut.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Maximilian Meindl, University of Vienna
"""

import numpy as np
import xarray as xr
import netCDF4
import os


def masking(target_grid, source_grid, output_path_mask):
    """
    Masking the data to match the spatial extent of target data.

        Input:
            target_grid              str        path to target grid
            source_grid              str        path to source grid
            output_path_mask         str        base path where the output file is stored

        Output:
            Returns mask netcdf-file based on nan-values of the target grid.
    """
    # Extract the filename from the source_grid
    filename = source_grid.split('/')[-1]

    # Check if the filename contains one of the specified substrings
    remap_options = ["_remapnn.nc", "_remapbil.nc", "_remapcon.nc", "_remapdis.nc"]

    # Modify the filename to include '_mask' before the .nc extension
    for remap_option in remap_options:
        if filename.endswith(remap_option):
            file = filename.replace(".nc", "_mask.nc")

    output_file = f"{output_path_mask}/{file}"

    # check whether the file already exits and return the path of the file
    if os.path.exists(output_file):
        return output_file
    else:
        # read in target and source grid
        target_grid = xr.open_dataset(target_grid)
        source_grid = xr.open_dataset(source_grid)

        if 'tas' in source_grid:
            variable = 'tas'

        if 'pr' in source_grid:
            variable = 'pr'

        nan_locations = target_grid[variable][0].isnull()
        source_mask = source_grid[variable].where(~nan_locations, np.nan)

        # save xarray Dataset to netcdf-file
        source_mask.to_netcdf(output_file)
        return output_file