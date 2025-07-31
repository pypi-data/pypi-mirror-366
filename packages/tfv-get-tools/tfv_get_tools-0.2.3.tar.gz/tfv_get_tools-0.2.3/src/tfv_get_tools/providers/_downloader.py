"""
Base Downloader class - this is the base class for all downloaders.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import sys

import pandas as pd
from pandas.tseries.offsets import MonthBegin, MonthEnd

from tfv_get_tools.providers._utilities import _get_config
from tfv_get_tools.utilities.parsers import _parse_date, _parse_path


class DownloadStatus(Enum):
    """Status codes for download operations"""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PARTIAL = "partial"


@dataclass
class FileDownloadResult:
    """Result for a single file download operation"""

    status: DownloadStatus
    file_path: Optional[Path] = None
    url: Optional[str] = None
    timestamp: Optional[pd.Timestamp] = None
    variable: Optional[str] = None
    message: Optional[str] = None
    error: Optional[Exception] = None
    bytes_downloaded: Optional[int] = None
    duration_seconds: Optional[float] = None

    @property
    def success(self) -> bool:
        return self.status == DownloadStatus.SUCCESS

    @property
    def failed(self) -> bool:
        return self.status == DownloadStatus.FAILED


@dataclass
class BatchDownloadResult:
    """Result for a batch download operation (multiple files)"""

    results: List[FileDownloadResult] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def add_result(self, result: FileDownloadResult) -> None:
        """Add a file download result to the batch"""
        self.results.append(result)

    @property
    def total_files(self) -> int:
        return len(self.results)

    @property
    def successful_files(self) -> List[FileDownloadResult]:
        return [r for r in self.results if r.success]

    @property
    def failed_files(self) -> List[FileDownloadResult]:
        return [r for r in self.results if r.failed]

    @property
    def skipped_files(self) -> List[FileDownloadResult]:
        return [r for r in self.results if r.status == DownloadStatus.SKIPPED]

    @property
    def success_rate(self) -> float:
        """Return success rate as percentage"""
        if self.total_files == 0:
            return 0.0
        return (len(self.successful_files) / self.total_files) * 100

    @property
    def summary(self) -> Dict[str, int]:
        """Get summary counts of each status"""
        summary = {}
        for status in DownloadStatus:
            summary[status.value] = len([r for r in self.results if r.status == status])
        return summary

    @property
    def total_bytes_downloaded(self) -> int:
        """Total bytes downloaded across all successful files"""
        return sum(r.bytes_downloaded or 0 for r in self.successful_files)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Total duration of the batch download"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class BaseDownloader(ABC):
    """Base class for downloader"""

    def __init__(
        self,
        start_date: Union[str, datetime, pd.Timestamp],
        end_date: Union[str, datetime, pd.Timestamp],
        xlims: Tuple[float, float],
        ylims: Tuple[float, float],
        zlims: Optional[Tuple[float, float]] = None,
        out_path: Union[str, Path] = Path("./raw"),
        model: Optional[str] = "default",
        prefix: Optional[str] = None,
        time_interval: Optional[Union[int, str]] = 24,
        verbose: bool = False,
        variables: Optional[List[str]] = None,
        skip_check: bool = False,
        **kwargs,
    ):
        """Initialise the BaseDownloader class"""
        self.start_date = _parse_date(start_date)
        self.end_date = _parse_date(end_date)

        if "output_directory" in kwargs:
            out_path = kwargs.pop("output_directory", "./raw")
            print(
                "Warning - the `output_directory` keyword argument has been replaced by `out_path`"
            )
            print(f"...Setting `out_path={out_path}")

        elif "outdir" in kwargs:
            out_path = kwargs.pop("outdir", "./raw")
            print(
                "Warning - the `outdir` keyword argument has been replaced by `out_path`"
            )
            print(f"...Setting `out_path={out_path}")

        self.outdir = _parse_path(out_path)

        self.xlims = self._validate_coords(xlims)
        self.ylims = self._validate_coords(ylims)

        # Validate zlim input if provided
        if zlims is not None:
            self.zlims = self._validate_coords(zlims)
        else:
            self.zlims = None

        self.time_interval = self._validate_time_interval(time_interval)

        self.prefix = prefix
        self.verbose = verbose
        self.skip_check = skip_check

        # Flag to download custom variables or not.
        self._custom_variables = True if variables else False
        self.variables = variables

        self.max_tries = 5
        self.timeout = 30

        # Track download results
        self._batch_result = BatchDownloadResult()

        # These are filled in the individual downloaders!
        # We'll init them here for reference.
        # Mode attribute e.g. {'ocean', 'wave'}
        # Source attribute e.g {'hycom', 'cawcr'}
        self.mode = None
        self.source = None
        self.model = model if model else "default"

        # Testing mode - run program but don't ever call the final API
        self.__test_mode__ = kwargs.pop("TEST_MODE", False)

        # Now we call the source specific init, which loads the source config `self.cfg`
        self._init_specific(**kwargs)

    @abstractmethod
    def _init_specific(self, **kwargs):
        """Initialize source specific attributes"""
        pass

    def prepare_request(self):
        """Prepare attributes including
        - Dataset id mapping (for sequential sources like copernicus, hycom)
        - Download interval and times (source specific)
        - Filename prefixes (source_mode + _model if relevant)
        - Default variables, if custom aren't requested.
        """
        self.dsmap = self.cfg["_DATASETS"]
        self.database = "N/A"  # Init for sources with sequential databases

        # Assign a download interval, monthly or daily.
        if self.cfg["_DOWNLOAD_INTERVAL"] == "daily":
            self.download_interval = "d"
        elif self.cfg["_DOWNLOAD_INTERVAL"] == "monthly":
            self.download_interval = "MS"
        else:
            raise ValueError('_DOWNLOAD_INTERVAL must be one of {"daily", "monthly"}')

        # Times to download (start times)
        if self.start_date.day == 1:
            ts = self.start_date
        elif (self.start_date.day != 1) & (self.cfg["_DOWNLOAD_INTERVAL"] == "monthly"):
            ts = self.start_date + MonthBegin(-1)
        else:
            # For daily downloaded data, it can be whatever.
            ts = self.start_date

        self.times = pd.date_range(ts, self.end_date, freq=self.download_interval)

        # Assign the default variables if no custom ones are requested.
        if not self._custom_variables:
            self.variables = self.cfg["_VARIABLES"]

        # Set the prefix.
        # Only append model if not 'default'
        if self.model == "default":
            fname = f"{self.source}_{self.mode}".upper()
        else:
            fname = f"{self.source}_{self.mode}_{self.model}".upper()

        if self.prefix is None:
            self.prefix = fname
        else:
            self.prefix = self.prefix + "_" + fname

        # Assign zlims for the source, if they were not provided
        if (self.mode == "OCEAN") & (self.zlims is None):
            self.zlims = self.cfg["_SOURCE_ZLIMS"]

        # Finally, validate the request now everything has been set
        src_xlims = self.cfg.pop("_SOURCE_XLIMS", (None, None))
        src_ylims = self.cfg.pop("_SOURCE_YLIMS", (None, None))
        src_zlims = self.cfg.pop("_SOURCE_ZLIMS", (None, None))
        src_timelims = self.cfg.pop("_SOURCE_TIMELIMS", (None, None))

        if self.model == "default":
            src_name = self.source
        else:
            src_name = f"{self.source}_{self.model}"

        self._validate_request_bounds(
            (self.start_date, self.end_date),
            self.xlims,
            self.ylims,
            self.zlims,
            src_timelims,
            src_xlims,
            src_ylims,
            src_zlims,
            src_name,
        )

    def check_request(self):
        """Print out a verbose confirmation of the user request"""
        # Print request
        fmt = "%Y-%m-%d"
        print(
            f"This request involves collection of approx. {len(self.times)} time intervals of {self.source.upper()} {self.mode} data"
        )
        print(f"Files are downloaded in {self.cfg['_DOWNLOAD_INTERVAL']} increments")

        # Note for HYCOM about missing days
        if self.source.lower() == "hycom":
            print(
                "Note that this tool does not replace missing days in the HYCOM database"
            )
            print(
                f"HYCOM data will be exported daily with a {self.time_interval}-hourly timestep"
            )

        # Note for monthly interval datasets when user didn't specify first day of the month
        if self.download_interval == "MS":
            if self.start_date != self.times[0]:
                print(
                    "Note: This data source is downloaded in monthly increments. The start date has been rounded."
                )
            if self.end_date != self.times[-1]:
                print(
                    "Note: This data source is downloaded in monthly increments. The end date has been rounded."
                )

        ts = self.times[0]
        if self.download_interval == "MS":
            te = self.times[-1] + MonthEnd(1)
        else:
            te = self.times[-1]

        print("--------------------")
        print("Confirming Request:")
        print(f"... xLims: {self.xlims}")
        print(f"... yLims: {self.ylims}")
        if self.mode.lower() == "ocean":
            print(f"... zLims: {self.zlims}")
        print(f"... Dates: {ts.strftime(fmt)} to {te.strftime(fmt)}")
        print(f"... Model: {self.model}")
        print(f"... Outdir: {self.outdir.as_posix()}")

        print("\n")

    @abstractmethod
    def download(self):
        """Source-specific download implementation
        Must yield download tasks
        """
        pass

    def execute_download(self) -> BatchDownloadResult:
        """Execute download with progress tracking and error handling"""
        self.prepare_request()
        self.check_request()

        if self.__test_mode__:
            # In test mode, skip the confirmation
            return self._perform_downloads()
        else:
            # Confirm y/n or let it rip
            if self.skip_check:
                return self._perform_downloads()
            else:
                if self._query_yes_no("Do you want to continue?"):
                    return self._perform_downloads()
                else:
                    self.log("Finished")
                    return BatchDownloadResult()

    def _perform_downloads(self) -> BatchDownloadResult:
        """Handle the common download workflow - all sources yield tasks"""
        from time import time
        from tqdm import tqdm

        batch_result = BatchDownloadResult()
        batch_result.start_time = datetime.now()

        # All sources now yield tasks
        download_tasks = list(self.download())

        # Count existing files for progress bar
        existing_count = sum(1 for task in download_tasks if task["file_path"].exists())

        # Set up progress bar
        progress_bar = tqdm(
            initial=existing_count, total=len(download_tasks), unit="file"
        )

        # Process each download task
        for task in download_tasks:
            result = self._process_single_download(task, progress_bar)
            batch_result.add_result(result)

        progress_bar.close()
        batch_result.end_time = datetime.now()

        self._log_download_summary(batch_result)
        return batch_result

    def _process_single_download(self, task: dict, progress_bar) -> FileDownloadResult:
        """Process a single download task"""
        from time import time

        file_path = task["file_path"]
        url = task.get("url", "N/A")  # Some sources don't use URLs
        timestamp = task["timestamp"]
        variable = task.get("variable", "unknown")
        download_func = task["download_func"]

        # Check if file already exists
        if file_path.exists():
            if self.verbose:
                self.log(f"{file_path.name} already exists! Moving on...")

            return FileDownloadResult(
                status=DownloadStatus.SKIPPED,
                file_path=file_path,
                timestamp=timestamp,
                variable=variable,
                message="File already exists",
            )

        # Perform the download
        start_time = time()

        if self.verbose:
            if url != "N/A":
                self.log(f"Fetching data for {timestamp} from {url}")
            else:
                self.log(f"Fetching data for {timestamp} via API")

        try:
            if not self.__test_mode__:
                success = download_func()
            else:
                success = True  # Simulate success in test mode

            duration = time() - start_time

            if success:
                file_size = file_path.stat().st_size if file_path.exists() else None

                progress_bar.set_postfix(
                    last_downloaded=timestamp.strftime("%Y-%m-%d"), refresh=False
                )
                progress_bar.update()

                return FileDownloadResult(
                    status=DownloadStatus.SUCCESS,
                    file_path=file_path,
                    url=url,
                    timestamp=timestamp,
                    variable=variable,
                    message=f"Downloaded successfully in {duration:.2f}s",
                    bytes_downloaded=file_size,
                    duration_seconds=duration,
                )
            else:
                return FileDownloadResult(
                    status=DownloadStatus.FAILED,
                    file_path=file_path,
                    url=url,
                    timestamp=timestamp,
                    variable=variable,
                    message="Download function returned False",
                    duration_seconds=duration,
                )

        except Exception as e:
            duration = time() - start_time
            return FileDownloadResult(
                status=DownloadStatus.FAILED,
                file_path=file_path,
                url=url,
                timestamp=timestamp,
                variable=variable,
                message=f"Exception during download: {str(e)}",
                error=e,
                duration_seconds=duration,
            )

    def _log_download_summary(self, batch_result: BatchDownloadResult) -> None:
        """Log a summary of the download batch results"""
        print("\n" + "=" * 50)
        print("DOWNLOAD SUMMARY")
        print("=" * 50)

        summary = batch_result.summary
        print(f"Total files processed: {batch_result.total_files}")
        print(f"Successful downloads: {summary['success']}")
        print(f"Failed downloads: {summary['failed']}")
        print(f"Skipped (existing): {summary['skipped']}")
        print(f"Success rate: {batch_result.success_rate:.1f}%")

        if batch_result.total_bytes_downloaded > 0:
            size_mb = batch_result.total_bytes_downloaded / (1024 * 1024)
            print(f"Total data downloaded: {size_mb:.2f} MB")

        if batch_result.duration_seconds:
            print(f"Total duration: {batch_result.duration_seconds:.2f} seconds")

        # List failed files if any
        if batch_result.failed_files:
            print(f"\nFailed downloads ({len(batch_result.failed_files)}):")
            for failed_result in batch_result.failed_files:
                print(f"  • {failed_result.file_path.name}: {failed_result.message}")

        print("=" * 50)

    def log(self, message: str):
        if self.verbose:
            print(message)

    def _load_config(self):
        cfg, base_url = _get_config(self.mode, self.source, self.model)

        self.cfg = cfg
        self.base_url = base_url

    @staticmethod
    def _validate_coords(coords: Tuple[float, float]) -> Tuple[float, float]:
        if not isinstance(coords, tuple) or len(coords) != 2:
            raise ValueError("Coordinates must be a tuple of two floats")
        return tuple(float(c) for c in coords)

    @staticmethod
    def _validate_time_interval(interval: int) -> int:
        valid_intervals = [3, 6, 12, 24, "best"]
        if interval not in valid_intervals:
            raise ValueError(f"Invalid time interval. Must be one of {valid_intervals}")
        return interval

    @staticmethod
    def _validate_request_bounds(
        timelims,
        xlims,
        ylims,
        zlims,
        src_timelims,
        src_xlims,
        src_ylims,
        src_zlims,
        source_name,
    ):
        """
        Validate that the requested coordinates and time range fall within the dataset's limits.
        """
        source_name = source_name.upper()

        def check_bounds(name, req_start, req_end, src_start, src_end):
            if src_start is not None and req_start < src_start:
                raise ValueError(
                    f"{name} start ({req_start}) is below {source_name} data extent ({src_start} to {src_end})"
                )
            if src_end is not None and req_end > src_end:
                raise ValueError(
                    f"{name} end ({req_end}) is above {source_name} data extent ({src_start} to {src_end})"
                )

        # Validate time limits
        check_bounds(
            "Time",
            pd.Timestamp(timelims[0]),
            pd.Timestamp(timelims[1]),
            pd.Timestamp(src_timelims[0]) if src_timelims[0] else None,
            pd.Timestamp(src_timelims[1]) if src_timelims[1] else None,
        )

        # Validate spatial limits
        check_bounds("X", xlims[0], xlims[1], src_xlims[0], src_xlims[1])
        check_bounds("Y", ylims[0], ylims[1], src_ylims[0], src_ylims[1])

        # Validate Z limits if provided
        if zlims and src_zlims:
            check_bounds("Z", zlims[0], zlims[1], src_zlims[0], src_zlims[1])

    @staticmethod
    def _query_yes_no(question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer."""
        valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == "":
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write(
                    "Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n"
                )
