"""
Module to handle land masking of an atmospheric dataset.
This has been straight air-lifted from GetAtmos with no modifications.
"""

import lzma
import pickle
import importlib.resources

import xarray as xr
import numpy as np
import dask.array as da
import pandas as pd
import logging
from scipy.ndimage import distance_transform_edt

from tqdm.auto import trange


def load_atmos_masks():
   """Returns a dictionary containing landmasks for ERA5, CFSR, CFSv2 and BARRA_R.

   Returns:
       lm (dict): Dict containing keys 'cfsr', 'cfsv2', 'barra_r', 'era5'.
           Each of these contains a sub-dict that has 'x', 'y' and 'lm' keys.
   """
   with importlib.resources.files(__name__).parent.joinpath("providers/atmos/data/atmos_masks.xz").open("rb") as stream:
       with lzma.open(stream, "rb") as f:
           lmdict = pickle.load(f)
   
   return lmdict


def mask_land_data(ds, source):
    lms = load_atmos_masks()

    # Load all land masks (TODO: BETTER HANDLING OF CFSR and CFSv2 SWITCH)
    if "cfs" in source:
        if ds["time"][-1] > pd.Timestamp(2011, 1, 1):
            k = "cfsv2"
        else:
            k = "cfsr"
    else:
        k = source.lower()
    lm = lms[k]

    dsm = xr.DataArray(
        np.squeeze(lm["lm"]), coords=dict(latitude=lm["y"], longitude=lm["x"])
    )

    ds["lsm"] = dsm.reindex(
        longitude=ds["longitude"], latitude=ds["latitude"], method="nearest"
    )
    ds["lsm"].attrs = {"units": "-", "long_name": f"{k} land mask index"}
      
    # If the Atmos dataset is in negative longitudes, we need to wrap the land mask around 180
    # (i.e., -180 to 180), not (0 to 360)
    if ds["longitude"].min() < 0.0:
        lon = dsm['longitude'].values
        lon[lon > 180] = (lon - 360)[lon > 180]
        dsm['longitude'] = lon    
        dsm = dsm.sortby('longitude')
    
    mask = (ds["lsm"] > 0.2).values
    mask_3d = repeat_2d_array(mask, ds.sizes["time"])

    for var in ds.data_vars.keys():
        dims = ds[var].dims
        if ('longitude' in dims) & ('latitude' in dims) & ('time' in dims):
            logging.debug(f"{var} in ds, running land mask")
            ds[var].data = fill(ds[var].values, mask_3d)

    return ds


def fill(data, mask):
    """Replace "masked" data with the nearest valid data cell

    Args:
        data (da.ndarray): 2D input data array
        invalid (da.ndarray): 2D boolean array, where True cells are replaced by the nearest data.

    Returns:
        filled_data: 2D output array with filled data
    """

    ind = distance_transform_edt(mask, return_distances=False, return_indices=True)
    return data[tuple(ind)]


def repeat_2d_array(array, n):
    repeated_array = da.tile(array, (n, 1, 1))
    return repeated_array
