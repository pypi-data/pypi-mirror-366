import xarray as xr
import numpy as np
from xarray import DataArray
import dask.array as da

def freq_to_period(freq: xr.DataArray) -> xr.DataArray:
    """Inverse frequency to get period (s)"""    
    return 1/freq

def dewpt_to_relhum(dew_temp: DataArray, sfc_temp: DataArray) -> DataArray:
    """Calculate relative humidity using dew_temp and sfc_temp
    RH (%) = (e/esat)*100
    a1=611.21 ; a3=17.502 ; a4=32.19 ; T0=273.16
    https://confluence.ecmwf.int/pages/viewpage.action?pageId=171411214

    Args:
        dew_temp (np.ndarray): dew point temperature in Kelvin
        sfc_temp (np.ndarray): surface temperature in Kelvin

    Returns:
        np.ndarray: Relative humidity (%)
    """

    a1=611.21
    a3=17.502
    a4=32.19
    T0=273.16
    
    esat = a1*np.exp(a3*((sfc_temp-T0)/(sfc_temp-a4)))
    e = a1*np.exp(a3*((dew_temp-T0)/(dew_temp-a4)))
    
    rel_hum = (e/esat)*100
    
    return rel_hum
