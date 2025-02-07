import xarray as xr
import os
import xesmf as xe

# Define input and output directories
input_folder = "/glade/derecho/scratch/qzou/input_forcing"
output_folder = "/glade/derecho/scratch/qzou/aggregated_forcing"
os.makedirs(output_folder, exist_ok=True)

# SSP scenarios to process
ssp_scenarios = ["ssp126", "ssp245", "ssp370", "ssp370-lowNTCF", "ssp585"]

# Function to load and preprocess gas data (CO2, CH4)
def load_gas_data(variable, scenario):
    """Loads and preprocesses CO2 or CH4 data by concatenating multi-period files."""
    if scenario == "ssp370-lowNTCF":
        file = [
            f"{input_folder}/{variable}_Amon_MRI-ESM2-0_{scenario}_r1i1p1f1_gn_201501-205512.nc",
            f"{input_folder}/{variable}_Amon_MRI-ESM2-0_{scenario}_r1i1p1f1_gn_205601-210012.nc"
        ]
    else:
        file = [
            f"{input_folder}/{variable}_Amon_MRI-ESM2-0_{scenario}_r1i1p1f1_gn_201501-206412.nc",
            f"{input_folder}/{variable}_Amon_MRI-ESM2-0_{scenario}_r1i1p1f1_gn_206501-210012.nc"
        ]
    ds = xr.concat([xr.open_dataset(f) for f in file], dim='time')
    ds = ds.sum('plev')  # Sum over pressure levels
    ds = ds.drop_vars(['time_bnds', 'lat_bnds', 'lon_bnds'], errors='ignore')  # Drop unnecessary variables
    return ds

# Function to load and preprocess aerosol emissions (BC, SO2)
def load_aerosol_data(variable, scenario):
    """Loads and preprocesses aerosol emissions data."""
    if scenario == "ssp370-lowNTCF":
        file = [
            f"{input_folder}/{variable}_AERmon_MRI-ESM2-0_{scenario}_r1i1p1f1_gn_201501-205512.nc",
            f"{input_folder}/{variable}_AERmon_MRI-ESM2-0_{scenario}_r1i1p1f1_gn_205601-210012.nc"
        ]
        ds = xr.concat([xr.open_dataset(f) for f in file], dim='time')
    else:
        file = f"{input_folder}/{variable}_AERmon_MRI-ESM2-0_{scenario}_r1i1p1f1_gn_201501-210012.nc"
        ds = xr.open_dataset(file)
    ds = ds.drop_vars(['time_bnds', 'lat_bnds', 'lon_bnds'], errors='ignore')  # Drop unnecessary variables
    return ds

# Process each SSP scenario
for scenario in ssp_scenarios:
    print(f"Processing {scenario}...")

    # Load gas data
    co2 = load_gas_data("co2", scenario)
    ch4 = load_gas_data("ch4", scenario)

    # Load aerosol data
    bc = load_aerosol_data("emibc", scenario)
    so2 = load_aerosol_data("emiso2", scenario)

    # Use CO2 as the reference dataset for regridding
    reference_ds = co2

    # Create a regridder
    regridder = xe.Regridder(bc, reference_ds, 'conservative', periodic=True)

    # Regrid aerosol data
    bc_regridded = regridder(bc)
    so2_regridded = regridder(so2)

    # Merge all datasets
    ds_aggregated = xr.merge([ch4, co2, so2_regridded, bc_regridded])

    # Save the aggregated dataset
    output_file = f"{output_folder}/inputs_{scenario}.nc"
    ds_aggregated.to_netcdf(output_file)
    
    print(f"Saved aggregated dataset: {output_file}")

print("Processing complete for all SSP scenarios.")
