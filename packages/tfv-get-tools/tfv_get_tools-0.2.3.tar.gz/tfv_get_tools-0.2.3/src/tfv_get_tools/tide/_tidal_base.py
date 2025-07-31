"""
GetTide. Only supports FES2014 and FES2022.
"""

from datetime import datetime, timedelta
from pathlib import Path
import pickle
import os
from typing import Union, Tuple, Optional

import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
from tqdm.auto import tqdm
from shapely import LineString
from pyproj import Geod, CRS

# Import the tidal prediction, pyTMD
import pyTMD
from pyTMD.io.FES import extract_constants as extract_FES_constants
from pyTMD.predict import time_series as predict_tidal_ts
from tfv_get_tools.utilities.parsers import _parse_date, _parse_path
from tfv_get_tools.utilities.warnings import deprecated
from tfv_get_tools.tide._nodestring import (
    load_nodestring_shapefile,
    process_nodestring_gdf,
)
from tfv_get_tools.fvc import write_tide_fvc

crs = CRS.from_epsg(4326)


class TidalExtractor:
    """Wrapper for PyTMD operations to enable testing."""

    def extract_fes_constants(self, coords, files, source, interpolate_method):
        """Extract FES constants - wrapped for testing."""
        return extract_FES_constants(
            coords[:, 0],
            coords[:, 1],
            files,
            TYPE="z",
            VERSION=source,
            METHOD=interpolate_method,
            GZIP=False,
            SCALE=1.0 / 100.0,
        )

    def predict_tidal_timeseries(self, tvec, hc, cons):
        """Predict tidal timeseries - wrapped for testing."""
        return predict_tidal_ts(tvec, hc, cons, corrections="FES")


# Default extractor instance
_default_extractor = TidalExtractor()


def _detect_tide_model_source(model_dir: Path):
    """Detect tidal model source based on model_dir."""
    original_model_dir = model_dir
    name = model_dir.name
    if name == "ocean_tide":
        model_dir = (model_dir / "..").resolve()
        name = model_dir.name

    if "fes2014" in name.lower():
        source = "FES2014"  # Return uppercase to match VALID_SOURCES
    elif "fes2022" in name.lower():
        source = "FES2022"  # Return uppercase to match VALID_SOURCES
    else:
        source = None

    # Return the resolved model_dir only if we actually resolved it
    if original_model_dir.name == "ocean_tide":
        return source, model_dir
    else:
        return source, original_model_dir


def _get_model_dir(source="FES2014", model_dir: Union[str, Path] = None) -> Path:
    """Get and validate model directory."""
    VALID_SOURCES = {"FES2014", "FES2022"}

    if source not in VALID_SOURCES:
        raise ValueError(
            f"Requested source {source} not supported. "
            f"Valid sources: {VALID_SOURCES}"
        )

    if model_dir is None:
        env = f"{source}_DIR"
        if env not in os.environ:
            raise ValueError(
                f"The {env} root directory needs to be supplied, either as "
                f"`model_dir` variable, or as environment variable '{env}'"
            )
        model_dir = os.environ[env]

    model_dir = Path(model_dir)

    if not model_dir.exists():
        raise FileNotFoundError(
            f"{source} model directory ({model_dir.as_posix()}) does not exist"
        )

    return model_dir


def _get_chainage_array(array: np.ndarray):
    """Calculate chainage from coordinates."""
    geod = Geod(ellps="WGS84")
    numCoords = array.shape[0] - 1
    geo = LineString(array)

    stf = 0
    for i in range(0, numCoords):
        point1 = geo.coords[i]
        point2 = geo.coords[i + 1]
        _, _, dist = geod.inv(point1[0], point1[1], point2[0], point2[1])
        stf += dist

    nx = len(geo.xy[0])
    incr = stf / (nx - 1)
    chainage = [incr * x for x in range(1, nx)]
    chainage.insert(0, 0)

    return chainage, nx


def _check_coords(coords):
    """Validate coordinate format."""
    if not isinstance(coords, np.ndarray):
        coords = np.asarray(coords)

        if len(coords.shape) == 1:
            coords = coords.reshape([1, 2])

    if coords.shape[1] != 2:
        raise ValueError(
            "Coordinates should be Nx2 format or tuple/list for single location (x, y)"
        )

    return coords


def _normalise_coordinates(coordinates: Union[tuple, np.ndarray, dict]) -> dict:
    """Convert coordinates to consistent dict format."""
    if isinstance(coordinates, tuple):
        if len(coordinates) != 2:
            raise ValueError("Tuple coordinates must be (lon, lat)")
        return {1: np.asarray(coordinates)[None, :]}

    elif isinstance(coordinates, np.ndarray):
        if coordinates.shape[1] != 2:
            raise ValueError("Array coordinates must be Nx2")
        return {1: coordinates}

    elif isinstance(coordinates, dict):
        if len(coordinates) == 0:
            raise ValueError("No coordinates provided")
        return coordinates

    else:
        raise ValueError("Unsupported coordinate format")


