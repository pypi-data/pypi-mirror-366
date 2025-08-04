"""
CFSR/CFSv2
"""

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
import xarray as xr
from pandas.tseries.offsets import MonthEnd
from tqdm import tqdm

from tfv_get_tools.providers._downloader import BaseDownloader
from tfv_get_tools.providers._merger import BaseMerger
from tfv_get_tools.providers._utilities import todstr


class DownloadCFSRAtmos(BaseDownloader):
    """CFSR downloader - only the source-specific parts"""
    
    def _init_specific(self, **kwargs):
        """Set source and mode - that's it"""
        self.source = "CFSR"
        self.mode = "ATMOS"
        self._load_config()
    
    def _get_output_filename(self, ts: pd.Timestamp, te: pd.Timestamp, var: str) -> Path:
        """CFSR-specific filename pattern"""
        return self.outdir / f"{self.prefix}_{var}_{todstr(ts)}_{todstr(te)}.nc"
    
    def _construct_opendap_url(self, date: pd.Timestamp, var: str) -> str:
        """CFSR-specific URL construction"""
        dataset_dates = list(self.dsmap.keys())
        idx = np.where([date.date() >= x for x in dataset_dates])[0][-1]
        dataset_time = dataset_dates[idx]
        
        ds_entry = list(self.dsmap[dataset_time].keys())[0]
        dataset_id, sys = ds_entry.split("-")

        datestr = date.strftime("%Y%m")
        year = date.year

        fname = f"{var}.{sys}.{datestr}.grb2"
        url = f"{self.base_url}/{dataset_id}/{year}/{fname}"
        return url
    
    def _download_single_file(self, fname: Path, url: str) -> bool:
        """CFSR-specific download and processing"""
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
    
    def download(self):
        """CFSR-specific download loop - only the parts that differ from base"""
        # The base class handles result tracking, progress, etc.
        # We just need to yield the download tasks
        
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

class MergeCFSRAtmos(BaseMerger):
    def _init_specific(self) -> None:
        self.source = "CFSR"
        self.mode = "ATMOS"
        self._load_config()

    def _extract_target_coordinates(self, datasets: List[xr.Dataset]) -> Tuple[np.ndarray, np.ndarray]:
        """Extract appropriate wind coordinates, preferring CFSv2 over CFSR."""
        cfsv2_coords = None
        cfsr_coords = None
        
        for ds in datasets:
            if ds is None or 'u-component_of_wind_height_above_ground' not in ds:
                continue
                
            time_values = pd.to_datetime(ds['time'].values)
            first_time = time_values[0] if len(time_values) > 0 else pd.Timestamp.min
            
            if first_time >= pd.Timestamp(2011, 1, 1):
                cfsv2_coords = (ds['lon'].values, ds['lat'].values)
            else:
                cfsr_coords = (ds['lon'].values, ds['lat'].values)
        
        # Prefer CFSv2, fallback to CFSR, then any available
        return cfsv2_coords or cfsr_coords or (datasets[0]['lon'].values, datasets[0]['lat'].values)

    def _process_file(self, file_path: Path) -> Optional[xr.Dataset]:
        """Load file and filter 30-minute data."""
        ds = self._open_subset_netcdf(file_path, chunks=dict(time=24))
        if ds is not None:
            # Filter out 30-minute data points
            time_values = pd.to_datetime(ds['time'].values)
            valid_indices = [i for i, t in enumerate(time_values) if t.minute != 30]
            ds = ds.isel(time=valid_indices)
        return ds

    def merge_files(self, file_list: List[Path]) -> Tuple[xr.Dataset, List[Path]]:
        """Merge CFSR files: group by startdate, merge variables, then concat time."""
        if not file_list:
            raise ValueError("No files provided for merging")
            
        # Group files by start date
        startdates = [f.stem.split('_')[-2] for f in file_list]
        grouped_files = {date: [] for date in np.unique(startdates)}
        
        # Load files and group them
        all_datasets = []
        skipped_files = []
        
        for i, file_path in enumerate(tqdm(file_list, disable=not self.verbose)):
            ds = self._process_file(file_path)
            if ds is not None:
                grouped_files[startdates[i]].append(ds)
                all_datasets.append(ds)
            else:
                skipped_files.append(file_path)
        
        if not all_datasets:
            raise ValueError("No valid datasets could be loaded")
        
        # Extract target coordinates for interpolation
        target_lon, target_lat = self._extract_target_coordinates(all_datasets)
        
        if self.verbose:
            print("Concatenating and interpolating xarray dataset")
        
        # Merge variables for each start date group
        merged_by_date = []
        for date_group in grouped_files.values():
            if date_group:
                # Interpolate all datasets to common grid
                interpolated = [
                    ds.interp(lon=target_lon, lat=target_lat, method='linear', 
                             kwargs=dict(fill_value='extrapolate'))
                    for ds in date_group
                ]
                merged_by_date.append(xr.merge(interpolated, compat='override'))
        
        # Concatenate along time dimension
        merged = xr.concat(merged_by_date, dim="time", combine_attrs="override",
                          data_vars="minimal", coords="minimal", compat="override")
        
        # Final cleanup
        merged = merged.mean(dim='height_above_ground', skipna=True)
        merged = merged.drop_vars(['reftime', 'time_bounds', 'GaussLatLon_Projection', 
                                  'LatLon_Projection', 'height_above_ground'], errors='ignore')
        
        # Sort and remove duplicates
        merged = merged.sortby('time')
        _, unique_idx = np.unique(merged['time'], return_index=True)
        merged = merged.isel(time=unique_idx)
        
        # Fill gaps and standardise coordinates
        merged = merged.bfill('time', limit=3).ffill('time', limit=3)
        merged = merged.rename({'lon': 'longitude', 'lat': 'latitude'})
        
        return merged, skipped_files