from datetime import datetime
from typing import Callable, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import xarray as xr


class FVCWriter:
    """Base class for writing FVC files."""

    def __init__(
        self, requires_coordinates: bool = True, source=None, model=None, info_url=None
    ):
        """Initialize FVC writer.

        Args:
            requires_coordinates: Whether this FVC type requires coordinate information
        """
        self.requires_coordinates = requires_coordinates
        self.coordinate_vars: Optional[Tuple[str, str]] = ("longitude", "latitude")
        self.time_var: str = "time"
        self.tzlbl: Optional[str] = None
        self.epsg: Optional[str] = None
        self.crs_name: Optional[str] = None

        # For metadata
        self.source = source
        self.model = model
        self.info_url = info_url

    def detect_coordinates(self, ds: xr.Dataset) -> Optional[Tuple[str, str]]:
        """Detect coordinate system from dataset if present.

        Args:
            ds: Input xarray Dataset

        Returns:
            Optional[Tuple[str, str]]: x and y coordinate variable names if found
        """
        if not self.requires_coordinates:
            return None

        if "x" in ds and "y" in ds:
            # Get CRS information from reprojected coordinates
            try:
                self.epsg = ds["x"].attrs.get("epsg")
                self.crs_name = ds["x"].attrs.get("name")
            except (KeyError, AttributeError):
                pass
            return "x", "y"
        elif "longitude" in ds and "latitude" in ds:
            # Get CRS information from geographic coordinates if available
            try:
                self.epsg = ds["longitude"].attrs.get("epsg")
                self.crs_name = ds["longitude"].attrs.get("name")
            except (KeyError, AttributeError):
                pass
            return "longitude", "latitude"
        elif self.requires_coordinates:
            raise ValueError(
                "Dataset requires coordinate variables (x,y or longitude,latitude) but none were found"
            )
        return None

    def detect_time_settings(self, ds: xr.Dataset) -> str:
        """Detect time variable and settings from dataset.

        Args:
            ds: Input xarray Dataset

        Returns:
            str: Name of time variable to use
        """
        if "local_time" in ds:
            try:
                self.tzlbl = ds["local_time"].attrs.get("tz")
            except (KeyError, AttributeError):
                pass
            return "local_time"
        return "time"

    def process_dataset(self, ds: xr.Dataset) -> None:
        """Process dataset to detect coordinate system and time settings.

        Args:
            ds: Input xarray Dataset
        """
        self.coordinate_vars = self.detect_coordinates(ds)
        self.time_var = self.detect_time_settings(ds)

    def get_coordinate_info(self, ds: xr.Dataset) -> Optional[dict]:
        """Extract coordinate information from dataset if available.

        Args:
            ds: Input xarray Dataset

        Returns:
            Optional[dict]: Dictionary containing coordinate variable names and limits if coordinates exist
        """
        if not self.coordinate_vars:
            return None

        xvar, yvar = self.coordinate_vars
        return {
            "xvar": xvar,
            "yvar": yvar,
            "xlims": format_limits(ds[xvar].values),
            "ylims": format_limits(ds[yvar].values),
        }

    def write_header(
        self, f: Union[List[str], any], title: str, ds: xr.Dataset
    ) -> None:
        """Write standard FVC file header.

        Args:
            f: File handle or list to write to
            title: Title string for the header
            ds: xarray Dataset for time/coordinate info
        """
        # Process dataset if not already done
        self.process_dataset(ds)

        lines = []
        lines.append(f"! TUFLOW FV FVC File for {title}")
        lines.append("! Written by TUFLOW FV `tfv-get-tools`")
        lines.append("")
        # These lines are too long, need to split over several lines
        lines.append("! This control file has been prepared using the TUFLOW FV Get Tools (tfv-get-tools),")
        lines.append("! a free set of Python tools designed to assist with the download and formatting of")
        lines.append("! boundary condition data from global model sources such as ERA5 and CFSR for use in TUFLOW FV.")
        lines.append("! These external model datasets are subject to change over time and are provided 'as is'.")
        lines.append("! Users are responsible for reviewing and, where possible, verifying these inputs against")
        lines.append("! observational data before use in any modelling application.")
        lines.append("")

        # Now bang in some standard source info and a sicko disclaimer
        lines.append(f"! Source: {self.source if self.source else 'Unknown'}")
        if self.model:
            if self.model != "default":
                lines.append(f"! Model: {self.model}")
        if self.info_url:
            lines.append(f"! Info: {self.info_url}")
        lines.append("")

        # Add timezone information if using local time
        time_var = "local_time" if "local_time" in ds else "time"
        if time_var == "local_time":
            lines.append(f"! NetCDF time datum: {ds[time_var].attrs['tz']}")
        else:
            lines.append("! NetCDF time datum: UTC")

        # Add time information
        lines.append(f"! NetCDF start time: {ds_time_to_str(ds, 0)}")
        lines.append(f"! NetCDF end time: {ds_time_to_str(ds, -1)}")
        lines.append("")

        # Add coordinate system information if available
        if self.requires_coordinates and (self.epsg or self.crs_name):
            if self.epsg:
                lines.append(f"! Coordinate system EPSG: {self.epsg}")
            if self.crs_name:
                lines.append(f"! Coordinate system name: {self.crs_name}")

        # Add coordinate limits if required and available
        if self.requires_coordinates:
            coords = self.get_coordinate_info(ds)
            if coords:
                lines.append(f"! NetCDF x-limits: {coords['xlims']}")
                lines.append(f"! NetCDF y-limits: {coords['ylims']}")

        lines.append("")

        if isinstance(f, list):
            f.extend(lines)
        else:
            for line in lines:
                f.write(line + "\n")


def format_limits(values: np.ndarray, funcs: List[Callable] = [np.min, np.max]) -> str:
    """Format array limits into a string using specified functions."""
    return ", ".join([f"{fn(values):0.4f}" for fn in funcs])


def format_timestamp(
    timestamp: Union[str, datetime, np.datetime64, pd.Timestamp],
    fmt: str = "%Y-%m-%d %H:%M",
) -> str:
    """Format various timestamp types to a consistent string format.

    Args:
        timestamp: Input timestamp as string, datetime, numpy.datetime64, or pandas.Timestamp
        fmt: Output format string (default: "%Y-%m-%d %H:%M")

    Returns:
        str: Formatted timestamp string

    Examples:
        >>> format_timestamp("2024-01-01")
        '2024-01-01 00:00'
        >>> format_timestamp(np.datetime64("2024-01-01"))
        '2024-01-01 00:00'
        >>> format_timestamp(pd.Timestamp("2024-01-01"))
        '2024-01-01 00:00'
    """
    # Convert to pandas Timestamp
    if isinstance(timestamp, (str, np.datetime64, datetime)):
        timestamp = pd.Timestamp(timestamp)

    return timestamp.strftime(fmt)


def ds_time_to_str(ds: xr.Dataset, i: int, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Convert a time from an xarray Dataset to a formatted string."""
    time_var = "local_time" if "local_time" in ds else "time"
    return format_timestamp(ds[time_var].values[i], fmt)