def get_constituents(
    coordinates: Union[tuple, np.ndarray, dict],
    model_dir: Union[str, Path] = None,
    interpolate_method="spline",
    save_cons: Union[str, Path] = None,
    source="FES2014",
    extractor=None,
):
    """Get tidal constituents."""
    if extractor is None:
        extractor = _default_extractor

    coordinates = _normalise_coordinates(coordinates)

    cons_dict = dict()
    for bnd_id, coords in coordinates.items():
        coords = _check_coords(coords)

        if coords.shape[0] > 1:
            chainage, nx = _get_chainage_array(coords)
        else:
            chainage = 0
            nx = 1

        model_dir = _get_model_dir(source, model_dir)
        srcdir = model_dir / ".."

        files = [x for x in model_dir.rglob("*.nc")]
        file_cons = [f.stem for f in files]
        files = [files[i] for i in np.argsort(file_cons)]

        model = pyTMD.io.model(srcdir).elevation(source)
        cons = model.constituents

        if source in ("FES2014", "FES2022"):
            if len(files) != 34:
                raise ValueError(f"Cannot find 34 .nc files for {source}")

        print("... extracting constituents from database")

        amp, ph = extractor.extract_fes_constants(
            coords, files, source, interpolate_method
        )

        cons_dict[bnd_id] = dict(
            cons=(amp, ph, cons), geo=(coords, chainage, nx), source=source
        )

    if save_cons:
        with open(save_cons, "wb") as f:
            pickle.dump(cons_dict, f)

    return cons_dict


def predict_waterlevel_timeseries(
    time_start: Union[str, pd.Timestamp, datetime],
    time_end: Union[str, pd.Timestamp, datetime],
    freq: Union[str, pd.Timedelta, timedelta] = "15min",
    coords: Union[tuple, np.ndarray, dict] = None,
    source: str = "FES2014",
    model_dir: Union[str, Path] = None,
    interpolate_method: str = "spline",
    constituents: Union[dict, str, Path] = None,
    extractor=None,
):
    """Extract tidal waterlevels for coordinates."""
    if extractor is None:
        extractor = _default_extractor

    timevec = pd.date_range(
        start=pd.Timestamp(time_start),
        end=pd.Timestamp(time_end),
        freq=freq,
    )

    ref_date = pd.Timestamp(1992, 1, 1)
    tvec = (timevec - ref_date).to_numpy().astype(float) / (10**9 * 60 * 60 * 24)

    # Load constituents if needed
    if constituents is None:
        if coords is None:
            raise ValueError("Either coords or constituents must be provided")
        constituents = get_constituents(
            coords,
            model_dir,
            source=source,
            interpolate_method=interpolate_method,
            extractor=extractor,
        )
    else:
        if not isinstance(constituents, dict):
            constituents = Path(constituents)
            if not constituents.exists():
                raise FileNotFoundError(f"Constituents file not found: {constituents}")

            with open(constituents, "rb") as f:
                constituents = pickle.load(f)

    dsset = {}
    for label, dat in constituents.items():
        (amp, ph, cons) = dat["cons"]
        source = dat["source"]
        nx = amp.shape[0]

        # Calculate complex phase in radians
        cph = -1j * ph * np.pi / 180.0
        hc = amp * np.exp(cph)

        print("...Expanding timeseries")
        ha = np.ma.zeros((tvec.shape[0], nx))
        for j in tqdm(range(nx)):
            ha[:, j] = extractor.predict_tidal_timeseries(
                tvec, hc[j].reshape(1, len(cons)), cons
            )

        # Remove invalid values by using nearest valid
        if hasattr(ha, "mask") and ha.mask.any():
            mask = ha.mask[0, :]
            real = np.where(mask == False)[0]
            for idx, cond in enumerate(mask.tolist()):
                if cond:
                    nearest_idx = real[np.argmin((real - idx) ** 2)]
                    ha[:, idx] = ha[:, nearest_idx]

        # Create dataset
        if isinstance(dat["geo"][1], (int, float)):
            chain = np.array([dat["geo"][1]])
            squeeze = True
        else:
            chain = dat["geo"][1]
            squeeze = False

        ds = xr.Dataset(
            coords=dict(time=timevec, chainage=chain),
            data_vars=dict(
                wl=(("time", "chainage"), ha),
                longitude=(("chainage",), dat["geo"][0][:, 0]),
                latitude=(("chainage",), dat["geo"][0][:, 1]),
            ),
        )
        ds.attrs["name"] = label
        ds.attrs["source"] = source
        ds["chainage"].attrs = {"long_name": "projected chainage", "units": "m"}
        ds["wl"].attrs = {"long_name": "tidal waterlevel", "units": "m"}
        ds["longitude"].attrs = crs.cs_to_cf()[1]
        ds["latitude"].attrs = crs.cs_to_cf()[0]

        if squeeze:
            ds = ds.isel(chainage=0)

        dsset[label] = ds

    if len(dsset) == 1:
        return list(dsset.values())[0]
    else:
        return dsset


