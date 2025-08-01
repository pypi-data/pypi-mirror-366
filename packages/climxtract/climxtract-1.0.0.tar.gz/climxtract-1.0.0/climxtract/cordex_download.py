# cordex_download.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Maximilian Meindl, University of Vienna
"""

import os
import wget
import glob
import shutil
import xarray as xr
from pyesgf.search import SearchConnection
from datetime import datetime
from cdo import Cdo


# Function to find matching URLs
def find_matching_urls(urls, target_start_dt, target_end_dt):
    matching_urls = []
    for url in urls:
        # Extract date range from URL
        parts = url.split("_")[-1].replace(".nc", "").split("-")
        start_dt = datetime.strptime(parts[0], "%Y%m%d")
        end_dt = datetime.strptime(parts[1], "%Y%m%d")

        # Check if the file falls within the target range
        if start_dt >= target_start_dt and end_dt <= target_end_dt:
            matching_urls.append(url)

    return matching_urls


def load_cordex(model_global, model_regional, variable, experiment, ens,
                start, end, output_path):
    """
    Download CORDEX data from ESGF using the ESGF Pyclient.

        Input:
            model_global       str      name of the global climate model
            model_regional     str      name of the regional climate model
            variable           str      variable name (e.g. tas)
            experiment         str      name of the experiment (eg. historical)
            start              str      start date (e.g. 20160101)
            end                str      end date (e.g. 20201231)
            output_directory   str      path where the netCDF file is stored

        Output:
            Returns the path of the netCDF file containing the CORDEX data.
    """
    # Define filename
    file = (
        f"{variable}_{model_global}_{experiment}_{ens}_"
        f"{model_regional}_{start}-{end}.nc"
    )
    output_file = os.path.join(output_path, file)

    # Check whether the file already exits and return the path of the file
    if os.path.exists(output_file):
        print("Loaded data successfully.")
        return output_file

    else:
        # Define temporary directory
        output_path_temp = os.path.join(output_path, "tmp")

        # Ensure the temporary directory exists
        os.makedirs(output_path_temp, exist_ok=True)

        # Define filname for temporal output
        temp_file = os.path.join(output_path_temp, file)

        try:
            hostname = "esgf.ceda.ac.uk"
            url = "http://{}/esg-search".format(hostname)

            conn = SearchConnection(url, distrib=True)

            request = {
                "latest": "true",  # Search for the latest data
                "domain": "EUR-11",
                "variable": variable,
                "driving_model": model_global,
                "rcm_name": model_regional,
                "time_frequency": "day",
                "experiment": experiment,
                "ensemble": ens,
            }

            ctx = conn.new_context(facets='project', **request)
            ds = ctx.search()[0]
            files = ds.file_context().search()

            # Get list of URLs
            url_list = []
            for f in files:
                url_list.append(f.download_url)

            # Convert target dates to datetime objects
            target_start_dt = datetime.strptime(start, "%Y%m%d")
            target_end_dt = datetime.strptime(end, "%Y%m%d")

            # Find matching URLs
            matching_urls = find_matching_urls(url_list, target_start_dt, target_end_dt)

            for url in matching_urls:
                filename = os.path.join(output_path_temp, os.path.basename(url))
                wget.download(url, filename)
                print("Downloaded data successfully.")

        except Exception as e:
            print("Failed to download data.")
            print(f"\nAn error occured: {e}")

        # Use CDO to merge netcdf files
        daily_files = sorted(glob.glob(os.path.join(output_path_temp, "*.nc")))

        # If cdo is not in the path, add it manually
        conda_bin = os.path.expanduser('~/.conda/envs/climxtract/bin')
        os.environ['PATH'] += f':{conda_bin}'

        # Initialize the Cdo object
        cdo = Cdo()

        if daily_files:
            # Convert the list of files into a space-separated string
            file_list = " ".join(daily_files)

            # Perform merging of files on the time dimension
            cdo.mergetime(input=file_list, output=temp_file)

        dataset = xr.open_dataset(temp_file)

        if variable == 'tas':
            # Convert from Kelvin to Celsius
            dataset[variable] = dataset[variable] - 273.15

        if variable == 'pr':
            # Convert kg m-2 s-1 into kg m-2
            dataset[variable] = dataset[variable]*86400

        # Save dataset to a netCDF file
        dataset.to_netcdf(output_file)

        # Remove the temporary directory
        shutil.rmtree(output_path_temp)

        return output_file