import sys
from pathlib import Path

import pandas as pd
import xarray as xr
import yaml

root = Path(__file__).parent

def _get_config(mode:str, source: str, model=None):
    """Load a data source config file

    Args:
        mode (str): Ocean data type {'ocean', 'wave', 'atmos'}
        source (str): Source e.g {'hycom', 'copernicus'}

    Returns:
        dict: cfg dictionary
        str: Base data source URL (e.g., for THREDDS)
    """
    # Replace the 'default' tag with a None for this check
    model = None if model == 'default' else model
    
    # If there is a model specified, append to filename
    if model is None:
        cfgname = f'{source}.yaml'
    else:
        cfgname = f'{source}_{model}.yaml'
    
    path = root / f"{mode}/cfgs/{cfgname}".lower()
    
    if not path.exists():
        raise ValueError(f'Config file mode {mode} and source/model {cfgname} does not exist! Please review your source / model request')
    
    with open(path) as f:
        cfg = yaml.safe_load(f)
        BASE_URL = cfg.pop("_BASE_URL", None)
        assert BASE_URL, "Please check config file, missing BASE_URL"
        
    return cfg, BASE_URL


def todstr(datetime):
    """Return a YYYYmmdd formatted datestr
    For use in all downloaders and mergers

    Args:
        datetime (pd.Timestamp): Timestamp for conversion

    Returns:
        str: YYYYmmdd format string
    """
    return datetime.strftime("%Y%m%d")

def _check_time_interval(x):
    assert int(x) == float(x), "Timestep unit should be an integer representing hours"
    x = int(x)
    assert (
        x >= 3
    ), "The highest resolution timestep available is 3-hourly output - please check"
    assert (
        x % 3 == 0
    ), "Timestep should be a multiple of 3 (highest available timestep resolution is 3hrly) - please check"
    return x


def _conv_date(date):
    # Convert date-types, if necessary
    if isinstance(date, str):
        if len(date) == 10:
            fmt = "%Y-%m-%d"
        elif len(date) == 13:
            fmt = "%Y-%m-%d %H"
        elif len(date) == 16:
            fmt = "%Y-%m-%d %H:%M"
        elif len(date) == 19:
            fmt = "%Y-%m-%d %H:%M:%S"
        elif len(date) == 8:
            fmt = "%Y%m%d"
        elif len(date) == 15:
            fmt = "%Y%m%d.%H%M%S"
        date = datetime.strptime(date, fmt)
    elif isinstance(date, pd.Timestamp):
        date = date.to_pydatetime()
    return date


def validate_request(
    timelims, xlims, ylims, src_timelims, src_xlims, src_ylims, source_name
):
    """Validate the time range of the source dataset.

    Args:
        timelims (tuple): start and end time of data request.
        xlims (tuple): x limits of the data request
        ylims (tuple): y limits of the data request
        src_timelims (tuple): tuple of start and end timeframes for the dataset.
        src_xlims (tuple): tuple of start and end longitudes for the dataset.
        src_ylims (tuple): tuple of start and end latitudes for the dataset.
        source_name (_type_): data source name
    """
    # Capitalise src name for consistency
    source_name = source_name.upper()

    # Validate time limits
    src_start, src_end = src_timelims

    time_start, time_end = timelims
    if src_start is not None:
        assert time_start >= pd.Timestamp(
            src_start
        ), f"Start time is outside of {source_name} data temporal extents ({src_start} to {src_end})"


    if src_end is not None:
        assert time_end <= pd.Timestamp(
            src_end
        ), f"End time is outside of {source_name} data temporal extents ({src_start} to {src_end})"
    else:
        assert time_end >= pd.Timestamp(
            src_start
        ), f"End time is outside of {source_name} data temporal extents ({src_start} to {src_end})"

    # Validate x limits
    x_start, x_end = xlims
    src_x_start, src_x_end = src_xlims

    if src_x_start is not None:
        assert (
            x_start >= src_x_start
        ), f"x start is outside of {source_name} data spatial extents ({src_x_start} to {src_x_end})"

    if src_x_end is not None:
        assert (
            x_end <= src_x_end
        ), f"x end is outside of {source_name} data spatial extents ({src_x_start} to {src_x_end})"

    # Validate y limits
    y_start, y_end = ylims
    src_y_start, src_y_end = src_ylims

    if src_y_start is not None:
        assert (
            y_start >= src_y_start
        ), f"y start is outside of {source_name} data spatial extents ({src_y_start} to {src_y_end})"

    if src_y_end is not None:
        assert (
            y_end <= src_y_end
        ), f"y end is outside of {source_name} data spatial extents ({src_y_start} to {src_y_end})"


def _open_netcdf_file(file: Path) -> xr.Dataset:
    """Open a subset netcdf file and assert validity

    Args:
        file (Path): path to the netcdf file

    Returns:
        xr.Dataset: Subset netcdf dataset
    """
    try:
        # Attempt to open the file
        ds = xr.open_dataset(file)

        # Check if 'time' is properly formatted
        if pd.api.types.is_datetime64_any_dtype(ds["time"]):
            return ds
        else:
            print(f"Skipping file {file.name} - time error")
            return None
    except Exception as e:
        print(f"Skipping file {file.name}: {str(e)}")
        return None


def wrap_longitude(ds, wrapto360=False, xname="longitude"):
    """Function to wrap a dataset longitude around 360 or 180.
    Defaults to -180 to 180.

    :param ds: dataset to be wrapped
    :param wrapto360: boolean to wrap to 360 (Defaults to False).
    :param xname: X-var name (Defaults to 'longitude')
    :return: ds (xr.Dataset): The wrapped dataset
    """
    attrs = ds[xname].attrs
    if wrapto360 is True:
        x = ds[xname].values
        x[x < 0] = x[x < 0] + 360
    else:
        x = ds[xname].values
        x[x > 180] = x[x > 180] - 360

    ds = ds.assign_coords({xname: x})
    ds = ds.sortby(xname)
    
    # Ensure attributes get copied in correctly
    ds[xname].attrs = attrs
    
    return ds


def check_path(path):
    # Convert str path to Pathlib; assert existence.
    if isinstance(path, str):
        path = Path(path)

    if path.is_dir():
        return path
    else:
        assert False, f"{path.as_posix()} is not a valid path - check that it exists"


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
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
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def is_notebook() -> bool:
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter
