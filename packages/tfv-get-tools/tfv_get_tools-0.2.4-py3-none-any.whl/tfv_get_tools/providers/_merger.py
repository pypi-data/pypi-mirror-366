"""Base merger class, inherited by all source specific mergers."""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import xarray as xr
from dask.diagnostics.progress import ProgressBar
from pandas.tseries.offsets import MonthBegin, MonthEnd
from pyproj import CRS, Transformer

from tfv_get_tools._standard_attrs import STDVARS
from tfv_get_tools.fvc import write_atmos_fvc, write_ocean_fvc
from tfv_get_tools.providers._custom_conversions import *
from tfv_get_tools.providers._utilities import _get_config, wrap_longitude
from tfv_get_tools.utilities.horizontal_padding import horizontal_pad
from tfv_get_tools.utilities.land_masking import mask_land_data
from tfv_get_tools.utilities.parsers import _parse_date, _parse_path


def check_path(path: Path) -> Path:
    """Helper function to check if a path exists and create it if it doesn't."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


class BaseMerger(ABC):
    """Base class for merger operations."""

    def __init__(
        self,
        in_path: Path = Path("./raw"),
        out_path: Path = Path("."),
        fname: Optional[str] = None,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        write_fvc: bool = True,
        reproject: Optional[int] = None,
        local_tz: Optional[Tuple[float, str]] = None,
        pad_dry: bool = False,
        wrapto360: bool = False,
        source: str = "HYCOM",
        mode: str = "OCEAN",
        model: str = "default",
        execute: bool = True,
        write: bool = True,
        verbose: bool = True,
    ):
        """
        Initialize the BaseMerger with parameters for merging and processing data files.

        Args:
            in_path: Directory of the raw data files
            out_path: Output directory for the merged netcdf and (opt) the fvc
            fname: Merged netcdf filename
            time_start: Start time limit of the merged dataset (format: "YYYY-mm-dd HH:MM")
            time_end: End time limit of the merged dataset (format: "YYYY-mm-dd HH:MM")
            write_fvc: Whether to write an accompanying .fvc file
            reproject: EPSG code for optional reprojection
            local_tz: Local timezone info as (Offset[float], Label[str])
            pad_dry: Whether to pad horizontally
            wrapto360: Whether to wrap longitudes to 360 degrees
            source: Source name {HYCOM, COPERNICUS}
            mode: Mode name
            model: Model name
            execute: Execute processing
            write: Write the dataset. If False, access via `.ds`
            verbose: Enable verbose output
        """
        # Parse and validate inputs
        self.in_path = _parse_path(in_path)
        self.out_path = _parse_path(out_path)

        # Time indexing
        self.ts = _parse_date(time_start) if time_start is not None else None
        self.te = _parse_date(time_end) if time_end is not None else None
        self.time_slice = slice(self.ts, self.te)

        # Validate and set attributes
        self.fname = self._validate_fname(fname)
        self.write_fvc = write_fvc
        self.reproject = self._validate_reproject(reproject)
        self.local_tz = self._validate_local_tz(local_tz)
        self.pad_dry = pad_dry
        self.wrapto360 = wrapto360
        self.verbose = verbose

        # Source/mode/model attributes
        self.mode = mode
        self.source = source
        self.model = model if model else "default"
        self.write = write

        # Initialize source-specific settings
        self._init_specific()

        if self.verbose:
            self._print_config()

        if execute:
            self.process()

    def _print_config(self) -> None:
        """Print configuration information."""
        print("Running TUFLOW FV Boundary Condition Merger")
        print(f"Source: {self.source}")
        print(f"Mode: {self.mode}")
        if self.model != "default":
            print(f"Model: {self.model}")
        print("\nOpening raw files and preparing to interpolate all to a common grid")
        print("This step can take a while, please wait")

    @staticmethod
    def _validate_fname(fname: Optional[str]) -> Optional[str]:
        """Validate filename."""
        if fname and not fname.endswith(".nc"):
            raise ValueError("Filename must end with '.nc'")
        return fname

    @staticmethod
    def _validate_reproject(reproject: Optional[int]) -> Optional[int]:
        """Validate EPSG code for reprojection."""
        if reproject and not (1000 <= reproject <= 32767):
            raise ValueError("Invalid EPSG code for reprojection")
        return reproject

    @staticmethod
    def _validate_local_tz(
        local_tz: Optional[Tuple[float, str]],
    ) -> Optional[Tuple[float, str]]:
        """Validate local timezone information."""
        if local_tz:
            if not isinstance(local_tz, tuple) or len(local_tz) != 2:
                raise ValueError("local_tz must be a tuple of (float, str)")
            if not isinstance(local_tz[0], (int, float)) or not isinstance(
                local_tz[1], str
            ):
                raise ValueError("local_tz must be in the format (float, str)")
        return local_tz

    def _load_config(self) -> None:
        """Load configuration for the specific source/mode/model combination."""
        cfg, _ = _get_config(self.mode, self.source, self.model)
        self.cfg = cfg

    @abstractmethod
    def _init_specific(self) -> None:
        """Initialize source-specific settings. Must be implemented by subclasses."""
        pass

    def _open_subset_netcdf(
        self, file: Path, time: Union[str, Tuple[str, ...]] = "time", **kwargs
    ) -> Optional[xr.Dataset]:
        """
        Open a subset netcdf file and validate for merging.

        Args:
            file: Path to the netcdf file
            time: Time coordinate name(s)
            **kwargs: Additional arguments for xr.open_dataset

        Returns:
            Dataset or None if file cannot be opened
        """
        chunks = kwargs.pop("chunks", dict(time=24))

        try:
            ds = xr.open_dataset(file, chunks=chunks, **kwargs)

            # Handle multiple possible time coordinate names
            if isinstance(time, tuple):
                time_var = None
                for t in time:
                    if t in ds:
                        time_var = t
                        break
                time = time_var

            if time and pd.api.types.is_datetime64_any_dtype(ds[time]):
                return ds
            else:
                if self.verbose:
                    print(f"Skipping file {file.name} - time error")
                return None

        except Exception as e:
            if self.verbose:
                print(f"Skipping file {file.name}: {str(e)}")
            return None

    def _filter_files_by_time(self, file_list: List[Path]) -> List[Path]:
        """
        Filter files based on time constraints.

        Args:
            file_list: List of file paths

        Returns:
            Filtered list of file paths
        """
        if self.ts is None and self.te is None:
            return file_list

        download_interval = self.cfg.get("_DOWNLOAD_INTERVAL", "monthly")

        if download_interval == "monthly":
            time_stings = [re.search(r'_(\d{8})_(\d{8})', x.stem) for x in file_list]
            start_time_strings = [x.group(1) for x in time_stings]
            end_time_strings = [x.group(2) for x in time_stings]
            
            start_times = pd.DatetimeIndex(
                [pd.to_datetime(x, format="%Y%m%d") for x in start_time_strings]
            )
            end_times = pd.DatetimeIndex(
                [pd.to_datetime(x, format="%Y%m%d") for x in end_time_strings]
            )

        elif download_interval == "daily":
            start_time_strings = [re.search(r'_(\d{8})_', x.stem).group(1) for x in file_list]
            start_times = pd.DatetimeIndex(
                [pd.to_datetime(x, format="%Y%m%d") for x in start_time_strings]
            )
            end_times = start_times + pd.Timedelta("23.99h")
        else:
            raise ValueError(f"Unknown download interval: {download_interval}")

        time_start = self.ts if self.ts is not None else start_times.min()
        time_end = self.te if self.te is not None else end_times.max()

        time_start = pd.Timestamp(time_start)
        time_end = pd.Timestamp(time_end)

        if download_interval == "monthly":
            time_start = time_start - MonthBegin(1)
            time_end = time_end + MonthEnd(1)

        mask = (start_times >= time_start) & (end_times <= time_end)
        return [file_list[i] for i in mask.nonzero()[0]]

    def get_file_list(self) -> List[Path]:
        """
        Get the list of files to be merged.

        Returns:
            List of file paths to be merged
        """
        # Construct search pattern
        query_parts = [self.source, self.mode]
        if self.model != "default":
            query_parts.append(self.model)
        query = "_".join(query_parts).upper()

        file_list = list(self.in_path.glob(f"*{query}*.nc"))

        if not file_list:
            raise FileNotFoundError(
                f"No files found matching pattern '*{query}*.nc' in {self.in_path}"
            )

        return self._filter_files_by_time(file_list)

    @abstractmethod
    def merge_files(self, file_list: List[Path]) -> Tuple[xr.Dataset, List[Path]]:
        """
        Merge the given files into a single xarray Dataset.

        Args:
            file_list: List of file paths to merge

        Returns:
            Tuple of (merged dataset, list of skipped files)
        """
        pass

    def _apply_preprocessing(self, ds: xr.Dataset) -> xr.Dataset:
        """
        Apply preprocessing steps defined in configuration.

        Args:
            ds: Input dataset

        Returns:
            Dataset with preprocessing applied
        """
        for vals in self.cfg.values():
            if "pre_process" in vals:
                var = vals["source_var"]
                pattern = r"\b([a-zA-Z_]\w*)\b"
                components = re.findall(pattern, vals["pre_process"])
                fn_call = eval(components[0])
                in_var_strs = components[1:]

                in_vars = [ds[v] for v in in_var_strs if v in ds.data_vars.keys()]
                if len(in_vars) == len(in_var_strs):
                    ds[var] = xr.apply_ufunc(fn_call, *in_vars, dask="allowed")

        return ds

    def standardise_dataset(self, ds: xr.Dataset) -> xr.Dataset:
        """
        Standardise dataset by renaming variables and applying attributes.

        Args:
            ds: Merged dataset with source-specific variable names

        Returns:
            Dataset with standardised variable names and attributes
        """
        # Apply preprocessing
        ds = self._apply_preprocessing(ds)

        # Rename variables
        name_remap = {
            v["source_var"]: k
            for k, v in self.cfg.items()
            if not k.startswith("_") and v["source_var"] in ds.data_vars
        }
        ds = ds.rename(name_remap)

        # Apply standard attributes
        for dv in ds.data_vars:
            if dv in STDVARS:
                ds[dv].attrs = STDVARS[dv]

        # Add coordinate attributes
        crs = CRS.from_epsg(4326)
        if "longitude" in ds.coords:
            ds["longitude"].attrs = dict(crs.cs_to_cf()[1], epsg=4326, name=crs.name)
        if "latitude" in ds.coords:
            ds["latitude"].attrs = dict(crs.cs_to_cf()[0], epsg=4326, name=crs.name)

        # Add coordinates field to data variables
        for dv in ds.data_vars:
            if {"longitude", "latitude"}.issubset(set(ds[dv].dims)):
                ds[dv].encoding.pop("coordinates", None)

                if "depth" in ds[dv].dims:
                    ds[dv].attrs["coordinates"] = "time depth latitude longitude"
                else:
                    ds[dv].attrs["coordinates"] = "time latitude longitude"

        # Add in a UTC label on the time array.
        ds["time"].attrs["tz"] = "UTC"

        return ds

    def wrap_longitudes(self, dataset: xr.Dataset, wrapto360: bool) -> xr.Dataset:
        """Wrap longitudes around 360 or 180 degrees."""
        return wrap_longitude(dataset, wrapto360=wrapto360)

    def pad_dataset(self, ds: xr.Dataset) -> xr.Dataset:
        """Pad the dataset to fill NaNs in horizontal space."""
        mode_lower = self.mode.lower()

        if mode_lower == "ocean":
            return horizontal_pad(ds)
        elif mode_lower == "atmos":
            return mask_land_data(ds, self.source.lower())
        elif mode_lower == "wave":
            if self.verbose:
                print(
                    "Land masking is not valid for wave data. Ignoring and carrying on"
                )
            return ds
        else:
            raise ValueError(f"Unknown mode for padding: {self.mode}")

    @staticmethod
    def reproject_dataset(ds: xr.Dataset, target_crs: int) -> Tuple[xr.Dataset, str]:
        """Reproject the dataset to a specified CRS."""
        crs = CRS.from_epsg(target_crs)
        transformer = Transformer.from_crs("epsg:4326", crs, always_xy=True)

        xv, yv = np.meshgrid(ds.longitude, ds.latitude)
        xp, yp = transformer.transform(xv, yv)
        ds = ds.assign_coords(
            dict(x=(("latitude", "longitude"), xp), y=(("latitude", "longitude"), yp))
        )
        ds["x"].attrs = dict(crs.cs_to_cf()[0], epsg=target_crs, name=crs.name)
        ds["y"].attrs = dict(crs.cs_to_cf()[1], epsg=target_crs, name=crs.name)

        return ds, f"EPSG{target_crs}"

    @staticmethod
    def add_local_timezone(ds: xr.Dataset, offset: float, label: str) -> xr.Dataset:
        """Add local timezone information to the dataset."""
        ds["time"].attrs = {"tz": "UTC"}

        ds = ds.assign_coords(
            dict(local_time=ds["time"] + pd.Timedelta(offset, unit="h"))
        )
        ds["local_time"].attrs = {"tz": label}

        # Handle high-resolution water level time if present
        if "wl_time" in ds.dims:
            ds = ds.assign_coords(
                dict(wl_local_time=ds["wl_time"] + pd.Timedelta(offset, unit="h"))
            )
            ds["wl_local_time"].attrs = {"tz": label}

        return ds

    def _generate_filename(self, ds: xr.Dataset) -> str:
        """Generate output filename based on dataset and settings."""
        if self.fname is not None:
            return self.fname

        # Extract time range
        time_values = pd.to_datetime(ds["time"][[0, -1]].values)
        ts = time_values[0].strftime("%Y%m%d")
        te = time_values[1].strftime("%Y%m%d")

        # Base filename
        name_parts = [self.source, self.mode]
        if self.model != "default":
            name_parts.append(self.model)

        base_name = "_".join(name_parts).upper()
        fname = f"{base_name}_{ts}_{te}.nc"

        # Add suffixes for processing options
        if self.local_tz is not None:
            tz_label = self.local_tz[1].replace(".", "p")
            fname = fname.replace(".", f"_{tz_label}.")

        if self.reproject is not None:
            fname = fname.replace(".", f"_EPSG{self.reproject}.")

        if self.pad_dry:
            fname = fname.replace(".", "_padded.")

        return fname

    def write_dataset(self, ds: xr.Dataset, output_path: str) -> None:
        """Write the dataset to a file."""
        time_vars = [coord for coord in ds.coords if "time" in coord]

        encoding = {
            var: {"units": "hours since 1990-01-01 00:00:00", "dtype": np.float64}
            for var in time_vars
        }

        write_task = ds.to_netcdf(output_path, compute=False, encoding=encoding)

        with ProgressBar():
            write_task.compute()

    def process(self) -> None:
        """Run through all steps to merge the dataset."""
        file_list = self.get_file_list()

        if not file_list:
            raise ValueError("No files found to merge")

        ds, skipped_list = self.merge_files(file_list)
        ds = self.standardise_dataset(ds)
        ds = self.wrap_longitudes(ds, self.wrapto360)

        if self.pad_dry:
            if self.verbose:
                print("...padding dataset")
            ds = self.pad_dataset(ds)

        crslbl = None
        if self.reproject is not None:
            if self.verbose:
                print(f"...reprojecting dataset to EPSG {self.reproject}")
            ds, crslbl = self.reproject_dataset(ds, self.reproject)

        if self.local_tz is not None:
            dt, lbl = self.local_tz
            if self.verbose:
                print(f"...adding local timezone {lbl} with offset of {dt} hours")
            ds = self.add_local_timezone(ds, dt, lbl)

        fname = self._generate_filename(ds)

        if self.verbose:
            print(f"Writing dataset: {fname}")

        if self.write:
            output_path = self.out_path / fname
            self.write_dataset(ds, output_path.as_posix())

            # Optionally write fvc - but only bother if we're writing the netty
            if self.write_fvc:
                fvc_fname = fname.replace(".nc", ".fvc")
                fvc_args = {
                    "nc_path": output_path.as_posix(),
                    "output_path": self.out_path,
                    "filename": fvc_fname,
                    "source": self.source,
                    "model": self.model,
                    "info_url": self.cfg.get("_INFO_URL", None),
                }
                if self.mode == "ATMOS":
                    write_atmos_fvc(ds, **fvc_args)
                elif self.mode == "OCEAN":
                    write_ocean_fvc(ds, **fvc_args)
        else:
            self.ds = ds

        if self.verbose:
            print("Merging finished")
            if skipped_list:
                print(
                    "The following raw files were skipped (file open / corruption failure)"
                )
                print("   \n".join([f.name for f in skipped_list]))
