from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import xarray as xr
from tqdm.auto import tqdm

from tfv_get_tools.providers._downloader import BaseDownloader
from tfv_get_tools.providers._merger import BaseMerger


class DownloadHycom(BaseDownloader):
    """Downloader class for HYCOM oceanographic data.
    
    Handles both single-database (pre-2024-08) and multi-database (post-2024-08) formats.
    """
    
    def _init_specific(self, **kwargs):
        """Initialize HYCOM specific attributes"""
        self.source = "HYCOM"
        self.mode = "OCEAN"
        self._load_config()
        
        # Dictionary to cache database coordinate information
        self.db_cache = {}
        # Track which variables are 2D (no depth dimension)
        self.two_dimensional_vars = ["surf_el"]
        
        # Convert time_interval to string if "best" is specified in model field
        if self.model and self.model.lower() == "best":
            self.time_interval = "best"
            # Reset model to default to avoid confusion in filename
            self.model = "default"
            if self.verbose:
                print("Using 'best' time interval: downloading all available timesteps")
    
    def _get_output_filename(self, date: datetime, db_name: str = None) -> Path:
        """Generate output filename based on date, time interval, and database name"""
        date_str = date.strftime('%Y%m%d')
        
        # Format time interval part of filename
        if self.time_interval == "best":
            interval_str = "best"
        else:
            interval_str = f"{self.time_interval:02d}h"
            
        # Construct filename
        if db_name:
            fname = f"{self.prefix}_{date_str}_{interval_str}_{db_name}.nc"
        else:
            fname = f"{self.prefix}_{date_str}_{interval_str}.nc"
            
        return self.outdir / fname
    
    def _get_database(self, date: datetime) -> Union[str, Dict[str, List[str]], None]:
        """Get database URL or mapping for a date"""
        if not isinstance(date, datetime):
            raise ValueError("Input must be a datetime object")

        # Sort the dates in ascending order
        sorted_dates = sorted(
            self.dsmap.keys(), key=lambda x: datetime.strptime(x, "%Y-%m-%d")
        )

        for i, start_date_str in enumerate(sorted_dates):
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

            # If it's the last item, or if the date is within this range
            if i == len(sorted_dates) - 1 or date < datetime.strptime(
                sorted_dates[i + 1], "%Y-%m-%d"
            ):
                if date >= start_date:
                    database_info = self.dsmap[start_date_str]
                    
                    # Check if this is a dictionary with multiple databases (new format)
                    if isinstance(database_info, dict) and not isinstance(next(iter(database_info.values())), str):
                        # New format: mapping of database URLs to variable lists
                        result = {}
                        for db_url, var_list in database_info.items():
                            # Check if we need to filter variables based on user request
                            if self._custom_variables:
                                # Only include databases that have variables we need
                                filtered_vars = [v for v in var_list if v in self.variables]
                                if filtered_vars:
                                    formatted_url = db_url.format(year=date.year) if "{year}" in db_url else db_url
                                    result[formatted_url] = filtered_vars
                            else:
                                # Include all databases and their variables
                                formatted_url = db_url.format(year=date.year) if "{year}" in db_url else db_url
                                result[formatted_url] = var_list
                        return result
                    else:
                        # Original format: single database URL
                        database_url = next(iter(database_info.keys()))
                        if "{year}" in database_url:
                            return database_url.format(year=date.year)
                        return database_url
                break

        if self.verbose:
            print(f"No data for {date}")
        return None
    
    def _initialize_database_coords(self, date: datetime, db_url: str, is_2d: bool):
        """Initialize coordinates for a database if not already cached"""
        db_key = f"{db_url}_{'2d' if is_2d else '3d'}"
        
        if db_key in self.db_cache:
            return True
        
        # Adjust longitude limits for post-2017 databases
        adjusted_xlims = self._adjust_longitude_limits(date, self.xlims)
        
        # Define bounding box
        if is_2d:
            bbox = {
                "xmin": adjusted_xlims[0],
                "xmax": adjusted_xlims[1],
                "ymin": self.ylims[0],
                "ymax": self.ylims[1],
            }
        else:
            bbox = {
                "xmin": adjusted_xlims[0],
                "xmax": adjusted_xlims[1],
                "ymin": self.ylims[0],
                "ymax": self.ylims[1],
                "zmin": self.zlims[0],
                "zmax": self.zlims[1],
            }
        
        return self._get_database_coords(date, db_url, bbox, not is_2d)
    
    def _download_hycom_file(self, date: datetime, db_url: str, var_list: List[str], output_file: Path) -> bool:
        """Download a single HYCOM file for given database and variables"""
        try:
            # Determine if this is a 2D database
            is_2d_db = all(var in self.two_dimensional_vars for var in var_list)
            
            # Initialize coordinates for this database
            if not self._initialize_database_coords(date, db_url, is_2d_db):
                return False
            
            # Get indices for this database
            idx_set = self._get_idxs(date, db_url, is_2d=is_2d_db)
            
            # Skip if no valid time indices
            if idx_set[0] == "0:1:0":
                if self.verbose:
                    print(f"No time indices found for {date} in {db_url}, skipping...")
                return False
            
            # Construct OpenDAP URL
            url = self._construct_opendap_url(var_list, idx_set, date, db_url, is_2d=is_2d_db)
            
            if self.verbose:
                self.log(url)
            
            # Download and save file
            return self._download_single_file(output_file, url)
            
        except Exception as e:
            if self.verbose:
                print(f"Error downloading from {db_url} for date {date}: {e}")
            return False
    
    def download(self):
        """HYCOM-specific download loop - yields tasks for new base class"""
        for date in self.times:
            # Get database mapping for this date
            db_info = self._get_database(date)
            if db_info is None:
                continue
            
            # Check if we have a multi-database situation (new format)
            is_multi_db = isinstance(db_info, dict)
            
            if is_multi_db:
                # Multi-database format: yield one task per database
                for db_url, var_list in db_info.items():
                    db_name = db_url.split('/')[-1]
                    output_file = self._get_output_filename(date, db_name)
                    
                    yield {
                        'file_path': output_file,
                        'url': db_url,
                        'timestamp': date,
                        'variable': f"{len(var_list)}_vars",
                        'download_func': lambda d=date, url=db_url, vars=var_list, out=output_file: 
                            self._download_hycom_file(d, url, vars, out)
                    }
            else:
                # Single database format
                output_file = self._get_output_filename(date)
                
                yield {
                    'file_path': output_file,
                    'url': db_info,
                    'timestamp': date,
                    'variable': f"{len(self.variables)}_vars",
                    'download_func': lambda d=date, url=db_info, vars=self.variables, out=output_file: 
                        self._download_hycom_file(d, url, vars, out)
                }
    
    # All the complex HYCOM-specific methods remain the same
    def _adjust_longitude_limits(self, date: datetime, xlims: Tuple[float, float]) -> Tuple[float, float]:
        """Adjust longitude limits if needed based on date"""
        xmin, xmax = xlims
        # Hycom specific logic - xmin/xmax needs jumped up after this date
        if date >= datetime(2017, 10, 1):
            xmin = xmin + 360.0 if xmin < 0 else xmin
            xmax = xmax + 360.0 if xmax <= 0 else xmax
        return (xmin, xmax)
    
    def _get_database_coords(self, date: datetime, database: str, bbox: Dict[str, float], include_depth: bool) -> bool:
        """Get coordinates for a database"""
        # Create key for database cache
        db_key = f"{database}_{'3d' if include_depth else '2d'}"
        
        # Check if coordinates are already cached
        if db_key in self.db_cache:
            return True
        
        # Construct base URL for coordinates
        if include_depth:
            baseurl = f"https://tds.hycom.org/thredds/dodsC/{database}?lat,lon,time,depth"
        else:
            baseurl = f"https://tds.hycom.org/thredds/dodsC/{database}?lat,lon,time"
        
        if self.verbose:
            print(f"-- Getting coordinates for database: {database} ({'3D' if include_depth else '2D'}) --")
        
        try:
            ds = xr.open_dataset(baseurl)
            
            # Extract coordinates
            lon = ds["lon"].values
            lat = ds["lat"].values
            times = ds["time"].values
            
            # Find indices within bounds
            lat_idxs = np.where((lat >= bbox["ymin"]) & (lat <= bbox["ymax"]))[0]
            lon_idxs = np.where((lon >= bbox["xmin"]) & (lon <= bbox["xmax"]))[0]
            
            # Create cache entry
            cache_entry = {
                'times': times,
                'lon_idxs': lon_idxs,
                'lat_idxs': lat_idxs,
            }
            
            # Add depth if needed
            if include_depth:
                dep = ds["depth"].values
                dep_idxs = np.where((dep >= bbox["zmin"]) & (dep <= bbox["zmax"]))[0]
                cache_entry['dep_idxs'] = dep_idxs
            
            # Store in cache
            self.db_cache[db_key] = cache_entry
            
            if self.verbose:
                print(f"Coordinates cached for {db_key}")
                print(f"  Time shape: {times.shape}")
                print(f"  Lon indices: {len(lon_idxs)}")
                print(f"  Lat indices: {len(lat_idxs)}")
                if include_depth:
                    print(f"  Depth indices: {len(dep_idxs)}")
            
            return True
            
        except Exception as e:
            print(f"Error retrieving coordinates for database {database}: {e}")
            # Create an empty entry to prevent repeated attempts
            self.db_cache[db_key] = {
                'times': np.array([]),
                'lon_idxs': np.array([]),
                'lat_idxs': np.array([]),
            }
            if include_depth:
                self.db_cache[db_key]['dep_idxs'] = np.array([])
                
            return False
    
    def _find_time_indices(self, date: datetime, times: np.ndarray) -> np.ndarray:
        """Find indices in times array that match the given date at specified time intervals"""
        # Convert to datetime for consistent handling
        date_dt = pd.Timestamp(date).floor('us').to_pydatetime()
        # Create a date-only object for comparison
        date_only = date_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        next_day = date_only + timedelta(days=1)
        
        # Get all timesteps within this day
        day_indices = []
        for i, t in enumerate(times):
            t_dt = pd.Timestamp(t).floor('us').to_pydatetime()
            # Check if the timestamp is on the same date
            if date_only <= t_dt < next_day:
                day_indices.append((i, t_dt))
        
        # If no timestamps found for this day, return empty array
        if not day_indices:
            return np.array([])
            
        # Handle "best" time interval - return all available timesteps
        if self.time_interval == "best":
            return np.array([idx for idx, _ in day_indices])
            
        # For daily interval (24 hours), try to find a timestamp closest to noon
        if self.time_interval >= 24:
            # Target time is noon
            target_time = date_only + timedelta(hours=12)
            
            # Find timestamp closest to noon
            closest_idx = min(day_indices, key=lambda x: abs((x[1] - target_time).total_seconds()))[0]
            return np.array([closest_idx])
                
        # For sub-daily intervals (e.g., 3, 6, 12 hours)
        selected_indices = []
        for hour in range(0, 24, self.time_interval):
            target_time = date_only + timedelta(hours=hour)  # Target start of interval
            
            # Find indices within this interval
            interval_indices = [
                (idx, dt) for idx, dt in day_indices
                if date_only + timedelta(hours=hour) <= dt < date_only + timedelta(hours=hour + self.time_interval)
            ]
            
            if interval_indices:
                # Find closest to the start of the interval
                closest_idx = min(interval_indices, key=lambda x: abs((x[1] - target_time).total_seconds()))[0]
                selected_indices.append(closest_idx)
        
        return np.array(selected_indices)
    
    def _format_opendap_slice(self, indices: np.ndarray) -> str:
        """Convert array of indices into OpenDAP slice format (start:step:stop)"""
        if len(indices) == 0:
            return "0:1:0"  # Empty slice
        
        if len(indices) == 1:
            return f"{indices[0]}:1:{indices[0]}"
        
        # Calculate differences between consecutive indices
        diff = np.diff(indices)
        
        # Check if we have a constant step size
        unique_steps = np.unique(diff)
        
        if len(unique_steps) == 1:
            # Continuous sequence with constant step
            step = unique_steps[0]
            return f"{indices[0]}:{step}:{indices[-1]}"
        else:
            # Try to find the most common step size
            step = np.bincount(diff).argmax()
            return f"{indices[0]}:{step}:{indices[-1]}"
    
    def _get_idxs(self, date: datetime, database: str, is_2d: bool = False) -> Tuple[str, str, str, Optional[str]]:
        """Get indices for the given database"""
        # Create key for database lookup
        db_key = f"{database}_{'2d' if is_2d else '3d'}"
        
        # Check if database has been initialized
        if db_key not in self.db_cache:
            if self.verbose:
                print(f"Warning: Database {db_key} not initialized. Unable to get indices.")
            return "0:1:0", "0:1:0", "0:1:0", None if is_2d else "0:1:0"
        
        # Get database data
        db_data = self.db_cache[db_key]
        
        # Check if database has valid data
        if len(db_data['times']) == 0:
            if self.verbose:
                print(f"Warning: No time data for {db_key}. Unable to get indices.")
            return "0:1:0", "0:1:0", "0:1:0", None if is_2d else "0:1:0"
        
        # Get the database-specific indices and times
        times = db_data['times']
        lon_idxs = db_data['lon_idxs']
        lat_idxs = db_data['lat_idxs']
        
        # Format basic indices for OpenDAP
        lon_idx = self._format_opendap_slice(lon_idxs)
        lat_idx = self._format_opendap_slice(lat_idxs)
        
        # For 2D variables (like surf_el), don't include depth
        if is_2d:
            dep_idx = None
        else:
            dep_idxs = db_data['dep_idxs']
            dep_idx = self._format_opendap_slice(dep_idxs)
        
        # Find time indices for this date
        try:
            time_idxs = self._find_time_indices(date, times)
            if len(time_idxs) == 0:
                if self.verbose:
                    print(f"Warning: No time indices found for {date} in {db_key}.")
                    print(f"Available times range: {pd.Timestamp(times[0])} to {pd.Timestamp(times[-1])}")
                return "0:1:0", lon_idx, lat_idx, dep_idx
            
            time_idx = self._format_opendap_slice(time_idxs)
            return time_idx, lon_idx, lat_idx, dep_idx
        except Exception as e:
            print(f"Error finding time indices for {date} in {db_key}: {e}")
            return "0:1:0", lon_idx, lat_idx, dep_idx
    
    def _construct_opendap_url(self, variables: List[str], idx_set: Tuple[str, str, str, Optional[str]], 
                              date: datetime, database: str, is_2d: bool = False) -> str:
        """Construct OpenDAP URL for the given variables and indices"""
        time_idx, lon_idx, lat_idx, dep_idx = idx_set

        # For future dates (forecasts), use a different URL format
        if date >= datetime.now():
            date2 = datetime.now() - timedelta(days=1)
            base_url = (
                f"https://tds.hycom.org/thredds/dodsC/{database}/FMRC/runs/GLBy0.08_930_FMRC_RUN_"
                + f'{date2.strftime("%Y-%m-%dT12:00:00Z")}?'
            )
        else:
            base_url = f"https://tds.hycom.org/thredds/dodsC/{database}?"
            
        # Add coordinate subsetting
        if is_2d:
            # For 2D variables (no depth)
            url = base_url + f"lat[{lat_idx}],lon[{lon_idx}],time[{time_idx}]"
        else:
            # For 3D variables (with depth)
            url = base_url + f"lat[{lat_idx}],lon[{lon_idx}],depth[{dep_idx}],time[{time_idx}]"

        # Add variable subsetting
        for v in variables:
            if v == "surf_el" or is_2d:
                # 2D variable (no depth dimension)
                url += f",{v}[{time_idx}][{lat_idx}][{lon_idx}]"
            else:
                # 3D variable (with depth dimension)
                url += f",{v}[{time_idx}][{dep_idx}][{lat_idx}][{lon_idx}]"

        return url
    
    def _download_single_file(self, fname: Path, url: str) -> bool:
        """Download a single HYCOM subset file"""
        assert fname.parent.exists(), "Output folder does not exist. Please create this first"
        
        try:
            ds = xr.open_dataset(url)
            ds.to_netcdf(fname, format="NETCDF4")
            assert fname.exists()
            return True
        except Exception as e:
            if self.verbose:
                print(f"File download failed: {e}")
            sleep(self.timeout)
            
            # Retry with decreasing tries
            if self.max_tries > 1:
                if self.verbose:
                    print(f"Retrying... {self.max_tries-1} tries left")
                self.max_tries -= 1
                return self._download_single_file(fname, url)
            return False

