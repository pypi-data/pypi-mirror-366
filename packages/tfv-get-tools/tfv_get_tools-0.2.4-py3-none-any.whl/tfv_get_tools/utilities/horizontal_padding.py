"""
Set of functions to managing horizontally padding an OCEAN dataset

This will cast the nearest value horizontally (lat/lon) for each depth level, through all times

"""
import xarray as xr
import numpy as np
from scipy import spatial

def horizontal_pad(ds):
    """Pad an ocean dataset horizontally for each time.

    Args:
        ds (xr.Dataset): input merged ocean dataset

    Returns:
        xr.Dataset: resulting padded ocean dataset
    """
    for var in ds.data_vars:
        if set(ds[var].dims) >= {'latitude', 'longitude', 'time'}:
            # Compute nearest indices for each depth level
            nearest_indices = xr.apply_ufunc(
                _compute_nearest_indices,
                ds[var].isel(time=0),
                input_core_dims=[['latitude', 'longitude']],
                output_core_dims=[['latitude', 'longitude']],
                vectorize=True
            )
            
            # Apply filling to all time steps for each depth
            filled_var = xr.apply_ufunc(
                _fill_nans_with_precomputed_indices,
                ds[var],
                nearest_indices,
                input_core_dims=[['latitude', 'longitude'], ['latitude', 'longitude']],
                output_core_dims=[['latitude', 'longitude']],
                vectorize=True
            )
            
            ds[var] = filled_var

    return ds

def _compute_nearest_indices(values: np.ndarray) -> np.ndarray:
    """Find the indices of the nearest non nan values across longitude/latitude

    Args:
        values (np.ndarray): variable values

    Returns:
        np.ndarray: indices array
    """
    ny, nx = values.shape
    lat = np.arange(ny)
    lon = np.arange(nx)
    lat, lon = np.meshgrid(lat, lon, indexing='ij')
    
    valid_mask = ~np.isnan(values)
    valid_points = np.column_stack((lat[valid_mask], lon[valid_mask]))
    
    # Create KDTree for efficient nearest neighbor search
    tree = spatial.cKDTree(valid_points)
    
    # Find nearest non-NaN point for each point
    all_points = np.column_stack((lat.ravel(), lon.ravel()))
    _, indices = tree.query(all_points)
    
    # Reshape indices to match the original shape
    return indices.reshape(values.shape)

def _fill_nans_with_precomputed_indices(values: np.ndarray, nearest_indices: np.ndarray) -> np.ndarray:
    """Fill nan values in dataset wih the pre-calced indicies.

    Args:
        values (np.ndarray): variable values
        nearest_indices (np.ndarray): indicies if nearest non-nan value across longitude/latitude

    Returns:
        np.ndarray: filled variable values
    """
    valid_values = values[~np.isnan(values)]
    
    # Apply the precomputed indices to fill NaN values
    filled_values = values.copy()
    nan_mask = np.isnan(filled_values)
    filled_values[nan_mask] = valid_values[nearest_indices[nan_mask]]
    
    return filled_values