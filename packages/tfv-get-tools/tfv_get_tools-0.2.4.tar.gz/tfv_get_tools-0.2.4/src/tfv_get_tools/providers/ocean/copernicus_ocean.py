"""
Copernicus Ocean
"""

from datetime import datetime
from functools import partial
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any

import copernicusmarine as cm
import numpy as np
import pandas as pd
from pandas.tseries.offsets import MonthEnd
from tqdm import tqdm
import xarray as xr

from tfv_get_tools.providers._downloader import BaseDownloader
from tfv_get_tools.providers._merger import BaseMerger
from tfv_get_tools.providers._utilities import todstr


class DownloadCopernicusOcean(BaseDownloader):
    """Copernicus Ocean downloader"""

    def _init_specific(self, **kwargs):
        """Set source and mode - matches original interface"""
        if self.model == "default":
            self.log("Default model has been selected == 'GLO'")
            self.model = "GLO"

        self.source = "COPERNICUS"
        self.mode = "OCEAN"
        self._load_config()

        # Login status tracking
        self._logged_in = False

        # Cache for temporal extents
        self._temporal_extents_cache = {}

        #
        if not self.verbose:
            logging.getLogger("copernicusmarine").setLevel(logging.WARNING)

    def _ensure_logged_in(self):
        """Ensure user is logged into Copernicus Marine Service"""
        if self._logged_in:
            return True

        # Fast credential check first
        if cm.login(check_credentials_valid=True):
            print("Found existing credentials file, skipping login check.")
            self._logged_in = True
            return True

        # Fallback to full login attempt
        print(
            "Login to Copernicus Marine Service required. Please enter your credentials."
        )
        print("Your credentials will be stored for next time.")
        print(
            'If you do not have an account, please register at "https://marine.copernicus.eu/".'
        )
        if cm.login():
            self._logged_in = True
            return True

        # Both methods failed
        raise AttributeError(
            "Login to Copernicus Marine Service has failed, please check credentials"
        )

    def _get_dataset_temporal_extent(self, dataset_id: str) -> Optional[Dict]:
        """Extract temporal extent for a dataset using Copernicus Marine API"""
        if dataset_id in self._temporal_extents_cache:
            return self._temporal_extents_cache[dataset_id]

        try:
            dataset_info = cm.describe(dataset_id=dataset_id)
            dataset_info_dict = (
                dataset_info.model_dump()
            )  # Use model_dump instead of deprecated dict()

            # Extract temporal extents
            for product in dataset_info_dict["products"]:
                for dataset in product["datasets"]:
                    if dataset["dataset_id"] == dataset_id:
                        for version in dataset["versions"]:
                            for part in version["parts"]:
                                for service in part["services"]:
                                    if service.get("variables"):
                                        for variable in service["variables"]:
                                            if variable.get("coordinates"):
                                                for coord in variable["coordinates"]:
                                                    if coord["coordinate_id"] == "time":
                                                        min_time_ms = coord[
                                                            "minimum_value"
                                                        ]
                                                        max_time_ms = coord[
                                                            "maximum_value"
                                                        ]

                                                        # Convert from milliseconds to datetime
                                                        start_date = (
                                                            datetime.fromtimestamp(
                                                                min_time_ms / 1000.0,
                                                            )
                                                        )
                                                        end_date = (
                                                            datetime.fromtimestamp(
                                                                max_time_ms / 1000.0,
                                                            )
                                                        )

                                                        extent = {
                                                            "start_date": start_date,
                                                            "end_date": end_date,
                                                            "start_timestamp_ms": min_time_ms,
                                                            "end_timestamp_ms": max_time_ms,
                                                        }

                                                        self._temporal_extents_cache[
                                                            dataset_id
                                                        ] = extent
                                                        return extent
        except Exception as e:
            if self.verbose:
                print(f"Failed to get temporal extent for {dataset_id}: {e}")
            return None

        return None

    def _get_dataset_group_temporal_intersection(
        self, dataset_group: Dict
    ) -> Optional[Tuple[datetime, datetime]]:
        """Get the temporal intersection of all datasets in a group"""
        if not dataset_group:
            return None

        extents = []
        for ds_id in dataset_group.keys():
            extent = self._get_dataset_temporal_extent(ds_id)
            if extent is None:
                return None
            extents.append(extent)

        # Find intersection (latest start, earliest end)
        latest_start = max(extent["start_date"] for extent in extents)
        earliest_end = min(extent["end_date"] for extent in extents)

        if latest_start <= earliest_end:
            return (latest_start, earliest_end)
        else:
            return None  # No overlap

    def _get_output_filename(
        self, ds_id: str, ts: pd.Timestamp, te: pd.Timestamp
    ) -> Path:
        """Copernicus filename pattern includes dataset ID"""
        outname = f"{self.prefix}_{ds_id}_{todstr(ts)}_{todstr(te)}.nc"
        return self.outdir / outname

    def _get_variables_for_dataset(self, dataset_config, ds_id: str):
        """Determine which variables to download for this dataset"""
        if self._custom_variables:
            # Use custom variables requested by user
            return self.variables
        else:
            # Use defaults (dataset-specific or global)
            if dataset_config[ds_id] == "default":
                return self.variables
            else:
                return dataset_config[ds_id]

    def get_variable_temporal_extents(self) -> Dict[str, Dict[str, Any]]:
        """Get temporal extents for each requested variable"""
        variable_extents = {}

        for variable in self.variables:
            # Find all datasets that contain this variable
            datasets_with_variable = []

            # Search through all dataset groups
            for dsmap_key, dataset_group in self.dsmap.items():
                for ds_id, variables in dataset_group.items():
                    if variable in variables:
                        extent = self._get_dataset_temporal_extent(ds_id)
                        if extent:
                            datasets_with_variable.append(
                                {
                                    "dataset_id": ds_id,
                                    "dsmap_key": dsmap_key,
                                    "start_date": extent["start_date"],
                                    "end_date": extent["end_date"],
                                }
                            )

            if datasets_with_variable:
                # Find the union of all temporal extents for this variable
                earliest_start = min(ds["start_date"] for ds in datasets_with_variable)
                latest_end = max(ds["end_date"] for ds in datasets_with_variable)

                variable_extents[variable] = {
                    "start_date": earliest_start,
                    "end_date": latest_end,
                    "datasets": datasets_with_variable,
                }

        return variable_extents

    def get_best_dsmap_key_for_date(
        self, target_date: pd.Timestamp, variable_extents: Dict
    ) -> Optional[str]:
        """Find the dsmap key that provides ALL variables for the given date"""
        target_dt = target_date.to_pydatetime()

        # Get all possible dsmap keys that could work for this date
        candidate_keys = set()
        for variable in self.variables:
            if variable in variable_extents:
                for dataset in variable_extents[variable]["datasets"]:
                    if dataset["start_date"] <= target_dt <= dataset["end_date"]:
                        candidate_keys.add(dataset["dsmap_key"])

        # Check each candidate key to see if it provides ALL variables for this date
        for dsmap_key in candidate_keys:
            can_provide_all = True

            for variable in self.variables:
                variable_available = False

                # Check if this dsmap_key has a dataset with this variable for this date
                if variable in variable_extents:
                    for dataset in variable_extents[variable]["datasets"]:
                        if (
                            dataset["dsmap_key"] == dsmap_key
                            and dataset["start_date"]
                            <= target_dt
                            <= dataset["end_date"]
                        ):
                            variable_available = True
                            break

                if not variable_available:
                    can_provide_all = False
                    break

            if can_provide_all:
                return dsmap_key

        return None

    def _download_single_file(
        self,
        ds_id: str,
        variables: list,
        ts: pd.Timestamp,
        te: pd.Timestamp,
        output_file: Path,
    ) -> bool:
        """Download single file via Copernicus Marine API"""
        try:
            xmin, xmax = self.xlims
            ymin, ymax = self.ylims
            zmin, zmax = self.zlims if self.zlims else (None, None)

            # Enforce UTC timezone for the Copernicus marine API
            ts = ts.tz_localize("UTC") if ts.tz is None else ts.tz_convert("UTC")
            te = te.tz_localize("UTC") if te.tz is None else te.tz_convert("UTC")

            cm.subset(
                dataset_id=ds_id,
                start_datetime=ts,
                end_datetime=te,
                minimum_longitude=xmin,
                maximum_longitude=xmax,
                minimum_latitude=ymin,
                maximum_latitude=ymax,
                minimum_depth=zmin,
                maximum_depth=zmax,
                variables=variables,
                output_filename=output_file.name,
                output_directory=output_file.parent,
                dataset_part="default",
            )
            return True

        except Exception as e:
            if self.verbose:
                error_msg = str(e)
                if "time dimension  exceed the dataset coordinates" in error_msg:
                    print("Time dimension exceeds coordinates - dataset incompatible")
                else:
                    print(f"Error downloading {output_file.name}: {error_msg}")
            return False

    def download(self):
        """Let her rip, potato chip"""

        assert self._ensure_logged_in(), "Login failed, cannot download data"

        # Get temporal extents for all variables upfront
        variable_extents = self.get_variable_temporal_extents()

        if not variable_extents:
            print("No temporal extents found for any requested variables!")
            return

        # Filter times to only those where all variables have coverage
        valid_times = []
        for ts in self.times:
            dsmap_key = self.get_best_dsmap_key_for_date(ts, variable_extents)
            if dsmap_key:
                valid_times.append(ts)
            elif self.verbose:
                print(f"Skipping {ts}: no dataset group provides all variables")

        if not valid_times:
            print(
                "No time periods found where all requested variables have dataset coverage!"
            )
            return

        if len(valid_times) < len(self.times):
            print(
                f"Warning: Only {len(valid_times)}/{len(self.times)} time periods have complete variable coverage"
            )

        # Process each valid time period
        for ts in valid_times:
            te = (ts + MonthEnd()).replace(hour=23, minute=59, second=59)

            # Get the best dsmap key for this time
            dsmap_key = self.get_best_dsmap_key_for_date(ts, variable_extents)
            # dataset_group = self.dsmap[dsmap_key]

            # Group variables by their datasets within this group
            dataset_variables = {}
            target_dt = ts.to_pydatetime()

            for variable in self.variables:
                for dataset_info in variable_extents[variable]["datasets"]:
                    if (
                        dataset_info["dsmap_key"] == dsmap_key
                        and dataset_info["start_date"]
                        <= target_dt
                        <= dataset_info["end_date"]
                    ):
                        ds_id = dataset_info["dataset_id"]

                        if ds_id not in dataset_variables:
                            dataset_variables[ds_id] = []
                        dataset_variables[ds_id].append(variable)
                        break

            # Download from each dataset
            for ds_id, variables in dataset_variables.items():
                output_file = self._get_output_filename(ds_id, ts, te)

                if self.verbose:
                    print(
                        f"Downloading {len(variables)} variables from {ds_id} for {ts}"
                    )
                    print(f"  Variables: {', '.join(variables)}")

                yield {
                    "file_path": output_file,
                    "url": f"copernicus://{ds_id}",
                    "timestamp": ts,
                    "variable": f"{len(variables)}_vars",
                    "download_func": partial(
                        self._download_single_file,
                        ds_id,
                        variables,
                        ts,
                        te,
                        output_file,
                    ),
                }