def ExtractTide(
    time_start: Union[str, pd.Timestamp, datetime],
    time_end: Union[str, pd.Timestamp, datetime],
    fname: Union[str, Path] = None,
    model_dir: Union[str, Path] = None,
    shapefile: Union[str, Path] = None,
    out_path: Path = Path("."),
    process_ids: Union[tuple, list] = None,
    freq: Union[str, pd.Timedelta, timedelta] = "15min",
    spacing: int = 2500,
    attrs=dict(),
    interpolate_method="spline",
    source=None,
    local_tz: Tuple[float, str] = None,
    constituents: Union[str, Path, dict] = None,
    write_netcdf: bool = True,
    write_fvc: bool = True,
    fvc_path: Path = None,
    nc_path_str: str = None,
    extractor=None,
):
    """Full workflow for tidal waterlevel extraction."""
    if extractor is None:
        extractor = _default_extractor

    out_path = _parse_path(out_path)
    time_start = _parse_date(time_start)
    time_end = _parse_date(time_end)

    # Extract constituents if not provided
    if constituents is None:
        if source is None:
            if model_dir is None:
                raise ValueError("Either source or model_dir must be provided")
            source, model_dir = _detect_tide_model_source(Path(model_dir))
            if source is None:
                raise ValueError(
                    "Could not detect tidal model source from model directory"
                )

        if shapefile is None:
            raise ValueError("Shapefile required when constituents not provided")

        shapefile = Path(shapefile)
        if not shapefile.exists():
            raise FileNotFoundError(f"Shapefile not found: {shapefile}")

        gdf = load_nodestring_shapefile(shapefile, process_ids=process_ids)
        ns_dat = process_nodestring_gdf(gdf, spacing=spacing)

        print("Running GetTide")
        print("--------------------")
        print("Confirming Request:")
        print(f"...Time Start: {time_start.strftime('%Y-%m-%d %H:%M')}")
        print(f"...Time End: {time_end.strftime('%Y-%m-%d %H:%M')}")
        print(f"...Model Dir: {model_dir.absolute().as_posix()}")
        print(f"...Tidal Data Source: {source}")
        print(f"...Nodestring Name: {shapefile.name}")
        print(f"...Nodestring Folder: {shapefile.parent.absolute().as_posix()}")
        print(f"...Nodestring ID's to Process: {list(ns_dat.keys())}")
        print(f"...Nodestring CRS (EPSG): {gdf.crs.to_epsg()}")
        print(f"...Nodestring Spacing: {spacing:0.1f}m")

        constituents = get_constituents(
            ns_dat,
            model_dir,
            source=source,
            interpolate_method=interpolate_method,
            extractor=extractor,
        )
    else:
        if isinstance(constituents, (str, Path)):
            with open(constituents, "rb") as f:
                constituents = pickle.load(f)
        print(f"...Using pre-extracted constituents file")
        # Get source from constituents
        k = list(constituents.keys())[0]
        source = constituents[k]["source"]

    if local_tz is None:
        print(f"...Timezone: UTC (GMT+0.0)")
    else:
        print(f"...Timezone: UTC (GMT+0.0) AND")
        print(f"...Local Timezone: {local_tz[0]:0.1f}, {local_tz[1]}")

    ns_wlev = predict_waterlevel_timeseries(
        time_start, time_end, freq=freq, constituents=constituents, extractor=extractor
    )

    # Convert to dict if single dataset
    if isinstance(ns_wlev, xr.Dataset):
        ns_wlev = {ns_wlev.attrs["name"]: ns_wlev}

    # Set filename
    if fname is None:
        tsstr = time_start.strftime("%Y%m%d")
        testr = time_end.strftime("%Y%m%d")

        fname = f"{source.upper()}_TIDE_{tsstr}_{testr}.nc"

        if local_tz is not None:
            tzlbl = local_tz[1]
            fname = fname.replace(".", f"_{tzlbl}.")

    outname = out_path / fname

    # Write netcdf
    print(f"Writing dataset: {fname}")
    nc = _netcdf_writer(
        constituents,
        ns_wlev,
        outname,
        time_start,
        time_end,
        freq,
        source,
        write_netcdf=write_netcdf,
        local_tz=local_tz,
        attrs=attrs,
    )

    # TODO: This is hardcoded, but we only have FES support so it's ok for now.
    # We must change this if we add other tidal models.
    info_url = "https://www.aviso.altimetry.fr/en/data/products/auxiliary-products/global-tide-fes.html"

    # Write FVC control file
    if write_fvc:
        nc_path_str = outname.as_posix() if not nc_path_str else nc_path_str
        fvc_fname = fname.replace(".nc", ".fvc")
        fvc_path = out_path if not fvc_path else fvc_path

        write_tide_fvc(
            nc,
            nc_path=nc_path_str,
            output_path=fvc_path,
            filename=fvc_fname,
            source=source,
            info_url=info_url,
        )

    return nc


