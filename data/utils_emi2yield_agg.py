import numpy as np
import pandas as pd
import xarray as xr
from eofs.xarray import Eof

# CONFIGURE BELOW
data_path = "./CMIP6_input/"

max_co2 = 9500
def normalize_co2(data):
    return data / max_co2

def un_normalize_co2(data):
    return data * max_co2

max_ch4 = 0.8
def normalize_ch4(data):
    return data / max_ch4

def un_normalize_ch4(data):
    return data * max_ch4

# Normalization for BC and SO2
max_bc = 1.0  
max_so2 = 1.0  

def normalize_bc(data):
    return data / max_bc

def normalize_so2(data):
    return data / max_so2


def create_predictor_data(data_sets):
    """
    Args:
        data_sets list(str): names of datasets
    """
        
    if isinstance(data_sets, str):
        data_sets = [data_sets]
    
    # Open datasets
    X = xr.concat([xr.open_dataset(data_path + f"inputs_{file}.nc") for file in data_sets], dim='time')
    X = X.assign_coords(time=np.arange(len(X.time)))

    # Sum BC and SO2 over lat and lon
    bc_summed = X['BC'].sum(dim=['latitude', 'longitude']).data
    so2_summed = X['SO2'].sum(dim=['latitude', 'longitude']).data

    # Normalize summed values
    bc_summed = normalize_bc(bc_summed)
    so2_summed = normalize_so2(so2_summed)

    inputs = pd.DataFrame({
        "CO2": normalize_co2(X["CO2"].data),
        "CH4": normalize_ch4(X["CH4"].data),
        "BC": bc_summed,  # Summed BC
        "SO2": so2_summed  # Summed SO2
    }, index=X["CO2"].coords['time'].data)

    return inputs


def get_test_data(file):
    """
    Args:
        file str: name of dataset
    """
        
    X = xr.open_dataset(data_path + f"inputs_{file}.nc")
        
    # Sum BC and SO2 over lat and lon
    bc_summed = X['BC'].sum(dim=['latitude', 'longitude']).data
    so2_summed = X['SO2'].sum(dim=['latitude', 'longitude']).data

    # Normalize summed values
    bc_summed = normalize_bc(bc_summed)
    so2_summed = normalize_so2(so2_summed)

    # Create DataFrame for test inputs
    inputs = pd.DataFrame({
        "CO2": normalize_co2(X["CO2"].data),
        "CH4": normalize_ch4(X["CH4"].data),
        "BC": bc_summed,  # Summed BC
        "SO2": so2_summed  # Summed SO2
    }, index=X["CO2"].coords['time'].data)

    return inputs