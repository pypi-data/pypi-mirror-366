# destine_download.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Maximilian Meindl, University of Vienna
"""

import os
import xarray as xr
from polytope.api import Client
import glob
import shutil
from cdo import Cdo
from importlib.resources import files


def load_destine(model_global, variable, experiment, start, end,
                 output_path):
    """
    Download hourly Destination Earth DT data via the Polytope web service
    hosted on the LUMI Databridge.

        Input:
            model_global    str     name of the global model
            variable        str     variable name (e.g. 2 metre temperature)
            experiment      str     climate change scenario
            start           str     start (e.g. 20200901)
            end             str     end (e.g. 20200930)
            output_path     str     path where netCDF file is stored

        Output:
            Returns the path of the netCDF file containing the DestinE
            daily mean data calculated from downloaded hourly data.
    """
    # Define filename
    file = f"{variable}_{model_global}_{start}-{end}.nc"
    output_file = os.path.join(output_path, file)

    # Check whether the file already exists and return the path of the file
    if os.path.exists(output_file):
        print("Loaded data successfully.")
        return output_file

    else:
        # Define temporary directory
        output_path_temp = os.path.join(output_path, "tmp")

        # Ensure the temporary directory exists
        os.makedirs(output_path_temp, exist_ok=True)

        # Define filename for temporal output
        temp_file = os.path.join(output_path_temp, file)

        # Define range of dates to be downloaded
        dates = xr.cftime_range(
            start=start,
            end=end,
            freq='1D',
            inclusive='both', 
            calendar='proleptic_gregorian'
        )

        for date in dates:
            date = date.strftime('%Y%m%d')

            fn = os.path.join(output_path_temp, f'{model_global}-climate-dt_{variable}_high_hourly_{date}.grib')
            if os.path.isfile(fn):
                continue

            # Initialize client
            client = Client(
                address="polytope.lumi.apps.dte.destination-earth.eu",
            )

            # Optionally revoke previous requests
            client.revoke("all")

            # Check experiment/activity consistency for scenario simulation
            if experiment == 'SSP3-7.0':
                activity = 'ScenarioMIP'

            # Check experiment/activity consistency for historical simulation
            if experiment == 'hist':
                activity = 'CMIP6'

            # Check variable consistency for temperature
            if variable == 'tas':
                variable_request = '167'

            # Check variable consistency for precipitation
            if variable == 'pr':
                variable_request = '260048'

            request = {
                "activity": activity,
                "class": "d1",
                "dataset": "climate-dt",
                "date": date,
                "experiment": experiment,
                "expver": "0001",
                "generation": "1",
                "levtype": "sfc",
                "model": model_global,
                "param": variable_request,
                "realization": "1",
                "resolution": "high",
                "stream": "clte",
                "time": "0000/0100/0200/0300/0400/0500/0600/0700/0800/0900/1000/1100/1200/1300/1400/1500/1600/1700/1800/1900/2000/2100/2200/2300",
                "type": "fc",
            }

            try:
                retrieve = client.retrieve(
                    "destination-earth",
                    request, 
                    output_file=fn, 
                    pointer=False)
                print(f'{date=}...DONE')

            except Exception:
                print(f'{date=}...FAIL')
                continue

        # Glob all GRIB files in the directory
        grib_files = sorted(glob.glob(os.path.join(output_path_temp, "*.grib")))

        for grib_file in grib_files:
            # Open the GRIB file
            dataset = xr.open_dataset(grib_file, engine="cfgrib")

            if variable == 'tas':
                # Rename the variable
                dataset = dataset.rename({'t2m': variable})

                # Calculate the daily mean
                daily_mean = dataset.resample(valid_time="1D").mean(dim="time")

                # Rename the time coordinate
                daily_mean = daily_mean.rename({'valid_time': 'time'})

                # Convert from Kelvin to Celsius
                daily_mean[variable] = daily_mean[variable] - 273.15

                # Generate an output file name
                base_name = os.path.basename(grib_file).replace(".grib", "_daily_mean.nc")
                daily_file = os.path.join(output_path_temp, base_name)

                # Save the daily mean to a NetCDF file
                daily_mean.to_netcdf(daily_file)

            if variable == 'pr':
                # Rename the variable
                dataset = dataset.rename({'tprate': variable})

                # Calculate the daily mean
                daily_mean = dataset.resample(valid_time="1D").mean(dim="time")

                # Rename the time coordinate
                daily_mean = daily_mean.rename({'valid_time': 'time'})

                # Convert from kg/m² second into kg/m² day
                daily_mean[variable] = daily_mean[variable]*86400

                # Generate an output file name
                base_name = os.path.basename(grib_file).replace(".grib", "_daily_mean.nc")
                daily_file = os.path.join(output_path_temp, base_name)

                # Save the daily mean to a NetCDF file
                daily_mean.to_netcdf(daily_file)

        # Use CDO to merge netcdf files
        daily_files = sorted(glob.glob(os.path.join(output_path_temp, "*_daily_mean.nc")))

        if daily_files:
            # Convert the list of files into a space-separated string
            file_list = " ".join(daily_files)

            # If cdo is not in the path, add it manually
            conda_bin = os.path.expanduser('~/.conda/envs/climxtract/bin')
            os.environ['PATH'] += f':{conda_bin}'

            # Initialize the Cdo object
            cdo = Cdo()

            # Perform merging of files on the time dimension
            cdo.mergetime(input=file_list, output=temp_file)

            # Dynamically get the file path to healpix_grid.txt inside the package
            healpix_grid_path = files('climxtract').joinpath('healpix_grid.txt')

            # Set grid from unstructured (default Destination Earth) to healpix for conservative regridding
            cdo.setgrid(str(healpix_grid_path), input=temp_file, output=output_file)

        # Path to the directory you want to remove
        shutil.rmtree(output_path_temp)

        return output_file