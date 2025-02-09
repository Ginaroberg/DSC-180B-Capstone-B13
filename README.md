# DSC-180B-Capstone-B13
DSC 180AB Capstone 


## Project Overview

By combining historical data with these climate scenarios, our team is looking to develop a predictive model for crop yields and create an interactive dashboard that visualizes the impact of climate change on global agriculture. Our goal with this project is to highlight the connection between climate policy and food security. 


## Running the Models

To run the models, follow these steps:

1. **Download Data and Preprocess**  
   Use the provided `prepare_data.py` script to execute the necessary data tasks. This script supports three actions—`download`, `process_input`, and `process_output`—to handle downloading, input data preprocessing, and output data processing respectively.

2. **Set Up the Environment**  
   Run the following commands to create and configure a Conda environment:

   ```bash
   conda create -n B13 python=3.10
   conda activate B13
   conda install -c conda-forge notebook xarray matplotlib cartopy eofs scikit-learn
   pip install "esem[gpflow,keras]" netcdf4
   ```

    If you encounter issues with `tensorflow-probability` on macOS, downgrade it to a version compatible with your TensorFlow installation:

    ```bash
    pip install tensorflow-probability==0.24
    ```

3. **Running the Code**  
   Once the environment is set up, you should be able to proceed with running the models on a Jupyter Notebook. Each model involves
   training that may take a long time to run if on a device lacking a CUDA capable GPU. If unable to run on environment, or runtime takes
   too long, a pdf output has been provided of the results of running the Notebook. 

