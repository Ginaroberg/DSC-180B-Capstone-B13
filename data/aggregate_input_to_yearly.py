import xarray as xr
import os

input_folder = "" # configure this

def aggregate_input(file_name):
    """
    Aggregates daily values in an xarray dataset into yearly means.
    Saves the aggregated datasets to new NetCDF files.

    Parameters:
        file_name (str): Path to the input NetCDF file with daily data.

    Returns:
        None
    """
    try:
        # Load the dataset
        ds = xr.open_dataset(input_folder + file_name)

        # Ensure time dimension exists
        if 'time' not in ds.dims:
            raise ValueError("The dataset does not have a 'time' dimension.")

        # Aggregate to monthly means
        # ds_monthly_start = ds.resample(time='MS').mean()
        # ds_monthly_start['time'] = ds_monthly_start.dt.year
        # monthly_file_name = file_name.replace('_daily', '_monthly')
        # ds_monthly_start.to_netcdf(f'/glade/derecho/scratch/qzou/input_monthly/{monthly_file_name}')
        # print(f"{monthly_file_name} saved")

        # Aggregate to yearly means
        ds_yearly = ds.resample(time='YS').mean()
        ds_yearly['time'] = ds_yearly['time'].dt.year
        yearly_file_name = file_name.replace('_daily', '_yearly')
        ds_yearly.to_netcdf(f'/glade/derecho/scratch/qzou/input_yearly/{yearly_file_name}')
        print(f"{yearly_file_name} saved")

    except Exception as e:
        print(f"An error occurred: {e}")


filenames = [f for f in os.listdir(input_folder) if f.endswith('.nc')]

for fn in filenames:
    aggregate_input(fn)