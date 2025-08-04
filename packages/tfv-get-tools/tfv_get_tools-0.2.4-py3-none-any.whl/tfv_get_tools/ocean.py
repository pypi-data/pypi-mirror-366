from datetime import datetime
from pathlib import Path
from typing import Union, Tuple, Optional, List, Literal
import pandas as pd

from tfv_get_tools.utilities._tfv_bc import write_tuflowfv_fvc
from tfv_get_tools.providers._downloader import BatchDownloadResult


def DownloadOcean(
    start_date: Union[str, datetime, pd.Timestamp],
    end_date: Union[str, datetime, pd.Timestamp],
    xlims: Tuple[float, float],
    ylims: Tuple[float, float],
    zlims: Optional[Tuple[float, float]] = None,
    out_path: Union[str, Path] = Path("./raw"),
    source: str = "HYCOM",
    model: str = "default",
    prefix: Optional[str] = None,
    verbose: bool = False,
    variables: Optional[List[str]] = None,
    time_interval: Union[int, Literal["best"]] = 24,
    skip_check: bool = False,
    **kwargs,
) -> BatchDownloadResult:
    """Download Ocean Data
    
    Users should call this function, not the individual downloader classes directly.
    
    This module will download ocean data from several possible sources to facilitate 
    TUFLOW FV and SWAN modelling.

    The following sources have been implemented:
        - `HYCOM` - Naval Research Laboratory - Global Ocean Forecast System (GOFS) 3.1
        - `Copernicus` - Various models from the Copernicus Marine Service
            - `GLO` - Global model domain

    Args:
        start_date: Start date. The string format is `%Y-%m-%d` (e.g., '2011-01-01')
        end_date: End date. The string format is `%Y-%m-%d` (e.g., '2011-02-01')
        xlims: Minimum and maximum longitude, as floats. e.g., (115, 120)
        ylims: Minimum and maximum latitude, as floats. e.g., (-40, -35)
        zlims: Minimum and maximum depth, as floats. e.g., (50, 250). 
            Defaults to the maximum per data source.
        out_path: Output directory for data files
        source: Data source to download. One of {'HYCOM', 'Copernicus'}
        model: Choice of model, depending on "source"
        prefix: Extra file name prefix
        verbose: Print extra program information
        variables: List of variables to download (surf_el, salinity, water_temp, water_u, water_v)
        time_interval: Time interval in hours for HYCOM only. Defaults to 24. Use "best" for the highest available. 
        skip_check: Skip user confirmation
        **kwargs: Additional arguments
        
    Returns:
        BatchDownloadResult: Results of the download operation
    """
    
    if source.lower() == "hycom":
        from tfv_get_tools.providers.ocean.hycom import DownloadHycom
        
        downloader = DownloadHycom(
            start_date=start_date,
            end_date=end_date,
            xlims=xlims,
            ylims=ylims,
            zlims=zlims,
            out_path=out_path,
            model=model,
            prefix=prefix,
            time_interval=time_interval,
            verbose=verbose,
            variables=variables,
            skip_check=skip_check,
            **kwargs
        )
        
        return downloader.execute_download()
    
    elif source.lower() == "copernicus":
        from tfv_get_tools.providers.ocean.copernicus_ocean import DownloadCopernicusOcean
        
        downloader = DownloadCopernicusOcean(
            start_date=start_date,
            end_date=end_date,
            xlims=xlims,
            ylims=ylims,
            zlims=zlims,
            out_path=out_path,
            model=model,
            prefix=prefix,
            time_interval=time_interval,
            verbose=verbose,
            variables=variables,
            skip_check=skip_check,
            **kwargs
        )
        
        return downloader.execute_download()
        
    else:
        raise ValueError(f'Unrecognised source {source}. Must be one of: HYCOM, Copernicus')


def MergeOcean(
    in_path: Path = Path("./raw"),
    out_path: Path = Path("."),
    source: str = 'HYCOM',
    model: str = 'default',
    fname: str = None,
    time_start: str = None,
    time_end: str = None,
    write_fvc=True,
    reproject: int = None,
    local_tz: Tuple[float, str] = None,
    pad_dry: bool = False,
    wrapto360=False,
    write=True,
):
    """
    Merge raw downloaded ocean datafiles into a single netcdf file, ready for TUFLOW-FV modelling
    Optionally create an accompanying .fvc file.

    **Use the same `source` and `model` that was supplied to the Downloader function**

    Args:
        in_path (Path, optional): Directory of the raw ocean data-files. Defaults to Path(".").
        out_path (Path, optional): Output directory for the merged ocean netcdf and (opt) the fvc. Defaults to Path(".").
        fname (str, optional): Merged ocean netcdf filename. Defaults to None.
        source (str, optional): Source to be merged. Defaults to HYCOM.
        model (str, optional): Model for source to be merged. Defaults to 'default'.
        time_start (str, optional): Start time limit of the merged dataset (str: "YYYY-mm-dd HH:MM"). Defaults to None.
        time_end (str, optional): End time limit of the merged dataset (str: "YYYY-mm-dd HH:MM"). Defaults to None.
        write_fvc (bool, optional): Optionally write an accompanying .fvc file. Defaults to True.
        reproject (int, optional): Optionally reproject based, based on EPSG code. Defaults to None.
        local_tz: (Tuple(float, str): optional): Add local timezone format is a tuple with Offset[float] and Label[str]
        pad_dry: (bool, optional): Optionally pad horizontally (i.e., fill nans with respect to depth). Defaults to False.
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
        # write_fvc=write_fvc,
        reproject=reproject,
        local_tz=local_tz,
        pad_dry=pad_dry,
        wrapto360=wrapto360,
        write=write,
    )

    if source.lower() == "hycom":
        from tfv_get_tools.providers.ocean.hycom import MergeHYCOM
        mrg = MergeHYCOM(*args, **kwargs)
    
    elif source.lower() == "copernicus":
        from tfv_get_tools.providers.ocean.copernicus_ocean import MergeCopernicusOcean
        mrg = MergeCopernicusOcean(*args, **kwargs)
    
    # If the user requested no-write, return the dataset object.
    if not write:
        return mrg.ds