import numpy as np
import xarray as xr
import pandas as pd
from eofs.xarray import Eof


data_path = './inputs/' # CONFIGURE



def compute_eofs(X, var, n_eofs):
    X_mean = X[var].mean(dim='time')
    X_std = X[var].std(dim='time')
    X_norm = (X[var] - X_mean) / X_std

    solver = Eof(X_norm)
    eofs = solver.eofsAsCorrelation(neofs=n_eofs)
    pcs = solver.pcs(npcs=n_eofs, pcscaling=1)
    
    pcs_df = pcs.to_dataframe().unstack('mode')
    pcs_df.columns = [f"{var}_{i}" for i in range(n_eofs)]
    
    return pcs_df, solver, X_mean, X_std





def get_Xtrain(datasets, n_eofs=5):
    
    if isinstance(datasets, str):
        datasets = [datasets]
        
    X = xr.concat([xr.open_dataset(data_path + f'inputs_{d}.nc') for d in datasets], dim='time')
    X = X.assign_coords(time=np.arange(len(X.time)))  # Reindex time

    variables = ['pr', 'rlds', 'rsds', 'sfcwind', 'tas', 'tasmax', 'tasmin']

    results = [compute_eofs(X, var, n_eofs) for var in variables]
    
    dfs, solvers, means, stds = zip(*results)
    
    inputs = pd.concat(dfs, axis=1)
    
    mean_dict = dict(zip(variables, means))
    std_dict = dict(zip(variables, stds))
    
    return inputs, solvers, mean_dict, std_dict




def project_eofs(X, var, solver, mean, std, n_eofs):
    X_norm = (X[var] - mean) / std
    
    pcs = solver.projectField(X_norm, neofs=n_eofs, eofscaling=1)
    pcs_df = pcs.to_dataframe().unstack('mode')
    pcs_df.columns = [f"{var}_{i}" for i in range(n_eofs)]
    
    return pcs_df





def get_Xtest(file, eof_solvers, mean_dict, std_dict, n_eofs=5):
    X = xr.open_dataset(data_path + f'inputs_{file}.nc')

    variables = ['pr', 'rlds', 'rsds', 'sfcwind', 'tas', 'tasmax', 'tasmin']

    dfs = [
        project_eofs(X, var, solver, mean_dict[var], std_dict[var], n_eofs)
        for var, solver in zip(variables, eof_solvers)
    ]

    return pd.concat(dfs, axis=1)




def get_Ytrain(datasets):

    if isinstance(datasets, str):
        datasets = [datasets]
        
    Y = xr.concat([xr.open_dataset(data_path + f'/lpjml_{d}_1850_2014.nc') if d == 'historical' else xr.open_dataset(data_path + f'/lpjml_{d}_2015_2100.nc') for d in datasets], dim='time')

    return Y


def get_Ytest(exp):
    if exp == 'historical':
        ds = xr.open_dataset(data_path + f'lpjml_{exp}_1850_2014.nc')
    else:
        ds = xr.open_dataset(data_path + f'lpjml_{exp}_2015_2100.nc')

    return ds




def get_rmse(truth, pred):
    weights = np.cos(np.deg2rad(truth.lat))
    return np.sqrt(((truth - pred)**2).weighted(weights).mean(['lat', 'lon'])).data