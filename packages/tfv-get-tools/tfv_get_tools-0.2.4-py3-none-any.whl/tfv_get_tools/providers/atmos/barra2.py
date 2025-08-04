from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from pandas.tseries.offsets import MonthEnd
from tqdm import tqdm

from tfv_get_tools.providers._downloader import BaseDownloader
from tfv_get_tools.providers._merger import BaseMerger
from tfv_get_tools.providers._utilities import todstr


class DownloadBARRA2(BaseDownloader):
    """BARRA2 Downloader
    
    This is a THREDDS Dataset with each variable saved under a sub-url.
    Compared to BARRA1, the new BARRA2 appears to be more self-consistent so we'll use a 
    standard THREDDS server downloader (like CAWCR)    
    
    """
    def _init_specific(self):
        if self.model == 'default':
            self.log("Default model has been selected == 'R2'")
            self.model = 'r2'
        
        self.source = "BARRA2"
        self.mode = "ATMOS"
        
        MODELS = {"c2", "r2", "re2"}
        if self.model.lower() not in MODELS:
            raise ValueError(f"Model must be one of {MODELS}")
        
        self._load_config()

    def _get_output_filename(self, ts: pd.Timestamp, te: pd.Timestamp, var: str) -> Path:
        """BARAR2 filename pattern"""
        fname = f"{self.prefix}_{self.model}_{var}_{todstr(ts)}_{todstr(te)}.nc"
        return self.outdir / fname

        
    def download(self):
        """Begin download of files.

        Approach:
            - Loop through each time in times vector
            - Try again if failures.
        """
        for ts in self.times:
            te = ts + MonthEnd() + pd.Timedelta("23.9h")
            
            for var in self.variables:
                out_file = self._get_output_filename(ts, te, var)
                url = self._construct_opendap_url(ts, var)
                
                # Let base class handle the file existence check, timing, etc.
                yield {
                    'file_path': out_file,
                    'url': url,
                    'timestamp': ts,
                    'variable': var,
                    'download_func': lambda f=out_file, u=url: self._download_single_file(f, u)
                }

    def _construct_opendap_url(self, date: pd.Timestamp, var: str) -> str:
        """
        Construct the OPeNDAP URL for the given date for BARRA2

        Args:
            date (pd.Timestamp): The date for which to construct the URL.
            var (str): Variable name to download (BARRA2 var)

        Returns:
            str: The constructed URL.
        """
        date_str = date.strftime("%Y%m")
        
        # Crap way of getting the dset template name from nexted dict.
        name_tmp = list(self.dsmap[list(self.dsmap.keys())[0]].keys())[0]      
        
        # Apply replacements
        name = name_tmp.replace('<VAR>', var).replace('<DATE>', date_str)
        
        url = f"{self.base_url}/{var}/latest/{name}"
        
        return url
    

    def _download_single_file(self, fname: Path, url: str) -> bool:
        """
        Download a single file from the specified URL and save it to the specified filename.

        Args:
            fname (Path): The output filename.
            url (str): The URL to download the data from.

        Returns:
            bool: True if the download was successful, False otherwise.
        """
        try:
            ds = xr.open_dataset(url)

            # Handle longitude selection (CFSR-specific logic)
            if self.xlims[0] < self.xlims[1]:
                lon_idx = np.hstack(
                    np.where(
                        (self.xlims[0] <= ds["lon"])
                        & (ds["lon"] <= self.xlims[1])
                    )
                )
            else:
                lon_idx = np.hstack(
                    (
                        np.where(ds["lon"] <= self.xlims[1])[0],
                        np.where(ds["lon"] >= self.xlims[0])[0],
                    )
                )
            
            assert lon_idx.size > 1, "No longitude points selected!"

            # Select latitude indices
            lat_idx = np.hstack(
                np.where(
                    (self.ylims[0] <= ds["lat"]) 
                    & (ds["lat"] <= self.ylims[1])
                )
            )
            assert lat_idx.size > 1, "No latitude points selected!"

            # Subset and save
            ds = ds.isel(lon=lon_idx, lat=lat_idx)
            ds.to_netcdf(fname)
            return True

        except Exception as e:
            if self.verbose:
                print(f"Failed to download {url}: {e}")
            return False

class MergeBARRA2(BaseMerger):
    def _init_specific(self):
        self.source = "BARRA2"
        self.mode = "ATMOS"
        
        if self.model == 'default':
            self.model = 'R2'
        
        self._load_config()

    
    def merge_files(self, file_list):
        """Specific merging logic
        
        # BARRA2 requires us to first merge on varabies before concatenating over time.
        
        Args:
            file_list (list): list of path objects to open and concat.

        Returns:
            xr.Dataset: merged xarray dataset
            list: files unable to be merged 
        """
        skipped_list = []
        
        startdates = [x.stem.split('_')[-2] for x in file_list]
        unq_startdates = np.unique(startdates)
        
        dsset = {k: [] for k in unq_startdates}
        
        for i, f in enumerate(tqdm(file_list)):
            dsx = self._open_subset_netcdf(f, chunks=dict(time=24))
            if dsx is not None:
                dsx['time'] = pd.to_datetime(dsx['time'].values).floor('1h')
                
                # Drop all the extra variables
                dsx = dsx.drop_vars(['height', 'level_height', 'model_level_number', 'sigma', 'crs'], errors='ignore')

                dsset[startdates[i]].append(dsx)
            else:
                skipped_list.append(f)
                
        print("Concatenating xarray dataset")
        
        # Merge the common start_dates first, then concatenate by time afterwards
        dssetm = []
        for v in dsset.values():
            dssetm.append(xr.merge(v))
        
        ds = xr.concat(
            dssetm,
            dim="time",
            combine_attrs="override",
            data_vars="minimal",
            coords="minimal",
            compat="override",
        )
        
        # Drop the redundant time_bnds var
        ds = ds.drop_vars(['time_bnds', 'bnds'], errors='ignore')

        # Sort and drop nans
        ds = ds.sortby('time')
        _, idx = np.unique(ds['time'], return_index=True)
        ds = ds.isel(time=idx)
        
        # Rename the original coords
        ds = ds.rename({'lon': 'longitude', 'lat': 'latitude'})
        
        return ds, skipped_list
