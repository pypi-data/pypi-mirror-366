# __init__.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Maximilian Meindl, University of Vienna
"""

import xarray as xr
from .oeks15_download import load_oeks15
from .spartacus_download import load_spartacus
from .cordex_download import load_cordex
from .eobs_download import load_eobs
from .destine_download import load_destine
from .era5_download import load_era5
from .regrid import remapbil
from .regrid import remapnn
from .regrid import remapcon
from .regrid import remapdis
from .mask import masking


def load(type, model_global, model_regional, variable, experiment, ens, start, end, output_path):
    """
    Function that calls the corresponding load functions, depending on the chosen type.
    Both the path of the file and the xarray object are returned.
    """
    if type == 'oeks15':
        # Call the load_oeks15 function to get the file path
        file_path_oeks15 = load_oeks15(model_global, model_regional, variable, experiment, ens, output_path)

        # Use xarray to load the dataset from the downloaded netCDF file
        dataset_oeks15 = xr.open_dataset(file_path_oeks15)
        return file_path_oeks15, dataset_oeks15

    if type == 'spartacus':
        # Call the load_spartacus function to get the file path
        file_path_spartacus = load_spartacus(variable, start, end, output_path)

        # Use xarray to load the dataset from the downloaded netCDF file
        dataset_spartacus = xr.open_dataset(file_path_spartacus)
        return file_path_spartacus, dataset_spartacus

    if type == 'eurocordex':
        # Call the load_cordex function to get the file path
        file_path_cordex = load_cordex(model_global, model_regional, variable, experiment, ens, start, end, output_path)

        # Use xarray to load the dataset from the downloaded netCDF file
        dataset_cordex = xr.open_dataset(file_path_cordex)
        return file_path_cordex, dataset_cordex

    if type == 'eobs':
        # Call the load_eobs function to get the file path
        file_path_eobs = load_eobs(variable, start, end, output_path)

        # Use xarray to load the dataset from the downloadeed netCDF file
        dataset_eobs = xr.open_dataset(file_path_eobs)
        return file_path_eobs, dataset_eobs

    if type == 'destine':
        # Call the download function to get the file path
        file_path_destine = load_destine(model_global, variable, experiment, start, end, output_path)

        # Use xarray to load the dataset from the downloaded netCDF file
        dataset_destine = xr.open_dataset(file_path_destine)
        return file_path_destine, dataset_destine

    if type == 'era5':
        # Call the download function to get the file path
        file_path_era5 = load_era5(model_global, variable, start, end, output_path)

        # Use xarray to load the dataset from the downloaded netCDF file
        dataset_era5 = xr.open_dataset(file_path_era5)
        return file_path_era5, dataset_era5

    else:
        raise ValueError(f"Unsupported type: {type}")


def regrid(type, target_file, input_file, output_path_regrid):
    """
    Function that calls the corresponding regridding function.
    Both the path of the file and the xarray object are returned.
    """

    if type == 'nneighbor':
        # nearest neighbor interpolation
        regrid_path = remapnn(target_file, input_file, output_path_regrid)

        dataset_regrid = xr.open_dataset(regrid_path)
        return regrid_path, dataset_regrid

    if type == 'bilinear':
        # bilinear interpolation
        regrid_path = remapbil(target_file, input_file, output_path_regrid)

        dataset_regrid = xr.open_dataset(regrid_path)
        return regrid_path, dataset_regrid

    if type == 'conservative':
        # conservative interpolation
        regrid_path = remapcon(target_file, input_file, output_path_regrid)

        dataset_regrid = xr.open_dataset(regrid_path)
        return regrid_path, dataset_regrid

    if type == 'distance':
        # distance weighted interpolation
        regrid_path = remapdis(target_file, input_file, output_path_regrid)

        dataset_regrid = xr.open_dataset(regrid_path)
        return regrid_path, dataset_regrid


def mask(target_grid, input_grid, output_path_mask):
    """
    Function that calls the masking function.
    Both the path of the file and the xarray object are returned.
    """
    mask_path = masking(target_grid, input_grid, output_path_mask)

    dataset_mask = xr.open_dataset(mask_path)
    return mask_path, dataset_mask