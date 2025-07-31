import xarray as xr
import pandas as pd
from pathlib import Path
import numpy as np


def write_tuflowfv_fvc(
    ds: xr.Dataset,
    fname: str,
    out_path: Path,
    reproject=False,
    local_time=False,
    var_order=["surf_el", "water_u", "water_v", "salinity", "water_temp"],
):
    """Write a tuflow-fv .fvc file to accompany the merged dataset

    Args:
        ds (xr.Dataset): merged barra dataset to supply headers
        fname (str): the filename of the .nc merged dataset
        out_path (Path): output directory
    """

    # Check to see if ds has been reprojected. Use x/y if so.
    if reproject:
        xvar = "x"
        yvar = "y"
    else:
        xvar = "longitude"
        yvar = "latitude"

    # Check to see if local_time has been added - use local_time if so.
    if local_time:
        time = "local_time"
    else:
        time = "time"

    xlims = ", ".join([f"{fn(ds[xvar].values):0.4f}" for fn in [np.min, np.max]])
    ylims = ", ".join([f"{fn(ds[yvar].values):0.4f}" for fn in [np.min, np.max]])

    vlist = ",".join(var_order)

    nc_path = (out_path / fname).as_posix()
    fname_fvc = fname.replace(".nc", ".fvc")
    with open(out_path / fname_fvc, "w") as f:
        f.write("! TUFLOW-FV FVC File for Ocean Dataset\n")
        f.write("! Written by `get_ocean`\n")
        f.write("\n")
        f.write(f"! Netcdf start time: {ds_time_to_str(ds, 0)}\n")
        f.write(f"! Netcdf end time: {ds_time_to_str(ds, -1)}\n")
        f.write(f"! Netcdf x-limits: {xlims}\n")
        f.write(f"! Netcdf y-limits: {ylims}\n")
        f.write("\n")

        # Grid def block
        f.write(f"grid definition file == {nc_path}\n")
        f.write(f"  grid definition variables == {xvar}, {yvar}, depth\n")
        f.write("  grid definition label == ocean\n")
        f.write("  boundary gridmap == 1\n")
        f.write("end grid\n")
        f.write("\n")

        f.write(f"bc == OBC_GRID, ocean, {nc_path}\n")
        f.write(f"  bc nodestrings == #  ! Please supply open boundary ns list\n")
        f.write("  sub-type == 6\n")
        f.write(f"  bc header == {time},{vlist}\n")
        f.write("  bc update dt == 900.\n")
        f.write("  bc time units == hours\n")
        f.write("  bc reference time == 01/01/1990 00:00\n")
        f.write("  bc offset == -0.5, 0.0, 0.0, 0.0, 0.0   ! Replace -0.5 with relevant surf-el offset\n")
        f.write("  bc default == NaN\n")
        f.write("  vertical coordinate type == depth\n")

        f.write("end bc\n")
        f.write("\n")


def ds_time_to_str(ds: xr.Dataset, i: int, fmt="%Y-%m-%d %H:%M") -> str:
    return pd.Timestamp(ds.time[i].values).strftime(fmt)