class MergeCopernicusOcean(BaseMerger):
    def _init_specific(self):
        self.source = "COPERNICUS"
        self.mode = "OCEAN"
        if self.model == "default":
            self.model = "GLO"
        self._load_config()

    def merge_files(self, file_list):
        """Copernicus sometimes requires use to first merge on variables,
        then concat on time.


        Args:
            file_list (list): list of path objects to open and concat.

        Returns:
            xr.Dataset: merged xarray dataset
            list: files unable to be merged
        """
        startdates = [x.stem.split("_")[-2] for x in file_list]
        unq_startdates = np.unique(startdates)

        dsset = {k: [] for k in unq_startdates}

        skipped_list = []
        for i, f in enumerate(tqdm(file_list)):
            dsx = self._open_subset_netcdf(f)

            # Water-level is tricky - it can be stored high-res
            # We'll create a daily mean water-level, plus the original hres water-level.
            if "zos" in dsx.data_vars:
                if dsx.sizes["time"] > 32:
                    dsx = dsx.rename(time="wl_time", zos="zosh")
                    dsx["zos"] = (
                        ("time", "latitude", "longitude"),
                        dsx["zosh"].resample(wl_time="24h").mean().data,
                    )
            if dsx is not None:
                dsset[startdates[i]].append(dsx)
            else:
                skipped_list.append(f)

        # Merge the common start_dates first, then concatenate by time afterwards
        dssetm = []
        for v in dsset.values():
            merge_list = []
            for dsx in v:
                # Any other modifications can be added here.
                # None required for Copernicus right now.

                merge_list.append(dsx)
            dssetm.append(xr.merge(merge_list))

        print("Concatenating xarray dataset")
        ds = xr.concat(
            dssetm,
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

        # Interpolate nan gaps (mainly in forecast data)
        # Turned it off; it creates issues with chunked data.
        # It is mainly a problem with HYCOM, not copernicus.
        # ds = ds.interpolate_na(max_gap="24h", dim="time")

        return ds, skipped_list
