"""ATMOS CLI

This tool provides two sub-programs:
- Downloading raw atmospheric data  
- Merging raw atmospheric data and assisting with TUFLOW FV fvc template setup
"""

from argparse import ArgumentParser
import sys
import textwrap

from tfv_get_tools import DownloadAtmos, MergeAtmos
from tfv_get_tools.cli._cli_base import CLIBase, check_bbox

def print_atmos_info():
    """Returns detailed help text for GetAtmos"""
    return textwrap.dedent("""
        GetAtmos
        =======================================
        
        This tool is designed to support a user with downloading  atmospheric datasets
        from common online publicly available sources, as well as subsequent 
        pre-processing and collation for TUFLOW FV modelling. 
        The ideology of the tool is to provide the datasets in a true to original
        raw format (program "A"), and then in a processed "simplified"
        merged format ready for TUFLOW FV modelling (program "B").

        GetAtmos works with atmospheric reanalysis and analysis data, including 10m wind 
        velocity components, mean sea-level pressure, temperature, relative humidity
        and short/long wave downward radiation. 

        There are several data sources and sub-models available currently. These are listed 
        below. Some of these may require registration. 
        
        Available data sources and sub-models:
        -------------
        1. (Default) ECMWF's "ERA5"  - registration required
            - "default" - A global reanalysis 
        
        2. NOAA's "CFSR"
            - "default" - A global reanalysis 

        3. BoM's "BARRA2"
           - "R2" - An 11-km grid reanalysis covering Australia
           - "C2" - An 4-km grid reanalysis covering Australia, with only wind and pressure fields downloaded. 
           - "RE2" - (Testing Only) An experimental ensembles 22-km grid covering Australia.
        
        Example Usage:
        ---------
        Download ERA5 Reanalysis Data - all defaults
            `GetAtmos A 2011-01-01 2012-01-01 145 150 -30 -25`
        
        Merge ERA5 Reanalysis Data - all defaults, merge all data in the raw folder
            `GetAtmos B`

        Download BARRA2 C2 Dataset
            `GetAtmos A -s BARRA2 -m R2 2011-01-01 2012-01-01 150 153 -30 -25`

        Merge BARRA2 C2 Dataset with reprojection and local time
            `GetAtmos B -s BARRA2 -m R2 -tz 10 -ltz AEST -rp 7856` 
    
        For more specific help, please use:
        `GetAtmos A -h` or `GetAtmos B -h`
        """)


def entry():
    """This is the entrypoint to the CLI, linked in the pyproject.toml"""
    cli = GetAtmos()
    sys.argv = check_bbox(sys.argv)
    cli.run_cli()


class GetAtmos(CLIBase):
    def __init__(self, download_func=None, merge_func=None):
        super().__init__("GetAtmos", "Tool for downloading and merging Atmos data")
        
        # Allow injection of functions for testing
        self.download_func = download_func or DownloadAtmos
        self.merge_func = merge_func or MergeAtmos
        
        self.add_download_parser(
            "A",
            "Download raw Atmos files for a set time period and bounding box extents",
        )
        self.add_merge_parser(
            "B",
            "Merge raw Atmos files into a single netcdf, and optionally write a TUFLOW FV FVC file",
        )

        self.add_info_parser()

    def run_cli(self):
        """Parse arguments and execute the appropriate function."""
        args = self.parser.parse_args()
        if args.command is not None:
            args.func(args)
        else:
            self.parser.print_help()

    def add_info_parser(self):
        parser = self.subparsers.add_parser('info', help="Print detailed information about this program and the options")
        parser.set_defaults(func=self.print_detailed_info)
    
    def print_detailed_info(self, args):
        text = print_atmos_info()
        print(text)

    def add_source_arguments(self, parser: ArgumentParser):
        """Add source arguments
        
        Args:
            parser: The parser to add arguments to.
        """
        super().add_source_arguments(parser)

        parser.add_argument(
            '--info',
            action="store_true",
            help="Display the full program help"
        )

        parser.add_argument(
            "-s",
            "--source",
            type=str,
            default="ERA5",
            help='Atmos data source. Default = "ERA5". Optionally others see wiki.',
        )
        parser.add_argument(
            "-m",
            "--model",
            type=str,
            default="default",
            help='Model from source. Default is "default". Optionally others see wiki.',
        )
        parser.add_argument(
            "--test",
            action="store_true",
            help="Run in test mode - no actual downloads performed",
        )

    def run_download(self, args):
        """Call the DownloadAtmos function

        Args:
            args: CLI argument parser
        """
        xlims = tuple([float(x) for x in args.bbox[:2]])
        ylims = tuple([float(x) for x in args.bbox[2:]])

        self.download_func(
            args.time_start,
            args.time_end,
            xlims,
            ylims,
            source=args.source,
            out_path=args.path,
            TEST_MODE=args.test,
        )

    def run_merge(self, args):
        """Call the MergeAtmos function

        Args:
            args: CLI argument parser
        """
        # Sort out the timezone arguments
        if (args.timezone_offset is not None) and (args.timezone_label is not None):
            tz = (args.timezone_offset, args.timezone_label)
        elif args.timezone_offset is not None:
            sign = "+" if args.timezone_offset > 0 else "-"
            tz = (args.timezone_offset, f"UTC{sign}{abs(args.timezone_offset):0.1f}")
        elif (args.timezone_offset is None) and (args.timezone_label is not None):
            raise ValueError("Need to supply a timezone_offset!")
        else:
            tz = None

        self.merge_func(
            in_path=args.in_path,
            out_path=args.out_path,
            fname=args.file_name,
            source=args.source,
            model=args.model,
            time_start=args.time_start,
            time_end=args.time_end,
            # write_fvc=args.write_fvc,
            reproject=args.reproject,
            local_tz=tz,
            wrapto360=args.wrapto360,
            pad_dry=args.pad_dry,
        )