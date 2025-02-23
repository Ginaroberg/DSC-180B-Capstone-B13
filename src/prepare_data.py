import os
import argparse
import requests
import xarray as xr
import glob
from tqdm import tqdm

def download_files(input_urls, output_urls, download_dir):
    os.makedirs(download_dir, exist_ok=True)
    
    def download_file(url, dest_folder):
        local_filename = os.path.join(dest_folder, url.split("/")[-1])
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            
            with open(local_filename, 'wb') as f, tqdm(
                desc=local_filename,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))
            print(f"Downloaded: {local_filename}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")
    
    for file_path in [input_urls, output_urls]:
        try:
            with open(file_path, 'r') as file:
                urls = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            urls = []
        
        for url in urls:
            download_file(url, download_dir)

    print("All downloads completed.")

def aggregate_input_to_yearly(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    for file_path in glob.glob(os.path.join(input_dir, "*_daily_*.nc")):
        try:
            ds = xr.open_dataset(file_path)
            if 'time' not in ds.dims:
                raise ValueError("The dataset does not have a 'time' dimension.")
            ds_yearly = ds.resample(time='YS').mean()
            ds_yearly['time'] = ds_yearly['time'].dt.year
            yearly_file_name = os.path.basename(file_path).replace('_daily', '_yearly')
            ds_yearly.to_netcdf(os.path.join(output_dir, yearly_file_name))
            print(f"Saved: {yearly_file_name}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

def merge_yearly_input_by_experiments(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    pattern = os.path.join(input_dir, "*_global_yearly_*.nc")
    all_files = sorted(glob.glob(pattern))
    exp_files = {}
    
    for fpath in all_files:
        fname = os.path.basename(fpath)
        parts = fname.split('_')
        try:
            experiment = parts[3]
            var_name = parts[4]
            start_year = int(parts[7])
        except (IndexError, ValueError):
            continue
        
        keep_file = (experiment.lower() == "picontrol" and start_year >= 2011) or \
                    (experiment.lower() == "historical") or \
                    (experiment.lower() not in ["picontrol", "historical"] and start_year >= 2015)
        
        if keep_file:
            exp_files.setdefault(experiment, {}).setdefault(var_name, []).append(fpath)
    
    for experiment, var_dict in exp_files.items():
        merged_vars = [xr.concat([xr.open_dataset(f) for f in filelist], dim="time") for filelist in var_dict.values()]
        ds_merged = xr.merge(merged_vars)
        out_fname = f"inputs_{experiment}.nc"
        ds_merged.to_netcdf(os.path.join(output_dir, out_fname))
        print(f"Saved merged dataset for {experiment} to {out_fname}")

def process_output(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    major_crops = {"wwh", "swh", "mai", "soy", "ri1", "ri2"}
    
    patterns = {"future": "*_2015_2100.nc", "historical": "*_1850_2014.nc"}
    
    for key, pattern in patterns.items():
        all_files = sorted(glob.glob(os.path.join(input_dir, pattern)))
        exp_to_dsets = {}
        
        for fpath in all_files:
            fname = os.path.basename(fpath)
            parts = fname.split('_')
            
            experiment = parts[3]
            if key == "historical" and experiment != "historical":
                continue
            
            crop_part = parts[6]
            crop_name = crop_part.replace("yield-", "").replace("-noirr", "")
            
            if crop_name not in major_crops:
                continue
            
            ds = xr.open_dataset(fpath, decode_times=False)
            
            data_vars = list(ds.data_vars)
            if len(data_vars) == 1:
                old_var_name = data_vars[0]
                ds = ds.rename({old_var_name: crop_name})
            else:
                print(f"Warning: {fpath} has multiple data_vars: {data_vars}. Adjust script if necessary.")
                
            exp_to_dsets.setdefault(experiment, []).append(ds)
        
        for experiment, ds_list in exp_to_dsets.items():
            print(f"\nAggregating major crops for experiment: {experiment}")
            ds_merged = xr.merge(ds_list)
            
            for ds in ds_list:
                ds.close()
            
            out_fname = f"lpjml_{experiment}_{'2015_2100' if key == 'future' else '1850_2014'}.nc"
            out_path = os.path.join(output_dir, out_fname)
            
            ds_merged['time'] = ds_merged['time'] + 1601
            ds_merged.to_netcdf(out_path)
            ds_merged.close()
            
            print(f"  -> Saved merged dataset for '{experiment}' with {len(ds_list)} major-crop files to {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Prepare climate impact model data")
    parser.add_argument("action", choices=["download", "process_input", "process_output"], help="Action to perform: download, process_input, or process_output")
    args = parser.parse_args()
    
    input_urls = "impact_model_input.txt"
    output_urls = "impact_model_output.txt"
    download_dir = "downloads"
    yearly_dir = "input_yearly"
    processed_input_dir = "processed_input"
    processed_output_dir = "processed_output"
    
    if args.action == "download":
        download_files(input_urls, output_urls, download_dir)
    elif args.action == "process_input":
        aggregate_input_to_yearly(download_dir, yearly_dir)
        merge_yearly_input_by_experiments(yearly_dir, processed_input_dir)
        print("Input Data processing completed.")
    elif args.action == "process_output":
        process_output(download_dir, processed_output_dir)
        print("Output Data processing completed.")

if __name__ == "__main__":
    main()
