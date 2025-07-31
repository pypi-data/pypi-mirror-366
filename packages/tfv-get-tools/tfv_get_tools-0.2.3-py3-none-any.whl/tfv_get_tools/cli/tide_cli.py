import argparse
from pathlib import Path
import sys

from tfv_get_tools import ExtractTide
from tfv_get_tools.tide._tidal_base import _detect_tide_model_source

def entry():
    parser = argparse.ArgumentParser(
        description="""
            Tool for extracting tidal water-levels from FES2014 or FES2022 global tidal models
            
            This data is provided by AVISO+. 
            
            Requires the user to supply a filepath to pre-downloaded constituent .nc files.
            These can be downloaded (after registration) from AVISO+: 
            https://www.aviso.altimetry.fr/en/data/products/auxiliary-products/global-tide-fes.html
            """
    )

    parser.add_argument(
        "out",
        type=str,
        help="Output netcdf path and name (e.g., './outputs/my_tide_file.nc')",
    )

    parser.add_argument(
        "time_start", type=str, help="Start date of tide timeseries (yyyy-mm-dd)"
    )

    parser.add_argument(
        "time_end", type=str, help="End date of tide timeseries (yyyy-mm-dd)"
    )

    parser.add_argument(
        "nodestring",
        type=Path,
        help="Path to nodestring Shapefile (e.g., ./inputs/2d_ns_xx_L.shp)",
    )

    parser.add_argument(
        "model_dir",
        type=Path,
        help="Path to folder containing the tidal model files (e.g., fes2014 or fes2022b folders)",
    )
    
    parser.add_argument(
        "--spacing",
        default=2500,
        type=float,
        help="Approx resolution (meters) for WL verticies along nodestring (default == 2500m)",
    )

    parser.add_argument(
        "--freq",
        type=str,
        default="15min",
        help="Frequency of tidal data (default is '15min')",
    )

    parser.add_argument(
        "-tz", "--timezone_offset", default=None, type=float, help='Fixed offset hours for local timezone, e.g. "-tz 10"',
    )

    parser.add_argument(
        "-ltz", "--timezone_label",
        type=str,
        default=None,
        help='Custom timezone label, e.g. "-ltz AEST"',
    )

    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Tidal model source name. This will attempt to be automatically detected from model_dir, but it can be overriden if there are issues."
    )
    parser.add_argument(
        "-fvc",
        "--write_fvc",
        action="store_true",
        help="Write a TUFLOW FV '.fvc' file to accompany extracted tide dataset",
    )

    # Try to parse args - if blank, print the description
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()

    # Check if tz_offset or tz_label is supplied. If not, pass None.
    if args.timezone_offset is None:
        local_tz = None
    else:
        local_tz = (args.timezone_offset, args.timezone_label)
        
    # Pull out source name if unspecified
    model_dir = Path(args.model_dir)

    if args.source is None:
        source, model_dir = _detect_tide_model_source(model_dir)
    else:
        source = args.source


    ExtractTide(
        args.out,
        args.tstart,
        args.tend,
        model_dir,
        shapefile=args.nodestring,
        freq=args.freq,
        spacing=args.spacing,
        local_tz=local_tz,
        source=source,
        write_fvc=args.write_fvc,
    )

