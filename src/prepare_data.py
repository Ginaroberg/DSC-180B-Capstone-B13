import os
import argparse
import requests
import xarray as xr
import glob
from tqdm import tqdm
import tarfile


def download(url, dest_folder):
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


def unzip_tar(download_dir, dest_folder):
    with tarfile.open(download_dir+'train_val.tar.gz', "r:gz") as tar:
        tar.extractall(path=dest_folder)
    print(f"Extracted train_val.tar.gz to {dest_folder}")



def download_output_files(file_path, download_dir):
    try:
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        
    for url in urls:
        download(url, download_dir)



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
                print(f"Warning: {fpath} has multiple data_vars: {data_vars}.")
                
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
    parser = argparse.ArgumentParser(description="Prepare training data")
    parser.add_argument("action", choices=["download", "process"], help="args: download, process")
    args = parser.parse_args()
    
    input_url = "https://zenodo.org/records/7064308/files/train_val.tar.gz"
    output_urls = "impact_model_output.txt"
    download_dir = "./downloads/"
    input_dir = "./Input4MIPs/"
    processed_output_dir = "./processed_output/"
    os.makedirs(download_dir, exist_ok=True)
    
    if args.action == "download":
        download(input_url, download_dir)
        download_output_files(output_urls, download_dir)
        print("All downloads completed.")
    elif args.action == "process":
        unzip_tar(download_dir, input_dir)
        process_output(download_dir, processed_output_dir)
        print("Output Data processing completed.")

if __name__ == "__main__":
    main()
