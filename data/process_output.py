import os
import glob
import xarray as xr

def process_output_major_crops(input_dir, output_dir):
    """
    1. Finds files ending with "_2015_2100.nc" in `input_dir`.
    2. Parses `experiment` = parts[3] (e.g. "picontrol", "ssp126", "ssp370", "ssp585", etc.)
    3. Parses `crop` from parts[6] (e.g. "yield-mai-noirr") and extracts "mai", "ri1", etc.
    4. Skips any crop not in the major crops list.
    5. Opens each file, renames the primary variable to the crop name.
    6. Groups these renamed Datasets by experiment.
    7. Merges all crops into one dataset per experiment (so each crop is a separate variable).
    8. Writes "lpjml_{experiment}_2015_2100.nc" for each experiment.
    """

    major_crops = {"wwh", "swh", "mai", "soy", "ri1", "ri2"}

    os.makedirs(output_dir, exist_ok=True)

    pattern = os.path.join(input_dir, "*_2015_2100.nc")
    all_files = sorted(glob.glob(pattern))

    exp_to_dsets = {} # { experiment : list_of_datasets }



    # Example: 
    # lpjml_mri-esm2-0_w5e5_picontrol_2015soc_default_yield-mai-noirr_global_annual-gs_2015_2100.nc
    #
    # parts[3] = "picontrol" (experiment)
    # parts[6] = "yield-mai-noirr" -> parse to get the crop name "mai"
    
    for fpath in all_files:
        fname = os.path.basename(fpath)
        parts = fname.split('_')

        if len(parts) < 10:
            continue  # skip if doesn't match the pattern

        experiment = parts[3]
        crop_part = parts[6]
        # Extract the actual crop name
        crop_name = crop_part.replace("yield-", "").replace("-firr", "")

        # If this crop is not one of the major crops, skip it
        if crop_name not in major_crops:
            continue

        ds = xr.open_dataset(fpath, decode_times=False)

        # If there's exactly one data variable, rename it to the crop_name:
        data_vars = list(ds.data_vars)
        if len(data_vars) == 1:
            old_var_name = data_vars[0]
            ds = ds.rename({old_var_name: crop_name})
        else:
            print(f"Warning: {fpath} has multiple data_vars: {data_vars}. "
                  f"Adjust script to rename correctly.")
            pass

        exp_to_dsets.setdefault(experiment, []).append(ds)

    # Now combine each experiment's datasets into one dataset
    for experiment, ds_list in exp_to_dsets.items():
        print(f"\nAggregating major crops for experiment: {experiment}")
        # Merge all these datasets, so each crop becomes a separate variable
        ds_merged = xr.merge(ds_list)

        # Close each input dataset
        for ds in ds_list:
            ds.close()

        # Write out as "lpjml_{experiment}_2015_2100.nc"
        out_fname = f"lpjml_{experiment}_2015_2100.nc"
        out_path = os.path.join(output_dir, out_fname)
        
        ds_merged['time'] = ds_merged['time'] + 1601
        ds_merged.to_netcdf(out_path)
        ds_merged.close()

        print(f"  -> Saved merged dataset for '{experiment}' with "
              f"{len(ds_list)} major-crop files to {out_path}")





def process_historical_major_crops(input_dir, output_dir):
    """
    1. Finds files ending with "_2015_2100.nc" in `input_dir`.
    2. Parses `experiment` = parts[3] (e.g. "picontrol", "ssp126", "ssp370", "ssp585", etc.)
    3. Parses `crop` from parts[6] (e.g. "yield-mai-noirr") and extracts "mai", "ri1", etc.
    4. Skips any crop not in the major crops list.
    5. Opens each file, renames the primary variable to the crop name.
    6. Groups these renamed Datasets by experiment.
    7. Merges all crops into one dataset per experiment (so each crop is a separate variable).
    8. Writes "lpjml_{experiment}_2015_2100.nc" for each experiment.
    """

    major_crops = {"wwh", "swh", "mai", "soy", "ri1", "ri2"}

    os.makedirs(output_dir, exist_ok=True)

    pattern = os.path.join(input_dir, "*_1850_2014.nc")
    all_files = sorted(glob.glob(pattern))

    exp_to_dsets = {} # { experiment : list_of_datasets }



    # Example: 
    # lpjml_mri-esm2-0_w5e5_picontrol_2015soc_default_yield-mai-noirr_global_annual-gs_2015_2100.nc
    #
    # parts[3] = "picontrol" (experiment)
    # parts[6] = "yield-mai-noirr" -> parse to get the crop name "mai"
    
    for fpath in all_files:
        fname = os.path.basename(fpath)
        parts = fname.split('_')

        if len(parts) < 10:
            continue  # skip if doesn't match the pattern

        experiment = parts[3]
        if experiment != 'historical':
            continue
            
        crop_part = parts[6]
        # Extract the actual crop name
        crop_name = crop_part.replace("yield-", "").replace("-firr", "")

        # If this crop is not one of the major crops, skip it
        if crop_name not in major_crops:
            continue

        ds = xr.open_dataset(fpath, decode_times=False)

        # If there's exactly one data variable, rename it to the crop_name:
        data_vars = list(ds.data_vars)
        if len(data_vars) == 1:
            old_var_name = data_vars[0]
            ds = ds.rename({old_var_name: crop_name})
        else:
            print(f"Warning: {fpath} has multiple data_vars: {data_vars}. "
                  f"Adjust script to rename correctly.")
            pass

        exp_to_dsets.setdefault(experiment, []).append(ds)

    # Now combine each experiment's datasets into one dataset
    for experiment, ds_list in exp_to_dsets.items():
        print(f"\nAggregating major crops for experiment: {experiment}")
        # Merge all these datasets, so each crop becomes a separate variable
        ds_merged = xr.merge(ds_list)

        # Close each input dataset
        for ds in ds_list:
            ds.close()

        # Write out as "lpjml_{experiment}_2015_2100.nc"
        out_fname = f"lpjml_{experiment}_1850_2014.nc"
        out_path = os.path.join(output_dir, out_fname)
        
        ds_merged['time'] = ds_merged['time'] + 1601
        ds_merged.to_netcdf(out_path)
        ds_merged.close()

        

        print(f"  -> Saved merged dataset for '{experiment}' with "
              f"{len(ds_list)} major-crop files to {out_path}")