class MergeHYCOM(BaseMerger):
    def _init_specific(self) -> None:
        self.source = "HYCOM"
        self.mode = "OCEAN"
        self._load_config()

    def _extract_target_coordinates(self, datasets: List[xr.Dataset]) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
        """Extract coordinates from the most complete dataset (prefer later models)."""
        # Use last dataset (reverse sorted) as it has extended coordinates
        for ds in reversed(datasets):
            if ds is not None:
                lon = ds['lon'].values
                lat = ds['lat'].values
                depth = ds['depth'].values if 'depth' in ds else None
                return lon, lat, depth
        
        raise ValueError("No valid datasets found for coordinate extraction")

    def _process_file(self, file_path: Path) -> Optional[xr.Dataset]:
        """Load and apply basic HYCOM processing."""
        ds = self._open_subset_netcdf(file_path, chunks=dict(time=24))
        if ds is not None:
            # Apply longitude wrapping (crucial for HYCOM because of mixed grids!!) 
            ds = ds.assign_coords(lon=((ds.lon + 180) % 360) - 180)
        return ds

    def _check_sub_daily_data(self, ds: xr.Dataset) -> bool:
        """Check if dataset contains sub-daily (< 24 hour) temporal resolution."""
        if ds is not None and len(ds['time']) > 1:
            time_diffs = np.diff(ds['time'].values).astype('timedelta64[h]').astype(int)
            return np.any(time_diffs < 24)
        return False

    def _apply_tidal_filtering(self, ds: xr.Dataset) -> xr.Dataset:
        """Apply 25-hour centered rolling mean to remove tidal signal from post-2024-08-09 data."""
        cutoff_time = pd.Timestamp('2024-08-09 23:59:00')
        
        # Filter time indices after cutoff
        post_cutoff_mask = ds['time'] > cutoff_time
        
        if not post_cutoff_mask.any():
            return ds  # No data after cutoff, return unchanged
            
        # Apply rolling mean only to post-cutoff data
        ds_filtered = ds.copy()
        
        # Process all time-dependent variables at once to avoid repeated rolling operations
        time_vars = [var for var in ds.data_vars if 'time' in ds[var].dims]
        
        if time_vars:
            # Create single rolling object and apply to all variables
            rolling_ds = ds[time_vars].rolling(time=25, center=True, min_periods=1).reduce(np.nanmean)
            
            for var_name in time_vars:
                # Only replace post-cutoff values
                ds_filtered[var_name] = xr.where(
                    post_cutoff_mask, 
                    rolling_ds[var_name], 
                    ds[var_name]
                )
        
        return ds_filtered

    def merge_files(self, file_list: List[Path]) -> Tuple[xr.Dataset, List[Path]]:
        """Merge HYCOM files: group by startdate, merge variables, then concat time."""
        if not file_list:
            raise ValueError("No files provided for merging")
            
        # Sort reverse to get extended coordinates from later models
        file_list.sort(reverse=True)
        
        # Group by start date
        startdates = [f.stem.split('_')[2] for f in file_list]
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
        
        # Extract target coordinates
        target_lon, target_lat, target_depth = self._extract_target_coordinates(all_datasets)
        
        # Check if we have post-2024-08-10 data and if it's sub-daily
        cutoff_date = pd.Timestamp('2024-08-10')
        has_post_cutoff_data = False
        apply_tidal_filtering = False
        
        # Check latest startdate (files are reverse sorted)
        if startdates:
            latest_startdate = pd.Timestamp(startdates[0])
            if latest_startdate >= cutoff_date:
                has_post_cutoff_data = True
                # Check the most recent dataset for sub-daily data
                if all_datasets and self._check_sub_daily_data(all_datasets[0]):
                    apply_tidal_filtering = True
        
        print("Concatenating and interpolating xarray dataset")
        if has_post_cutoff_data and apply_tidal_filtering:
            print('... Dataset contains sub-daily data post-2024-08-10 (HYCOM ESPC-D-V02), applying tidal filtering using a simple 25h rolling mean.')
            print('... Warning: Your dataset should be padded at least 1 full day either side before using in TUFLOW FV.')
        
        # Merge variables for each start date group
        merged_by_date = []
        for date_group in grouped_files.values():
            if date_group:
                interpolated = []
                for ds in date_group:
                    # Interpolate to common grid (2D or 3D as appropriate)
                    if target_depth is not None and 'depth' in ds.dims:
                        ds_interp = ds.interp(lon=target_lon, lat=target_lat, depth=target_depth,
                                            method='nearest', kwargs=dict(fill_value='extrapolate'))
                    else:
                        ds_interp = ds.interp(lon=target_lon, lat=target_lat,
                                            method='nearest', kwargs=dict(fill_value='extrapolate'))
                    interpolated.append(ds_interp)
                
                merged_by_date.append(xr.merge(interpolated, compat='override'))
        
        # Concatenate along time dimension
        merged = xr.concat(merged_by_date, dim="time", combine_attrs="override",
                          data_vars="minimal", coords="minimal", compat="override")
        
        # Apply tidal filtering to the merged dataset if needed
        if apply_tidal_filtering:
            # Copy the original surface elevation data to a raw variable for later
            raw_surf_el = merged['surf_el'].copy()
            merged = self._apply_tidal_filtering(merged)

            # Copy original surface elevation
            merged['raw_surf_el'] = raw_surf_el
            merged['raw_surf_el'].attrs['note'] = 'Original HYCOM water-level containing tides after 2024-08-10'
        
        # Final cleanup
        merged = merged.rename({'lon': 'longitude', 'lat': 'latitude'})
        merged = merged.sortby('time')
        _, unique_idx = np.unique(merged['time'], return_index=True)
        merged = merged.isel(time=unique_idx)
        
        return merged, skipped_files