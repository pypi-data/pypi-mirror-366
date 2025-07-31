from datetime import datetime
import pandas as pd
from pathlib import Path
from typing import Union


def _parse_date(date: Union[str, datetime, pd.Timestamp]) -> datetime:
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

        try:
            date = datetime.strptime(date, fmt)
        except:
            raise ValueError(f'Failed to convert date `{date}` to a Timestamp, please check format (e.g., YYYY-mm-dd)')
        return date
    
    elif isinstance(date, pd.Timestamp):
        return date.to_pydatetime()
    elif isinstance(date, datetime):
        return date
    else:
        raise ValueError(
            "Date must be a string, datetime, or pandas Timestamp object"
        )

def _parse_path(path: Union[str, Path]) -> Path:
    path = Path(path)
    if path.is_dir():
        return path
    else:
        raise NotADirectoryError(
            f"`{path.as_posix()}` does not exist, please check."
        )