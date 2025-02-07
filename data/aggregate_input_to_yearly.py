# aggregate to monthly start
import xarray as xr
import os

def aggregate_dataset(file_name):
    """
    Aggregates daily values in an xarray dataset into monthly (month-start) and yearly means.
    Saves the aggregated datasets to new NetCDF files.

    Parameters:
        file_name (str): Path to the input NetCDF file with daily data.

    Returns:
        None
    """
    try:
        # Load the dataset
        path = '/glade/derecho/scratch/qzou/input/'
        ds = xr.open_dataset(path + file_name)

        # Ensure time dimension exists
        if 'time' not in ds.dims:
            raise ValueError("The dataset does not have a 'time' dimension.")

        # # Aggregate to monthly means (month start)
        # ds_monthly_start = ds.resample(time='MS').mean()
        # ds_monthly_start['time'] = ds_monthly_start.dt.year
        # monthly_file_name = file_name.replace('_daily', '_monthly')
        # ds_monthly_start.to_netcdf(f'/glade/derecho/scratch/qzou/input_monthly/{monthly_file_name}')
        # print(f"{monthly_file_name} saved")

        # # Aggregate to quarterly means (quarter start)
        # ds_quarterly = ds.resample(time='QS').mean()
        # quarterly_file_name = file_name.replace('_daily', '_quarterly')
        # ds_quarterly.to_netcdf(f'/glade/derecho/scratch/qzou/input_quarterly/{quarterly_file_name}')
        # print(f"{quarterly_file_name} saved")

        # Aggregate to yearly means
        ds_yearly = ds.resample(time='YS').mean()
        ds_yearly['time'] = ds_yearly['time'].dt.year
        yearly_file_name = file_name.replace('_daily', '_yearly')
        ds_yearly.to_netcdf(f'/glade/derecho/scratch/qzou/input_yearly/{yearly_file_name}')
        print(f"{yearly_file_name} saved")

    except Exception as e:
        print(f"An error occurred: {e}")


filenames = [f for f in os.listdir('/glade/derecho/scratch/qzou/input/') if f.endswith('.nc')]
for fn in filenames:
    aggregate_dataset(fn)