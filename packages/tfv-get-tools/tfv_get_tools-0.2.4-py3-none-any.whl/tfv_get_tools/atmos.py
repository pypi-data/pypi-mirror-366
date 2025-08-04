from datetime import datetime
from pathlib import Path
from typing import Union, Tuple, Optional, List
import pandas as pd
from tfv_get_tools.providers._downloader import BatchDownloadResult


def DownloadAtmos(
    start_date: Union[str, datetime, pd.Timestamp],
    end_date: Union[str, datetime, pd.Timestamp],
    xlims: Tuple[float, float],
    ylims: Tuple[float, float],
    out_path: Union[str, Path] = Path("./raw"),
    source: str = "ERA5",
    model: str = "default",
    prefix: Optional[str] = None,
    verbose: bool = False,
    variables: Optional[List[str]] = None,
    skip_check: bool = False,
    **kwargs,
) -> BatchDownloadResult:
    """Download Atmospheric Data - the proper user-facing API
    
    Users should call this function, not the individual downloader classes directly.
    
    Args:
        start_date: Start date
        end_date: End date  
        xlims: Longitude bounds
        ylims: Latitude bounds
        out_path: Output directory
        source: Data source ('ERA5', 'CFSR', 'BARRA2')
        model: Model variant
        prefix: File prefix
        verbose: Verbose output
        variables: Custom variables to download
        skip_check: Skip user confirmation
        **kwargs: Additional arguments
        
    Returns:
        BatchDownloadResult: Results of the download operation
    """
    
    if source.lower() == "cfsr":
        from tfv_get_tools.providers.atmos.cfsr import DownloadCFSRAtmos
        
        downloader = DownloadCFSRAtmos(
            start_date=start_date,
            end_date=end_date,
            xlims=xlims,
            ylims=ylims,
            out_path=out_path,
            model=model,
            prefix=prefix,
            verbose=verbose,
            variables=variables,
            skip_check=skip_check,
            **kwargs
        )
        return downloader.execute_download()
    
    elif source.lower() == "era5":
        from tfv_get_tools.providers.atmos.era5 import DownloadERA5Atmos
        
        downloader = DownloadERA5Atmos(
            start_date=start_date,
            end_date=end_date,
            xlims=xlims,
            ylims=ylims,
            out_path=out_path,
            model=model,
            prefix=prefix,
            verbose=verbose,
            variables=variables,
            skip_check=skip_check,
            **kwargs
        )
        return downloader.execute_download()
        
    elif source.lower() == "barra2":
        from tfv_get_tools.providers.atmos.barra2 import DownloadBARRA2
        
        downloader = DownloadBARRA2(
            start_date=start_date,
            end_date=end_date,
            xlims=xlims,
            ylims=ylims,
            out_path=out_path,
            model=model,
            prefix=prefix,
            verbose=verbose,
            variables=variables,
            skip_check=skip_check,
            **kwargs
        )
        return downloader.execute_download()
        
    else:
        raise ValueError(f'Unrecognised source {source}. Must be one of: CFSR, ERA5, BARRA2')


def MergeAtmos(
    in_path: Path = Path("./raw"),
    out_path: Path = Path("."),
    fname: str = None,
    source: str = 'ERA5',
    model: str = 'default',
    time_start: str = None,
    time_end: str = None,
    reproject: int = None,
    local_tz: Tuple[float, str] = None,
    pad_dry: bool = False,
    wrapto360: bool = False,
    write: bool = True,
):
    """
    Merge raw downloaded atmos datafiles into a single netcdf file. 
    
    **Use the same `source` and `model` that was supplied to the Downloader function**

    Args:
        in_path (Path, optional): Directory of the raw ocean data-files. Defaults to Path(".").
        out_path (Path, optional): Output directory for the merged ocean netcdf and (opt) the fvc. Defaults to Path(".").
        fname (str, optional): Merged ocean netcdf filename. Defaults to None.
        source (str, optional): Source to be merged, defaults to "ERA5". 
        model (str, optional): Model for source to be merged. Defaults are listed in the wiki documentation.
        time_start (str, optional): Start time limit of the merged dataset (str: "YYYY-mm-dd HH:MM"). Defaults to None.
        time_end (str, optional): End time limit of the merged dataset (str: "YYYY-mm-dd HH:MM"). Defaults to None.
        reproject (int, optional): Optionally reproject based, based on EPSG code. Defaults to None.
        local_tz: (Tuple(float, str): optional): Add local timezone format is a tuple with Offset[float] and Label[str]
        pad_dry: (bool, optional): Optionally pad landwards (i.e., fill nans horizontally). Defaults to False.
        wrapto360: (bool, optional): Optionally wrap longitude to (0, 360) rather than (-180, 180). Defaults to False.
        write (bool): Write the dataset. If False, the virtual merged dataset will be returned.
    """
    
    args = tuple()

    kwargs = dict(
        in_path=in_path,
        out_path=out_path,
        fname=fname,
        source=source,
        model=model,
        time_start=time_start,
        time_end=time_end,
        reproject=reproject,
        local_tz=local_tz,
        pad_dry=pad_dry,
        wrapto360=wrapto360,
        write=write,
    )
    
    if source.lower() == "era5":
        from tfv_get_tools.providers.atmos.era5 import MergeERA5Atmos
        mrg = MergeERA5Atmos(*args, **kwargs)
    
    elif source.lower() == "cfsr":
        from tfv_get_tools.providers.atmos.cfsr import MergeCFSRAtmos
        mrg = MergeCFSRAtmos(*args, **kwargs)

    elif source.lower() == "barra2":
        from tfv_get_tools.providers.atmos.barra2 import MergeBARRA2
        mrg = MergeBARRA2(*args, **kwargs)

    # If the user requested no-write, return the dataset object.
    if not write:
        return mrg.ds