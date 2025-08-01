# eobs_download.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Maximilian Meindl, University of Vienna
"""

import os
import wget
import shutil
from cdo import Cdo


def load_eobs(variable, start, end, output_path):
    """
    Download daily E-OBS data from European Climate Assessment & Dataset.
    The complete dataset from 1950 onwards is downloaded and saved.

        Input:
            variable       str          variable name (e.g. 2m_temperature)
            start          str          start year (1950)
            end            str          end year (2024)
            output_path    str          path where netCDF file is stored

        Output:
            Returns the path of the netCDF file containing the ERA5 daily mean data.
    """
    # Define filename
    file = f"{variable}_e-obs30.e_{start}-{end}.nc"
    output_file = os.path.join(output_path, file)

    # Check whether the file already exists and return the path of the file
    if os.path.exists(output_file):
        print("Loaded data successfully.")
        return output_file

    else:
        # Check variable consistency for temperature
        if variable == 'tas':
            variable_long = 'tg'

        # Check variable consistency for precipitation
        if variable == 'pr':
            variable_long = 'rr'

        # Define temporary directory
        output_path_temp = os.path.join(output_path, "tmp")

        # Ensure the temporary directory exists
        os.makedirs(output_path_temp, exist_ok=True)

        # Define filename for temporal output
        temp_file = os.path.join(output_path_temp, file)

        try:
            # Putting together the download link (url)
            base_url = "https://knmi-ecad-assets-prd.s3.amazonaws.com/ensembles/data/"
            url_directory = base_url + "Grid_0.1deg_reg_ensemble/"
            filename = str(variable_long) + "_" + "ens_mean_0.1deg_reg_v30.0e.nc"
            url = url_directory + filename

            # Download the file using the wget package
            wget.download(url, out=temp_file)
            print("Downloaded data successfully.")

        except Exception as e:
            print("Failed to download data.")
            print(f"\nAn error occured: {e}")

        # If cdo is not in the path, add it manually
        conda_bin = os.path.expanduser('~/.conda/envs/climxtract/bin')
        os.environ['PATH'] += f':{conda_bin}'

        # Initialize the Cdo object
        cdo = Cdo()

        if variable == 'tas':
            # Rename the variable
            cdo.chname("tg", "tas", input=temp_file, output=output_file)

        if variable == 'pr':
            # Rename the variable
            cdo.chname("rr", "pr", input=temp_file, output=output_file)

        # Path to the directory you want to remove
        shutil.rmtree(output_path_temp)

        return output_file