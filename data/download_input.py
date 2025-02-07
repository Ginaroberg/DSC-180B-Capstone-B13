import os
import requests

# File containing the list of URLs
file = "input_files.txt"

# Directory to save the files
download_dir = "/glade/derecho/scratch/qzou/input/"
os.makedirs(download_dir, exist_ok=True)

# Function to download a file
def download_file(url, dest_folder):
    local_filename = os.path.join(dest_folder, url.split("/")[-1])
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)
        print(f"Downloaded: {local_filename}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")

# Read URLs from the file
try:
    with open(file, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]
except FileNotFoundError:
    print(f"Error: The file '{url_file}' was not found.")
    urls = []

# Download all files
for url in urls:
    download_file(url, download_dir)

print("All downloads completed.")
