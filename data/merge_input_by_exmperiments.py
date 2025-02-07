import os
import glob
import xarray as xr

def aggregate_experiments(input_dir, output_dir):
    """
    - Finds all netCDF files matching "*_global_yearly_*.nc" in `input_dir`.
    - Parses experiment = parts[3], variable = parts[4], start_year = int(parts[7]).
    - Logic:
        If experiment == "picontrol":
            Keep only files that start in 2011 or later (e.g. 2011_2020, 2021_2030, etc.).
            After opening them, subset to time >= 2015.
        Otherwise (e.g. ssp370, ssp585, etc.):
            Keep only files whose start_year >= 2015.
    - Groups by (experiment -> variable), concatenates per variable, merges variables
      into one dataset per experiment, and writes 'inputs_{experiment}.nc'.
    """

    os.makedirs(output_dir, exist_ok=True)

    pattern = os.path.join(input_dir, "*_global_yearly_*.nc")
    all_files = sorted(glob.glob(pattern))

    # Accumulate file paths here: { experiment: { variable: [filepaths] } }
    exp_files = {}

    for fpath in all_files:
        fname = os.path.basename(fpath)
        parts = fname.split('_')
        # e.g.: mri-esm2-0_r1i1p1f1_w5e5_picontrol_pr_global_yearly_2011_2020.nc
        # parts[3] = "picontrol"
        # parts[4] = "pr"
        # parts[7] = "2011"
        try:
            experiment = parts[3]      # e.g. "picontrol", "ssp370", ...
            var_name   = parts[4]      # e.g. "pr", "tas", ...
            start_year = int(parts[7]) # e.g. 2011
        except (IndexError, ValueError):
            # Skip files that don't match expected pattern
            continue

        keep_file = False
        if experiment.lower() == "picontrol":
            # Only keep files that start in 2011 or later
            if start_year >= 2011:
                keep_file = True
        else:
            # For all other experiments, only keep files starting in 2015 or later
            if start_year >= 2015:
                keep_file = True

        if keep_file:
            exp_files.setdefault(experiment, {}) \
                     .setdefault(var_name, []) \
                     .append(fpath)

    # Aggregate each experiment
    for experiment, var_dict in exp_files.items():
        print(f"Processing experiment: {experiment}")
        merged_vars = []  # Will hold a list of (concatenated) Datasets, one per variable

        for var_name, filelist in var_dict.items():
            filelist = sorted(filelist)
            print(f"  -> Variable '{var_name}': {len(filelist)} file(s)")

            ds_list = []
            for fn in filelist:
                ds = xr.open_dataset(fn)

                if experiment.lower() == "picontrol":
                    # Subset to keep only time >= 2015
                    # If your time coordinate is integer-based, e.g. [2011..2020]
                    ds = ds.sel(time=slice(2015, None))

                    # Or if time is a datetime coordinate, do:
                    # ds = ds.where(ds.time.dt.year >= 2015, drop=True)

                # If no time steps remain, skip
                if not ds.time.size:
                    ds.close()
                    continue

                ds_list.append(ds)

            if not ds_list:
                print(f"    No data remains for variable '{var_name}' after subsetting.")
                continue

            # Concatenate along 'time'
            ds_concat = xr.concat(ds_list, dim="time")

            # Close each partial dataset
            for ds_tmp in ds_list:
                ds_tmp.close()

            merged_vars.append(ds_concat)

        if not merged_vars:
            print(f"  -> No valid data for experiment '{experiment}' after filtering.")
            continue

        # Merge all variables for this experiment
        ds_merged = xr.merge(merged_vars)

        # Write out a single file for this experiment
        out_fname = f"inputs_{experiment}.nc"
        out_path  = os.path.join(output_dir, out_fname)

        ds_merged.to_netcdf(out_path)
        ds_merged.close()

        print(f"  -> Saved merged dataset for '{experiment}' to {out_path}")

        # Close each variable dataset
        for ds_var in merged_vars:
            ds_var.close()
