# imports
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
import cartopy.crs as ccrs
from esem import gp_model
from eofs.xarray import Eof
from utils import *
import gpflow


# Prepare data
train_files= ['ssp126', 'ssp585', 'historical']

Xtrain, eof_solvers = get_Xtrain(train_files)
train_nan_mask = Xtrain.isna().any(axis=1).values
Xtrain = Xtrain.dropna(axis=0, how='any')

Ytrain = get_Ytrain(train_files)

Xtest = get_Xtest('ssp370', eof_solvers)
test_nan_mask = Xtest.isna().any(axis=1).values
Xtest = Xtest.dropna(axis=0, how='any')

Ytest = get_Ytest('ssp370')



# Model training
crops = ['mai', 'ri1', 'ri2', 'soy', 'swh', 'wwh']
models = {}
masks = {}

for crop in crops:
    # Prepare data
    
    # exclude years with missing emission data for training
    Ytrain_yield = Ytrain[crop].values.reshape(-1, 360*720)
    Ytrain_yield = Ytrain_yield[~train_nan_mask]
    assert Xtrain.shape[0]==Ytrain_yield.shape[0]
    
    Ytest_yield = Ytest[crop].values.reshape(-1, 360*720)
    Ytest_yield = Ytest_yield[~test_nan_mask]
    assert Xtest.shape[0]==Ytest_yield.shape[0]

    # use a mask to exclude coordinates with nan yield across all years (these correspond to locations not suitable for growing crops)
    mask_all_nan_by_col = np.isnan(Ytrain_yield).all(axis=0)
    Ytrain_yield_dropped = Ytrain_yield[:, ~mask_all_nan_by_col]
    # then impute the rest with 0
    Y_imputed = np.nan_to_num(Ytrain_yield_dropped, nan=0.0)
    

    
    # Model

    # define kernels
    kernel_CO2 = gpflow.kernels.Matern32(active_dims=[0]) # active_dims specifies which dimension the kernel is applied to
    kernel_CH4 = gpflow.kernels.Matern32(active_dims=[1])
    kernel_BC = gpflow.kernels.Matern32(lengthscales=5 * [1.], active_dims=[2, 3, 4, 5, 6])
    kernel_SO2 = gpflow.kernels.Matern32(lengthscales=5 * [1.], active_dims=[7, 8, 9, 10, 11])
    kernel = kernel_CO2 + kernel_CH4 + kernel_BC + kernel_SO2

    # define model
    np.random.seed(5)
    mean = gpflow.mean_functions.Constant()
    model = gpflow.models.GPR(data=(Xtrain.astype(np.float64), # cast to float64 because gpflow requires numerical stability
                                    Y_imputed.astype(np.float64)),
                              kernel = kernel,
                              mean_function = mean)

    # define optimizer
    optimizer = gpflow.optimizers.Scipy()
    
    # train
    optimizer.minimize(model.training_loss,
                       variables=model.trainable_variables,
                       options=dict(disp=True, maxiter=5000))

    # store the mask
    masks[crop] = mask_all_nan_by_col
    # store the trained model
    models[crop] = model




# Get predictions
predictions = {}
for crop in crops:
    model = models[crop]
    mask_all_nan_by_col = masks[crop]
    
    # predict
    posterior_mean, posterior_var = model.predict_y(Xtest.values) # predicted mean of GP, predicted variance of GP
    posterior_stddev = np.sqrt(posterior_var)
    
    posterior_yield_mean_full = np.full((Xtest.shape[0], Ytrain_yield.shape[1]), np.nan)  # fill with NaN
    posterior_yield_mean_full[:, ~mask_all_nan_by_col] = posterior_mean
    
    posterior_yield_stddev_full = np.full((Xtest.shape[0], Ytrain_yield.shape[1]), np.nan)  # fill with NaN
    posterior_yield_stddev_full[:, ~mask_all_nan_by_col] = posterior_stddev

    # put output back into xarray format for calculating RMSE/plotting
    posterior_yield = np.reshape(posterior_yield_mean_full, [len(Ytest['time']), 360, 720])
    posterior_yield_stddev = np.reshape(posterior_yield_stddev_full, [len(Ytest['time']), 360, 720])
    posterior_yield_data = xr.DataArray(
        posterior_yield,
        dims=("time", "lat", "lon"),
        coords={"time": Ytest["time"], "lat": Ytest["lat"], "lon": Ytest["lon"]}
    )
    posterior_yield_std_data = xr.DataArray(
        posterior_yield_stddev,
        dims=("time", "lat", "lon"),
        coords={"time": Ytest["time"], "lat": Ytest["lat"], "lon": Ytest["lon"]}
    )

    predictions[crop] = {'mean': posterior_yield_data, 'std': posterior_yield_std_data}


# Save predictions
for crop in crops:
    predictions['mai']['mean'].to_netcdf(f'GP_{crop}_prediction.nc')