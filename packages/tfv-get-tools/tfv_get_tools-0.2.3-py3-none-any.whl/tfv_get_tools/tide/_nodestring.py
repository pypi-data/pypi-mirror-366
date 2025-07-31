from pathlib import Path
from typing import Union, List, Any

import numpy as np
import pandas as pd
import geopandas as gpd
from pyproj import CRS
from geopandas import GeoDataFrame
from shapely.geometry import LineString, Point


def _convert_id(x: Any):
    """Simple ID entry conversion

    Try to make each ID an integer, but fall back on a string.

    Args:
        x (Any): ID Field (e.g., 2, 'NS1')

    Returns:
        Union[int, str]: ID as either an int or str, with preference on integer.
    """
    try:
        x = int(x)
    except:
        x = str(x)
    return x


def load_nodestring_shapefile(
    filename: Union[Path, str], crs: int = None, process_ids: Union[tuple, list] = None
) -> GeoDataFrame:
    """Load a TUFLOW FV nodestring shapefile as a GeoDataFrame.

    The CRS will be read from the .prj file if present. Otherwise, `crs=X` can be passed as an EPSG integer code.

    By default, all the features in the nodestring will be loaded. Use `process_ids` arg to filter to only certain features.

    Args:
        filename (Union[Path, str]): Path to the nodestring .shp file
        crs (int, optional): Coordinate reference system EPSG code. Defaults to None.
        process_ids (Union[tuple, list], optional): List of ID's to process. Defaults to None.

    Returns:
        GeoDataFrame: Frame containing the geometry and ID features ready for processing.
    """

    gdf = gpd.read_file(filename, columns=["ID"])

    # Set the CRS of the geodataframe. Assume 4326 as backup.
    if crs is None:
        if not gdf.crs:
            print(
                "No CRS could be read from the shapefile. Assuming nodestring is in latitude/longitude (EPSG 4326)"
            )
            gdf.set_crs(4326)
    else:
        try:
            crs = CRS.from_epsg(crs)
            gdf = gdf.set_crs(crs)
        except:
            raise ValueError(
                f"Supplied CRS `{crs}` is not valid. Please provide an EPSG code as an integer, e.g., 7856"
            )

    # Parse the process ID's
    assert "ID" in gdf.columns, "There must be an `ID` column present in the shapefile"
    shp_ids = gdf["ID"].apply(_convert_id).tolist()

    if process_ids is None:
        # If no id's are supplied, then we take everything except obvious nan's.
        process_ids = [x for x in shp_ids if x != "nan"]
    else:
        # If they are supplied, then we first convert to INT or STR
        process_ids = [_convert_id(x) for x in process_ids]
        for x in process_ids:
            assert (
                x in shp_ids
            ), f"Nodestring feature ID `{x}` was not found in the shapefile"

    # Do a check on geometry before moving on
    checked_ids = []
    for x in process_ids:
        idx = shp_ids.index(x)
        geo = gdf.loc[idx, "geometry"]

        if geo is None:
            print(
                f"Warning - No geometry detected for Nodestring ID {x}. Skipping this feature..."
            )
        elif not isinstance(geo, LineString):
            print(
                f"Warning - Invalid geometry detected for Nodestring ID {x}. Must be a Linestring type. Skipping this feature..."
            )
        else:
            checked_ids.append(x)

    msk = [shp_ids.index(x) for x in checked_ids]
    gdf = gdf.loc[msk]

    return gdf


def process_nodestring_gdf(gdf: GeoDataFrame, spacing=2500.0) -> dict:
    """Generates a dictionary containing a Nx2 array of lat/lon coordinates from a nodestring geodataframe.

    The geodataframe must have a `crs` set. It does not need to be lat/lon.

    All features in the geodataframe will be processed - it is assumed that filtering has already happened.

    Args:
        gdf (GeoDataFrame): nodestring geodataframe.
        spacing (float, optional): Spacing in meters. Defaults to 2500.0

    Returns:
        dict: nodestring dictionary where key is the `ID` and values are a Nx2 np.ndarray.
    """

    if gdf.crs is None:
        raise ValueError("The nodestring geodataframe must have a CRS defined.")

    coords = sample_coordinates_along_linestring(gdf, spacing)

    process_ids = [_convert_id(x) for x in gdf["ID"]]

    ns_dat = {}
    for i, k in enumerate(process_ids):
        coord_array = np.squeeze(np.asarray([x.xy for x in coords.iloc[i]]))
        ns_dat[k] = coord_array

    return ns_dat


def sample_coordinates_along_linestring(
    gdf: gpd.GeoDataFrame, spacing: float
) -> gpd.GeoSeries:
    """
    Sample coordinates along LineString geometries in a GeoDataFrame.

    Args:
        gdf (gpd.GeoDataFrame): The input GeoDataFrame containing LineString geometries.
        spacing (float): The desired spacing between sampled points in meters.

    Returns:
        gpd.GeoSeries: A GeoSeries where each element is a list of sampled Points in WGS84 coordinates.
    """
    return gdf.apply(lambda row: process_row(row, spacing, gdf.crs), axis=1)


def sample_linestring(line: LineString, spacing_meters: float) -> List[Point]:
    """
    Sample points along a LineString at a specified spacing.

    Args:
        line (LineString): The LineString to sample points from.
        spacing_meters (float): The spacing between points in meters.

    Returns:
        List[Point]: A list of sampled points along the LineString.

    Raises:
        ValueError: If the line is empty or the spacing is not positive.
    """
    if line.is_empty:
        raise ValueError("The LineString is empty.")
    if spacing_meters <= 0:
        raise ValueError("Spacing must be a positive number.")

    line_length = line.length
    num_points = int(line_length / spacing_meters) + 1
    distances = np.linspace(0, line_length, num_points)
    return [line.interpolate(distance) for distance in distances]


def process_row(row: pd.Series, spacing: float, crs: CRS) -> List[Point]:
    """
    Process a single row of a GeoDataFrame, sampling points along its LineString geometry.

    This function handles both geographic (lat/lon) and projected coordinate systems.
    It always returns the sampled points in WGS84 (EPSG:4326) lat/lon coordinates.

    Args:
        row (pd.Series): A row from a GeoDataFrame containing a 'geometry' column
                         with a LineString object.
        spacing (float): The desired spacing between sampled points in meters.
        crs (CRS): The coordinate reference system of the input geometry.

    Returns:
        List[Point]: A list of sampled points along the LineString, in lat/lon coordinates.

    Raises:
        ValueError: If the input geometry is not a LineString.
    """
    if not isinstance(row.geometry, LineString):
        raise ValueError("The geometry must be a LineString.")

    if crs.is_geographic:
        # Convert to UTM for accurate distance calculations
        centroid = row.geometry.centroid
        utm_zone = int((centroid.x + 180) // 6 + 1)
        utm_crs = CRS.from_proj4(
            f"+proj=utm +zone={utm_zone} +datum=WGS84 +units=m +no_defs"
        )
        utm_geometry = gpd.GeoSeries([row.geometry], crs=crs).to_crs(utm_crs)[0]
        sampled_points = sample_linestring(utm_geometry, spacing)
        points_gdf = gpd.GeoDataFrame(geometry=sampled_points, crs=utm_crs)
    else:
        # If already projected, sample directly
        sampled_points = sample_linestring(row.geometry, spacing)
        points_gdf = gpd.GeoDataFrame(geometry=sampled_points, crs=crs)

    # Convert sampled points to lat/lon (WGS84)
    points_gdf = points_gdf.to_crs(epsg=4326)
    return points_gdf.geometry.tolist()
