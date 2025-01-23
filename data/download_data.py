import os
import requests

# File containing the list of URLs
input_files = "input_files.txt"
output_files = "output_files.txt"

# Directory to save the files
input_download_dir = "" # configure this
output_download_dir = "" # configure this

os.makedirs(input_download_dir, exist_ok=True)
os.makedirs(output_download_dir, exist_ok=True)



# Function to download a file
def download_file(url, dest_folder):
    local_filename = os.path.join(dest_folder, url.split("/")[-1])
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024): # 1 MB
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)
        print(f"Downloaded: {local_filename}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")




# Download input files
try:
    with open(input_files, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]
except FileNotFoundError:
    print(f"Error: The file '{input_files}' was not found.")
    urls = []

for url in urls:
    download_file(url, input_download_dir)

print("All input file downloads completed.")



# Download output files
try:
    with open(output_files, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]
except FileNotFoundError:
    print(f"Error: The file '{output_files}' was not found.")
    urls = []

for url in urls:
    download_file(url, output_download_dir)

print("All output file downloads completed.")
