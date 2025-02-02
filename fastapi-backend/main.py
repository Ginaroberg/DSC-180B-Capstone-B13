import json
import xarray as xr
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
import uuid
from fastapi.responses import FileResponse


app = FastAPI()

# Allow CORS for the frontend (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Path to save the plot images
STATIC_DIR = "static"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# NetCDF file path
NC_FILE_PATH = "./DSC-180B-Capstone-B13/fastapi-backend/fastapi-data/climate-data.nc" ## put local path 

@app.get("/generate-plot")
async def generate_plot(time_index: int, crop: str):
    # Print the received time_index and crop to the console
    print(f"Debug: Received Time Index = {time_index}, Crop = {crop}")

    try:
        # Open the NetCDF file
        ds = xr.open_dataset(NC_FILE_PATH)
        print("Debug: NetCDF file loaded successfully.")
        ds = ds[crop].isel(time=time_index)

        # Extract latitudes and longitudes for plotting
        lats = ds['lat'].values
        lons = ds['lon'].values

        # Set up the plot with Cartopy
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_title(f"{crop.capitalize()} Data for Time Index {time_index}")
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAND, color='lightgray', alpha=0.5)

        # Plot the crop data (as a heatmap or contour map)
        mesh = ax.pcolormesh(lons, lats, ds, transform=ccrs.PlateCarree(), cmap='viridis')

        # Add colorbar
        cbar = fig.colorbar(mesh, ax=ax, orientation='vertical', shrink=0.6)
        cbar.set_label(f"{crop.capitalize()} Value")

        # Save the plot as a PNG file with a unique name
        plot_filename = f"plot_{uuid.uuid4().hex}.png"
        plot_path = os.path.join(STATIC_DIR, plot_filename)
        plt.savefig(plot_path)
        plt.close()

        print(ds)
        # Close the dataset
        ds.close()


        # Return the URL of the generated plot image
        return {"plot_url": f"http://127.0.0.1:8000/static/{plot_filename}"}

    except Exception as e:
        # Handle any errors
        print(f"Error: {str(e)}")
        return {"error": str(e)}

# Serve static files (plot images)
@app.get("/static/{filename}")
async def get_static_file(filename: str):
    return FileResponse(os.path.join(STATIC_DIR, filename))
