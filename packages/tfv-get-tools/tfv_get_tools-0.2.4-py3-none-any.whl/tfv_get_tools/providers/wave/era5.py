"""
ERA5 Wave downloader
"""

import shutil
import zipfile
from pathlib import Path
from typing import List, Tuple

import cdsapi
import numpy as np
import pandas as pd
import xarray as xr
from pandas.tseries.offsets import MonthEnd
from tqdm import tqdm

from tfv_get_tools.providers._downloader import BaseDownloader
from tfv_get_tools.providers._merger import BaseMerger
from tfv_get_tools.providers._utilities import todstr

class DownloadERA5Wave(BaseDownloader):
    """ERA5 Wave downloader via CDS API"""
    
    def _init_specific(self, **kwargs):
        """Set source and mode - matches original interface"""
        self.source = "ERA5"
        self.mode = "WAVE"
        self._load_config()
    
    def _get_output_filename(self, ts: pd.Timestamp, te: pd.Timestamp) -> Path:
        """ERA5 Wave filename pattern (no variable in filename)"""
        fname = f"{self.prefix}_{todstr(ts)}_{todstr(te)}.nc"
        return self.outdir / fname
    
    def _construct_cds_request(self, date: pd.Timestamp) -> dict:
        """Construct CDS API request parameters"""
        limstr = self._to_limstr(self.xlims, self.ylims)
        
        year = date.year
        month = date.month
        times = [f"{x:02}:00" for x in range(0, 24, 1)]  # Hourly
        days = [str(x) for x in range(1, 32)]
        
        return {
            "product_type": "reanalysis",
            "variable": self.variables,
            "year": [year],
            "month": [month],
            "day": days,
            "time": times,
            "area": limstr,
            "data_format": "netcdf",
            "download_format": "unarchived",
        }
    
    @staticmethod
    def _to_limstr(x, y):
        """Convert coordinate bounds to ERA5 area string format"""
        return f"{y[1]}/{x[0]}/{y[0]}/{x[1]}"
    
    def _download_single_file(self, temp_file: Path, final_file: Path, cds_request: dict) -> bool:
        """Download single file via CDS API"""
        try:
            c = cdsapi.Client()
            
            # Download to temporary file first
            c.retrieve("reanalysis-era5-single-levels", cds_request, temp_file)
            
            if temp_file.exists():
                # ERA5 sometimes returns zip files, handle both cases
                self._convert_split_netcdf_data(temp_file, final_file)
                return True
            else:
                return False
                    
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for specific error types and provide helpful messages
            if "missing/incomplete configuration file" in error_msg or ".cdsapirc" in error_msg:
                print("\n" + "="*60)
                print("CDS API CONFIGURATION ERROR")
                print("="*60)
                print("The CDS API configuration file is missing or incomplete.")
                print("To fix this issue:")
                print("1. Register at https://cds.climate.copernicus.eu/")
                print("2. Go to your profile page and copy your API key")
                print("3. Create a file called '.cdsapirc' in your home directory with:")
                print("   url: https://cds.climate.copernicus.eu/api")
                print("   key: YOUR_API_KEY_HERE")
                print("="*60)
                
            elif "authentication" in error_msg or "invalid key" in error_msg:
                print("\n" + "="*60)
                print("CDS API AUTHENTICATION ERROR")
                print("="*60)
                print("Your CDS API key appears to be invalid.")
                print("Please check your .cdsapirc file and ensure your API key is correct.")
                print("You can find your key at: https://cds.climate.copernicus.eu/user/")
                print("="*60)
                
            elif "cds-beta.climate.copernicus.eu" in error_msg:
                print("\n" + "="*60)
                print("CDS API AUTHENTICATION ERROR")
                print("="*60)
                print("Your CDS API key appears to be invalid.")
                print("This is likely due to an update by the Copernicus Climate Data Store.")
                print("Please check your .cdsapirc file and ensure your API key is correct.")
                print("You can find your key at: https://cds.climate.copernicus.eu/user/")
                print("="*60)

            else:
                print(f"Failed to download via CDS API: {e}")

                    
            return False
    
    @staticmethod
    def _convert_split_netcdf_data(file_handle_temp: Path, file_handle: Path) -> bool:
        """
        Handle ERA5 zip files or direct NetCDF files
        """
        file_path = Path(file_handle_temp)
        file_path_out = Path(file_handle)
        
        # Check if file is a zip file
        if zipfile.is_zipfile(file_path):
            datasets = []
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # Extract all files to a temporary directory
                temp_dir = file_path.parent / 'temp_netcdf'
                temp_dir.mkdir(exist_ok=True)
                zip_ref.extractall(temp_dir)
                
                # Load all NetCDF files
                for extracted_file in temp_dir.glob('*.nc'):
                    with xr.open_dataset(extracted_file) as dsx:
                        dsx.load()
                    datasets.append(dsx)
                
                # Clean up extracted files
                for file in temp_dir.iterdir():
                    file.unlink()
                temp_dir.rmdir()
            
            if not datasets:
                raise ValueError("No NetCDF files found in zip archive")
            
            # Combine all datasets
            ds = xr.merge(datasets, compat='override')
            ds.to_netcdf(file_path_out)
            
            # Delete the zip file
            file_path.unlink()
            
        else:
            # Move the NetCDF file to the output path
            shutil.move(file_path, file_path_out)
        
        return True
    
    def download(self):
        """ERA5 Wave-specific download loop - yields tasks for new base class"""
        for ts in self.times:
            te = ts + MonthEnd() + pd.Timedelta("23.9h")
            
            final_file = self._get_output_filename(ts, te)
            temp_file = self.outdir / '_temp_era5_file'
            cds_request = self._construct_cds_request(ts)
            
            yield {
                'file_path': final_file,
                'url': 'CDS_API',  # Not a URL but API call
                'timestamp': ts,
                'variable': 'all_variables',  # ERA5 downloads all vars together
                'download_func': lambda tf=temp_file, ff=final_file, req=cds_request: 
                    self._download_single_file(tf, ff, req)
            }


class MergeERA5Wave(BaseMerger):
    def _init_specific(self) -> None:
        self.source = "ERA5"
        self.mode = "WAVE"
        self._load_config()

    def _process_era5_dataset(self, ds: xr.Dataset) -> xr.Dataset:
        """Apply ERA5-specific coordinate and dimension processing."""
        # Rename time coordinate
        if "valid_time" in ds.coords:
            ds = ds.rename({"valid_time": "time"})
            
        # Handle experiment version dimension  
        if "expver" in ds.dims:
            ds = ds.mean(dim="expver", keep_attrs=True)
        ds = ds.drop_vars("expver", errors='ignore')
        
        # Standardise coordinate names
        coord_mappings = {'lon': 'longitude', 'lng': 'longitude', 'lat': 'latitude'}
        rename_dict = {old: new for old, new in coord_mappings.items() if old in ds.coords}
        if rename_dict:
            ds = ds.rename(rename_dict)
            
        return ds

    def merge_files(self, file_list: List[Path]) -> Tuple[xr.Dataset, List[Path]]:
        """Merge ERA5 wave files with time concatenation."""
        if not file_list:
            raise ValueError("No files provided for merging")
            
        datasets = []
        skipped_files = []
        
        for file_path in tqdm(file_list, disable=not self.verbose):
            ds = self._open_subset_netcdf(file_path, time=("time", "valid_time"))
            if ds is not None:
                ds = self._process_era5_dataset(ds)
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
        
        # Sort latitudes south to north
        if 'latitude' in merged.coords:
            merged = merged.sortby("latitude")
            
        return merged, skipped_files
