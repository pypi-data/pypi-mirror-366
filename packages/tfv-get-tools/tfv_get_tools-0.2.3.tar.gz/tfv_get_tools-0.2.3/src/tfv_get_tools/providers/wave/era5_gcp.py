"""
AEW - This is an alternative source ERA5 that we used for awhile while CDSAPI wasn't playing ball.
It's marginally faster, requires no registration, but runs several months behind CDSAPI which
got called out a few times, so we should stick with CDSAPI. Also generally believe it's good form to
have users go through CDSAPI as it is their data. 
"""

from pathlib import Path

import numpy as np
import xarray as xr
import pandas as pd
from tqdm import tqdm

from pandas.tseries.offsets import MonthEnd

from tfv_get_tools.providers._utilities import todstr
from tfv_get_tools.providers._downloader import BaseDownloader
from tfv_get_tools.providers._merger import BaseMerger


class DownloadERA5WaveGCP(BaseDownloader):
    """Updated version that makes use of the public GCP Zarr ERA5 release"""

    def _init_specific(self, **kwargs):
        """Set source and mode - matches original interface"""
        self.source = "ERA5_GCP"
        self.mode = "WAVE"
        self._load_config()
        
        # Initialize the Zarr dataset connection
        self.era5_ds = None
        self.last_valid = None
    
    def _initialize_zarr_connection(self):
        """Initialize connection to ERA5 Zarr dataset"""
        if self.era5_ds is None:
            if self.verbose:
                print('Opening connection to ERA5 data - please wait')
            
            self.era5_ds = xr.open_zarr(
                self.base_url,
                chunks=dict(time=744),  # 31 day chunk
                storage_options=dict(token='anon'),
            )

            self.last_valid = pd.Timestamp(self.era5_ds.attrs['valid_time_stop']).floor('1d')

            self.era5_ds = self.era5_ds.sel(time=slice(
                pd.Timestamp(1940, 1, 1), self.last_valid
            ))
    
    def _get_output_filename(self, ts: pd.Timestamp, te: pd.Timestamp) -> Path:
        """ERA5 GCP filename pattern (no variable in filename - downloads all together)"""
        fname = f"{self.prefix}_{todstr(ts)}_{todstr(te)}.nc"
        return self.outdir / fname
    
    def _download_single_time_period(self, ts: pd.Timestamp, te: pd.Timestamp, output_file: Path) -> bool:
        """Download single time period from Zarr dataset"""
        try:
            # Check if we're past the valid time range
            if ts > self.last_valid:
                if self.verbose:
                    print(f'The final valid ERA5 time on this database is {self.last_valid.strftime("%Y-%m-%d")}.')
                    print('Skipping this time period')
                return False
            
            # Apply slices and variable filters
            dsx = self.era5_ds.sel(
                time=slice(ts, te),
                latitude=slice(*self.ylims[::-1]), 
                longitude=slice(*self.xlims),
            )[self.variables]
            
            if self.verbose:
                print(f"... Downloading {output_file.name}")
            
            # Wrap the cut-down piece back to -180 to 180
            dsx = dsx.assign_coords({'longitude': (dsx['longitude'] + 180) % 360 - 180})
            dsx = dsx.sortby('longitude')

            dsx.to_netcdf(output_file)
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Failed to download {output_file.name}: {e}")
            return False
    
    def download(self):
        """ERA5 GCP-specific download loop - yields tasks for new base class"""
        # Initialize the Zarr connection once
        self._initialize_zarr_connection()
        
        if self.verbose:
            print('Starting downloading loop')
        
        for ts in self.times:
            te = ts + MonthEnd() + pd.Timedelta("23.9h")
            
            # Check if we're past the valid time range
            if ts > self.last_valid:
                if self.verbose:
                    print(f'The final valid ERA5 time on this database is {self.last_valid.strftime("%Y-%m-%d")}.')
                    print('Exiting download loop early')
                break
            
            output_file = self._get_output_filename(ts, te)
            
            yield {
                'file_path': output_file,
                'url': f'zarr://{self.base_url}',  # Pseudo-URL for logging
                'timestamp': ts,
                'variable': 'all_variables',  # ERA5 downloads all vars together
                'download_func': lambda start=ts, end=te, out=output_file: 
                    self._download_single_time_period(start, end, out)
            }

class MergeERA5WaveGCP(BaseMerger):
    def _init_specific(self):
        self.source = "ERA5"
        self.mode = "WAVE"
        self._load_config()

    def merge_files(self, file_list):
        """
        ERA5 merging logic.

        ERA5 names the time variable "valid_time" which we rename after opening.

        Args:
            file_list (list): list of path objects to open and concat.

        Returns:
            xr.Dataset: merged xarray dataset
            list: files unable to be merged
        """
        dsset = []
        skipped_list = []
        for f in tqdm(file_list):
            dsx = self._open_subset_netcdf(f, time=("time", "valid_time"))
            if dsx is not None:
                if "valid_time" in dsx:
                    dsx = dsx.rename(valid_time="time")
                if "expver" in dsx.dims:
                    dsx = dsx.mean(dim="expver", keep_attrs=True)
                dsx = dsx.drop("expver", errors='ignore')
                dsset.append(dsx)
            else:
                skipped_list.append(f)

        print("Concatenating xarray dataset")
        ds = xr.concat(
            dsset,
            dim="time",
            combine_attrs="override",
            data_vars="minimal",
            coords="minimal",
            compat="override",
        )

        # Sort by time and drop duplicates (from overlaps)
        ds = ds.sortby("time")
        _, idx = np.unique(ds["time"], return_index=True)
        ds = ds.isel(time=idx)

        ds = ds.sortby("latitude")  # Latitudes should go south to north

        return ds, skipped_list