def _netcdf_writer(
    constituents: dict,
    ns_wlev: dict,
    outname: Path,
    time_start: pd.Timestamp,
    time_end: pd.Timestamp,
    freq: str,
    source: str,
    local_tz=None,
    attrs=dict(),
    write_netcdf=True,
):
    """Write netcdf file."""
    encoding = dict()

    timevec = pd.date_range(
        start=pd.Timestamp(time_start),
        end=pd.Timestamp(time_end),
        freq=freq,
    )

    ns = list(ns_wlev.keys())

    nc = xr.Dataset(
        coords=dict(time=timevec), attrs=attrs.copy()  # Copy to avoid mutable default
    )
    nc.attrs["source"] = source
    nc["time"].attrs["tz"] = "UTC"
    encoding["time"] = dict(dtype=np.float64, units="days since 1990-01-01 00:00:00")

    # Add local time if requested
    if local_tz is not None:
        tz_offset = local_tz[0]
        tz_name = local_tz[1]
        if tz_name is None:
            tz_name = f"GMT{tz_offset:+}"

        nc["local_time"] = (("time",), timevec + pd.Timedelta(tz_offset, unit="h"))
        nc["local_time"].attrs = dict(tz=tz_name)
        encoding["local_time"] = dict(
            dtype=np.float64, units="days since 1990-01-01 00:00:00"
        )

    for bnd_id in ns_wlev.keys():
        coords, chainage, nx = constituents[bnd_id]["geo"]
        wl_data = ns_wlev[bnd_id]["wl"]

        dimstr = f"ns{bnd_id}_chain"
        chnstr = f"ns{bnd_id}_chainage"
        varstr = f"ns{bnd_id}_wl"

        # Ensure chainage is always an array, even for single points
        chainage_array = np.asarray(chainage).astype(np.float32)
        if chainage_array.ndim == 0:  # scalar case
            chainage_array = np.array([chainage_array])

        nc[chnstr] = ((dimstr,), chainage_array)
        nc[chnstr].attrs["units"] = "m"
        nc[chnstr].attrs["longname"] = f"nodestring {bnd_id} chainage"

        # Handle water level data dimensions properly
        if wl_data.ndim == 1:  # Single point case (squeezed)
            # Reshape to (time, 1) for single chain point
            wl_values = wl_data.values.reshape(-1, 1).astype(np.float32)
        else:  # Multiple points case
            wl_values = wl_data.values.astype(np.float32)

        nc[varstr] = (("time", dimstr), wl_values)
        nc[varstr].attrs["units"] = "m"
        nc[varstr].attrs["long_name"] = f"nodestring {bnd_id} waterlevel"

        nc[f"ns{bnd_id}_longitude"] = ((dimstr,), coords[:, 0], crs.cs_to_cf()[1])
        nc[f"ns{bnd_id}_latitude"] = ((dimstr,), coords[:, 1], crs.cs_to_cf()[0])
        nc[f"ns{bnd_id}_longitude"].attrs["description"] = "X extraction coordinate"
        nc[f"ns{bnd_id}_latitude"].attrs["description"] = "Y extraction coordinate"

        encoding[chnstr] = dict(zlib=True, complevel=1, dtype=np.float32)
        encoding[varstr] = dict(zlib=True, complevel=1, dtype=np.float32)

    if write_netcdf:
        nc.to_netcdf(outname, encoding=encoding)

    return nc


# Keep the deprecated function for backwards compatibility
@deprecated(ExtractTide)
def gen_tfv_tide_netcdf(*args, **kwargs):
    """Deprecated - use ExtractTide instead."""
    # Convert old parameter names to new ones
    if "outname" in kwargs:
        kwargs["fname"] = Path(kwargs.pop("outname")).name
        kwargs["out_path"] = Path(kwargs["fname"]).parent
    if "version" in kwargs:
        kwargs["source"] = kwargs.pop("version")
    if "cons_file" in kwargs:
        kwargs["constituents"] = kwargs.pop("cons_file")

    return ExtractTide(*args, **kwargs)
