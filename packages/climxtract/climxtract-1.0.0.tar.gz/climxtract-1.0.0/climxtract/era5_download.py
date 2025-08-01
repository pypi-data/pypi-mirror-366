# era5_download.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Maximilian Meindl, University of Vienna
"""

import cdsapi
import zipfile
import os
import xarray as xr
import numpy as np
from datetime import datetime, timedelta


def load_era5(model_global, variable, start, end, output_path):
    """
    Download hourly ERA5 data from the Copernicus Climate Data Store using the
    CDS API and convert hourly data into daily means.

        Input:
            model_global          str          name of the dataset
            variable_long         str          variable name
            start                 str          start date (e.g. 20200901)
            end                   str          end date (e.g. 20200930)
            output_path           str          path where netCDF file is stored

        Output:
            Returns the path of the netCDF file containing the ERA5 daily mean
            data calculated from downloaded hourly data.
    """
    # Define filename
    file = f"{variable}_{model_global}_{start}-{end}.nc"
    output_file = os.path.join(output_path, file)

    # Check whether the file already exists and return the path of the file
    if os.path.exists(output_file):
        print("Loaded data successfully.")
        return output_file

    else:
        # Check variable consistency for temperature
        if variable == 'tas':
            variable_long = '2m_temperature'

        # Check variable consistency for precipitation
        if variable == 'pr':
            variable_long = 'total_precipitation'

        try:
            # Initialize the API client
            client = cdsapi.Client()

            # Convert strings to datetime objects
            start_date = datetime.strptime(start, "%Y%m%d")
            end_date = datetime.strptime(end, "%Y%m%d")

            # Generate list of years, months, and days
            date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

            years = sorted(list(set(date.strftime("%Y") for date in date_range)))
            months = sorted(list(set(date.strftime("%m") for date in date_range)))
            days = sorted(list(set(date.strftime("%d") for date in date_range)))

            dataset = model_global
            request = {
                "product_type": ["reanalysis"],
                "variable": variable_long,
                "year": years,
                "month": months,
                "day": days,
                "time": [
                    "00:00", "01:00", "02:00",
                    "03:00", "04:00", "05:00",
                    "06:00", "07:00", "08:00",
                    "09:00", "10:00", "11:00",
                    "12:00", "13:00", "14:00",
                    "15:00", "16:00", "17:00",
                    "18:00", "19:00", "20:00",
                    "21:00", "22:00", "23:00"
                ],
                "area": [80, -50, 20, 75],
                "data_format": "netcdf",
                "download_format": "zip"
            }

            target = os.path.join(output_path, 'download.zip')

            client.retrieve(dataset, request, target)
            print("Downloaded data successfully.")

        except Exception as e:
            print("Failed to download data.")
            print(f"\nAn error occured: {e}")

        # Unzipping the file and saving the contents to the specified directory
        with zipfile.ZipFile(target, 'r') as zip_ref:
            # Extract all files
            zip_ref.extractall(output_path)

            # List the files inside the zip
            extracted_files = zip_ref.namelist()

        # Get the full path of each extracted file
        filename = [os.path.join(output_path, file) for file in extracted_files]

        # Take list and convert into a string
        filename = ' '.join(filename)

        # Remove downloaded zip file
        os.remove(target)

        # Open previously downloaded hourly dataset
        dataset = xr.open_dataset(filename)

        if variable == 'tas':

            # Rename the variable
            dataset = dataset.rename({'t2m': variable})

            # Calculate daily means based on hourly data
            daily_mean = dataset.resample(valid_time='1D').mean(dim='valid_time')

            # Rename the time coordinate
            daily_mean = daily_mean.rename({'valid_time': 'time'})

            # Convert from kelvin to celsius
            daily_mean[variable] = daily_mean[variable] - 273.15

            # write dataset contents to a netCDF file
            daily_mean.to_netcdf(output_file)

        # ERA5-Land hourly precip data to total precip for a day
        if variable == 'pr' and model_global == 'reanalysis-era5-land':

            # Rename the variable
            dataset = dataset.rename({'tp': variable})

            # Get all 00UTC time steps, because it contains the accumulated precip
            daily_sum = dataset.sel(valid_time=dataset.valid_time.dt.hour == 0)

            # Assign the precipitation to the previous day explicitly:
            daily_sum = daily_sum.assign_coords(
                valid_time=(daily_sum.valid_time - np.timedelta64(1, 'D'))
            )

            # Rename the time coordinate
            daily_sum = daily_sum.rename({'valid_time': 'time'})

            # Convert from meters to millimeters
            daily_sum[variable] = daily_sum[variable]*1000

            # Write dataset contents to a netCDF file
            daily_sum.to_netcdf(output_file)

        # ERA5 hourly precip data to total precip for a day
        if variable == 'pr' and model_global == 'reanalysis-era5-single-levels':

            # Rename the variable
            dataset = dataset.rename({'tp': variable})

            # Convert from m to mm
            dataset[variable] = dataset[variable]*1000

            # Round times to the nearest hour to avoid datetime issues
            dataset['valid_time'] = dataset['valid_time'].dt.round('1h')

            # Prepare output list
            daily_pr_list = []

            # Get date range from dataset (floor to day)
            dates = np.arange(
                dataset.valid_time.dt.floor('D')[0].values,
                dataset.valid_time.dt.floor('D')[-1].values,
                np.timedelta64(1, 'D')
            )

            for day in dates:
                day = np.datetime64(day)

                # Select hours 01 to 23 of day `d`
                pr_d = dataset.pr.sel(
                    valid_time=slice(day + np.timedelta64(1, 'h'),
                                     day + np.timedelta64(23, 'h')))

                # Select 00 UTC of day `d+1` (this is hour 24 of day `d`)
                pr_d1_00 = dataset.pr.sel(
                    valid_time=day + np.timedelta64(1, 'D'))  # 00 UTC next day

                # Sum all 24 hourly values
                pr_daily = pr_d.sum(dim='valid_time') + pr_d1_00

                # Assign the time label back to day `d`
                pr_daily = pr_daily.expand_dims(valid_time=[day])

                daily_pr_list.append(pr_daily)

            # Combine into a daily DataArray
            daily_precip = xr.concat(daily_pr_list, dim='valid_time')

            # Rename the time coordinate
            daily_precip = daily_precip.rename({'valid_time': 'time'})

            # Write dataset contents to a netCDF file
            daily_precip.to_netcdf(output_file)

        # Remove original file
        os.remove(filename)

        return output_file