from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
import xarray as xr
from pandas.tseries.offsets import MonthEnd
from tqdm import tqdm

from tfv_get_tools.providers._downloader import BaseDownloader
from tfv_get_tools.providers._merger import BaseMerger
from tfv_get_tools.providers._utilities import todstr


class DownloadCAWCR(BaseDownloader):
    """CAWCR Wave downloader"""
    
    def _init_specific(self, **kwargs):
        """Set source and mode - matches original interface"""
        if self.model == 'default':
            self.log("Default model has been selected == 'glob_24m'")
            self.model = 'glob_24m'
        
        self.source = "CAWCR"
        self.mode = "WAVE"
        
        # Validate model selection
        MODELS = {"pac_4m", "pac_10m", "glob_24m", "aus_4m", "aus_10m"}
        if self.model not in MODELS:
            raise ValueError(f"Model must be one of {MODELS}")
        
        self._load_config()
        
        # CAWCR-specific: track whether we've checked for valid data
        self.checked_data = False
    
    def _get_output_filename(self, ts: pd.Timestamp, te: pd.Timestamp) -> Path:
        """CAWCR filename pattern includes model name"""
        return self.outdir / f"{self.prefix}_{self.model}_{todstr(ts)}_{todstr(te)}.nc"
    
    def _construct_opendap_url(self, date: pd.Timestamp) -> str:
        """Construct the OPeNDAP URL for the given date"""
        date_str = date.strftime("%Y%m")
        url = f"{self.base_url}/ww3.{self.model}.{date_str}.nc"
        return url
    
    def _check_data_validity(self, ds: xr.Dataset) -> None:
        """Check if the dataset contains valid data (CAWCR-specific)"""
        if not self.checked_data:
            # Check first variable for valid data
            v = next(iter(self.variables))
            nonnan = np.nansum(ds[v][0].values)
            if nonnan == 0.0:
                raise ValueError(
                    "No valid data detected in netcdf - please check requested extents against the data source"
                )
            else:
                self.checked_data = True
    
    def _download_single_file(self, fname: Path, url: str) -> bool:
        """Download single file from CAWCR OPeNDAP server"""
        try:
            ds = xr.open_dataset(url)

            # Handle longitude selection (CAWCR-specific logic)
            if self.xlims[0] < self.xlims[1]:
                lon_idx = np.hstack(
                    np.where(
                        (self.xlims[0] <= ds["longitude"])
                        & (ds["longitude"] <= self.xlims[1])
                    )
                )
            else:
                lon_idx = np.hstack(
                    (
                        np.where(ds["longitude"] <= self.xlims[1])[0],
                        np.where(ds["longitude"] >= self.xlims[0])[0],
                    )
                )
            
            if lon_idx.size <= 1:
                raise ValueError("No longitude points selected! You may need to increase your grid extents")

            # Select latitude indices
            lat_idx = np.hstack(
                np.where(
                    (self.ylims[0] <= ds["latitude"]) & (ds["latitude"] <= self.ylims[1])
                )
            )
            
            if lat_idx.size <= 1:
                raise ValueError("No latitude points selected! You may need to increase your grid extents")

            # Subset dataset by latitude and longitude
            ds = ds.isel(longitude=lon_idx, latitude=lat_idx)

            # Subset dataset to requested variables
            ds = ds[self.variables]

            # CAWCR-specific: Check for valid data on first download
            self._check_data_validity(ds)

            # Save to file
            ds.to_netcdf(fname)
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Failed to download {url}: {e}")
            return False
    
    def download(self):
        """CAWCR-specific download loop - yields tasks for new base class"""
        for ts in self.times:
            te = ts + MonthEnd() + pd.Timedelta("23.9h")
            
            output_file = self._get_output_filename(ts, te)
            url = self._construct_opendap_url(ts)
            
            yield {
                'file_path': output_file,
                'url': url,
                'timestamp': ts,
                'variable': f"{len(self.variables)}_vars",
                'download_func': lambda f=output_file, u=url: self._download_single_file(f, u)
            }

class MergeCAWCR(BaseMerger):
    def _init_specific(self) -> None:
        self.source = "CAWCR"
        self.mode = "WAVE"
        
        if self.model == 'default':
            self.model = 'glob_24m'
        
        self._load_config()

    def merge_files(self, file_list: List[Path]) -> Tuple[xr.Dataset, List[Path]]:
        """Merge CAWCR wave files using time concatenation."""
        if not file_list:
            raise ValueError("No files provided for merging")
            
        datasets = []
        skipped_files = []
        
        for file_path in tqdm(file_list, disable=not self.verbose):
            ds = self._open_subset_netcdf(file_path)
            if ds is not None:
                datasets.append(ds)
            else:
                skipped_files.append(file_path)
                
        if not datasets:
            raise ValueError("No valid datasets could be loaded")
            
        # Concatenate and clean up
        merged = xr.concat(datasets, dim="time", combine_attrs="override", 
                          data_vars="minimal", coords="minimal", compat="override")
        
        # Remove duplicates and sort
        merged = merged.sortby("time")
        _, unique_idx = np.unique(merged["time"], return_index=True)
        merged = merged.isel(time=np.sort(unique_idx))
        
        return merged, skipped_files
        