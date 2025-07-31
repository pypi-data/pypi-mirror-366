"""Base CLI Class

This is where all the default arguments are setup for the CLI tools (for Downloader "A" or Merger "B")

For the mode specific arguments and messaging, go to X_cli.py program.
"""

from abc import ABC, abstractmethod
import argparse
from pathlib import Path
import re
import sys
       

class CLIBase(ABC):
    def __init__(self, prog_name, description):
        self.parser = argparse.ArgumentParser(
            prog=prog_name,
            description=description,
            epilog="See '<command> --help' to read about a specific sub-command.",
        )
        self.subparsers = self.parser.add_subparsers(
            dest="command", help="Sub-commands"
        )

    def dir_path(self, path):
        if Path(path).is_dir():
            return Path(path)
        else:
            raise argparse.ArgumentTypeError(
                f"--path:{path} is not a valid path - check that it exists"
            )

    @abstractmethod
    def add_source_arguments(self, parser):
        pass

    def add_download_parser(self, name, help_text):
        parser = self.subparsers.add_parser(name, help=help_text)
        parser.add_argument(
            "time_start", type=str, help='Start time in format "yyyy-mm-dd"'
        )
        parser.add_argument("time_end", type=str, help='End time in format "yyyy-mm-dd"')
        parser.add_argument(
            "bbox",
            nargs=4,
            type=float,
            help='Bounding box lon/lat extents as a list "xmin xmax ymin ymax"',
        )
        parser.add_argument(
            "-p",
            "--path",
            default=".",
            type=self.dir_path,
            help="Output directory, needs to exist first",
        )
        self.add_source_arguments(parser)
        parser.set_defaults(func=self.run_download)

        return parser

    def add_merge_parser(self, name, help_text):
        parser = self.subparsers.add_parser(name, help=help_text)
        parser.add_argument(
            "-f",
            "--file_name",
            help='Merged netcdf filename. Default: "<Type>_<time_start>_<time_end>.nc"',
        )
        parser.add_argument(
            "--time_start", help='Start time in format "yyyy-mm-dd"'
        )
        parser.add_argument("--time_end", help='End time in format "yyyy-mm-dd"')
        parser.add_argument(
            "-i",
            "--in_path",
            default=".",
            type=self.dir_path,
            help="Path to the directory holding the raw data files",
        )
        parser.add_argument(
            "-o",
            "--out_path",
            default="./raw",
            type=self.dir_path,
            help="Output directory for the merged dataset, should exist first. Defaults to `./raw`",
        )
        parser.add_argument(
            "-fvc",
            "--write_fvc",
            action="store_true",
            help="Write a TUFLOW FV '.fvc' file to accompany merged dataset",
        )
        parser.add_argument(
            "-rp",
            "--reproject",
            type=int,
            default=None,
            help="Reproject coordinates to a new coord system, input as EPSG code (e.g., 4326)",
        )
        parser.add_argument(
            "-tz",
            "--timezone_offset",
            type=float,
            default=None,
            help='Fixed offset hours for local timezone, e.g. "-tz 10"',
        )
        parser.add_argument(
            "-ltz",
            "--timezone_label",
            type=str,
            default=None,
            help='Custom timezone label, e.g. "-ltz AEST"',
        )
        parser.add_argument(
            "--wrapto360",
            action="store_true",
            help="Format longitude as (0, 360) rather than (-180, 180)",
        )
        parser.add_argument(
            "--pad_dry",
            action="store_true",
            help="Flag to pad values out over land or dry cells by applied nearest neighbour extrapolation",
        )
        self.add_source_arguments(parser)
        parser.set_defaults(func=self.run_merge)

        return parser

    @abstractmethod
    def run_download(self, args):
        pass

    @abstractmethod
    def run_merge(self, args):
        pass


def check_bbox(args):
    """
    Unfortunate edge case hackfix for programmer style floats like "-28." isntead of "-28.0".
    Fixes negative numbers with trailing dots in the final 4 arguments (bbox).
    Only modifies if all 4 final args are numeric-like!!
    Otherwise spits fire
    """
    # Early exit if only 1 or 2 args are provided - or --help  / -h
    if len(args) == 1 or len(args) == 2 or (len(args) >= 2 and (('-h' in args) or ('--help' in args))):
        return args
        
    if (len(args) < 4):
        raise ValueError("Must supply at minimum 6 arguments - time_start time_end xmin xmax ymin ymax")

    # Get the last 4 arguments ( Should be bbox )
    bbox_args = args[-4:]
    other_args = args[:-4]

    # Check if all 4 look like numbers (including problematic trailing dots)
    numeric_pattern = r'^-?\d*\.?\d*$'
    if not all(re.match(numeric_pattern, arg) and arg not in ['', '.', '-.', '-'] for arg in bbox_args):
        raise ValueError("The final 4 arguments don't appear to be valid bbox coordinates. "
                        "Expected format: xmin xmax ymin ymax (numeric values)")

    # Fix trailing dots by adding '0'
    trailing_dot_pattern = r'^-?\d+\.$'
    fixed_bbox = [arg + '0' if re.match(trailing_dot_pattern, arg) else arg for arg in bbox_args]

    # Verify they're actually parseable as floats
    try:
        [float(arg) for arg in fixed_bbox]
    except ValueError:
        raise ValueError("The final 4 arguments cannot be parsed as bbox coordinates."
                        "Expected format: xmin xmax ymin ymax (numeric values)")

    return other_args + fixed_bbox