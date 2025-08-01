# regrid.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Maximilian Meindl, University of Vienna
"""

import os
from cdo import Cdo
from importlib.resources import files


def remapnn(target_file, source_file, output_path_regrid):
    """
    Remapping any grid to lambert_conformal_conic projection using nearest-neighbour interpolation.
    Target file can be either a netcdf-file or a grid description file (.txt).

        Input:
            target_file            str   path to the target file
            source_file            str   path to the source file
            output_path_regrid     str   base path where the output file is stored

        Output:
            Returns the remapped netcdf-file as well as the output path for the cutting function.
    """
    # If cdo is not in the path, add it manually
    conda_bin = os.path.expanduser('~/.conda/envs/climxtract/bin')
    os.environ['PATH'] += f':{conda_bin}'

    # Extract the filename from the source file
    filename = source_file.split('/')[-1]

    # Modify the filename to include '_remapnn' before the .nc extension
    file = filename.replace(".nc", "_remapnn.nc")
    output_file = f"{output_path_regrid}/{file}"

    # Check whether the file already exits and return the path of the file
    if os.path.exists(output_file):
        return output_file

    else:
        # Initialize the Cdo object
        cdo = Cdo()

        # Perform the regridding using the remapnn method
        cdo.remapnn(target_file, input=source_file, output=output_file)
        return output_file


def remapbil(target_file, source_file, output_path_regrid):
    """
    Remapping any grid to lambert_conformal_conic projection using bilinear interpolation.
    Target file can be either a netcdf-file or a grid description file (.txt).

        Input:
            target_file              str     path to the target file
            source_file              str     path to the source file
            output_path_regrid       str     base path where the output file is saved

        Output:
            Returns the remapped netcdf-file as well as the output path for the cutting function.
    """
    # If cdo is not in the path, add it manually
    conda_bin = os.path.expanduser('~/.conda/envs/climxtract/bin')
    os.environ['PATH'] += f':{conda_bin}'

    # Extract the filename from the source file
    filename = source_file.split('/')[-1]

    # Modify the filename to include '_remapbil' before the .nc extension
    file = filename.replace(".nc", "_remapbil.nc")
    output_file = f"{output_path_regrid}/{file}"

    # Check whether the file already exits and return the path of the file
    if os.path.exists(output_file):
        return output_file

    else:
        # Initialize the Cdo object
        cdo = Cdo()

        # Perform the regridding using the remapbil method
        cdo.remapbil(target_file, input=source_file, output=output_file)
        return output_file


def remapcon(target_file, source_file, output_path_regrid):
    """
    Remapping any grid to lambert_conformal_conic projection using conservative interpolation.
    Target file can be either a netcdf-file or a grid description file (.txt).

        Input:
            target_file              str     path to the target file
            source_file              str     path to the source file
            output_path_regrid       str     base path where the output file is saved

        Output:
            Returns the remapped netcdf-file as well as the output path for the cutting function.
    """
    # If cdo is not in the path, add it manually
    conda_bin = os.path.expanduser('~/.conda/envs/climxtract/bin')
    os.environ['PATH'] += f':{conda_bin}'

    # Extract the filename from the source file
    filename = source_file.split('/')[-1]

    # Modify the filename to include '_remapcon' before the .nc extension
    file = filename.replace(".nc", "_remapcon.nc")
    output_file = f"{output_path_regrid}/{file}"

    # Check whether the file already exits and return the path of the file
    if os.path.exists(output_file):
        return output_file

    else:
        # Initialize the Cdo object
        cdo = Cdo()

        # Dynamically get the file path to oeks15_grid.txt inside the package
        oeks15_grid_path = files('climxtract').joinpath('oeks15_grid.txt')

        # Perform the regridding using the remapcon method
        cdo.remapcon(str(oeks15_grid_path), input=source_file, output=output_file, options="--force")
        return output_file


def remapdis(target_file, source_file, output_path_regrid):
    """
    Remapping any grid to lambert_conformal_conic projection using distance weighted interpolation.
    Target file can be either a netcdf-file or a grid description file (.txt).

        Input:
            target_file              str     path to the target file
            source_file              str     path to the source file
            output_path_regrid       str     base path where the output file is saved

        Output:
            Returns the remapped netcdf-file as well as the output path for the cutting function.
    """
    # If cdo is not in the path, add it manually
    conda_bin = os.path.expanduser('~/.conda/envs/climxtract/bin')
    os.environ['PATH'] += f':{conda_bin}'

    # Extract the filename from the source file
    filename = source_file.split('/')[-1]

    # Modify the filename to include '_remapdis' before the .nc extension
    file = filename.replace(".nc", "_remapdis.nc")
    output_file = f"{output_path_regrid}/{file}"

    # check whether the file already exits and return the path of the file
    if os.path.exists(output_file):
        return output_file
    else:
        # Initialize the Cdo object
        cdo = Cdo()

        # Perform the regridding using the remapdis method
        cdo.remapdis(target_file, input=source_file, output=output_file)
        return output_file