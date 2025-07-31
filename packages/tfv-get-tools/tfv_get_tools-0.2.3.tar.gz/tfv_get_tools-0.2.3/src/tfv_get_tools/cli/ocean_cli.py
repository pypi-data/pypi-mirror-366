"""Ocean CLI tool

This tool provides two sub-programs:
- Downloading raw ocean physics data
- Merging raw ocean physics data and assisting with TUFLOW FV fvc template setup

"""

from argparse import ArgumentParser
import sys
import textwrap

from tfv_get_tools.cli._cli_base import CLIBase, check_bbox
from tfv_get_tools import DownloadOcean, MergeOcean


def print_ocean_info():
    """Returns detailed help text for GetOcean"""
    return textwrap.dedent("""
        GetOcean
        =======================================
        
        This tool is designed to support users with downloading ocean physics datasets
        from common online publicly available sources, as well as subsequent 
        pre-processing and collation for TUFLOW FV modelling. 
        The ideology of the tool is to provide the datasets in a true to original
        raw format (program "A"), and then a processed "simplified"
        merged format ready for TUFLOW FV modelling (program "B").

        GetOcean works with ocean physics data including sea surface height, water 
        temperature, salinity, and ocean current velocity components (u, v).

        There are several data sources and sub-models available currently. These are listed 
        below. Some of these may require registration. 
        
        Available data sources and sub-models:
        -------------
        1. (Default) "HYCOM" - Global Ocean Forecasting System
            - "default" - Global ocean analysis and forecast system
        
        2. Other sources available - see documentation
        
        Example Usage:
        ---------
        Download HYCOM Ocean Data - all defaults, daily timestep
            `GetOcean A 2011-01-01 2012-01-01 145 150 -30 -25`
        
        Download HYCOM with 3-hourly timestep and depth limits
            `GetOcean A 2011-01-01 2012-01-01 145 150 -30 -25 -ts 3 -z 0 100`
        
        Merge Ocean Data - all defaults, merge all data in the raw folder
            `GetOcean B`

        Merge Ocean Data with reprojection and local time
            `GetOcean B -tz 10 -ltz AEST -rp 7856` 
    
        For more specific help, please use:
        `GetOcean A -h` or `GetOcean B -h`
        """)


def entry():
    """This is the entrypoint to the CLI, linked in the pyproject.toml"""
    cli = GetOcean()
    sys.argv = check_bbox(sys.argv)
    cli.run_cli()


class GetOcean(CLIBase):
    def __init__(self, download_func=None, merge_func=None):
        super().__init__("GetOcean", "Tool for downloading and merging Ocean data")
        
        # Allow injection of functions for testing
        self.download_func = download_func or DownloadOcean
        self.merge_func = merge_func or MergeOcean
        
        dparser = self.add_download_parser(
            "A",
            "Download raw Ocean files for a set time period and bounding box extents",
        )
        self.add_merge_parser(
            "B",
            "Merge raw Ocean files into a single netcdf, and optionally write a TUFLOW FV FVC file",
        )

        # Add ocean-specific download arguments
        dparser.add_argument(
            "-ts",
            "--timestep",
            default=24,
            type=int,
            help="Download timestep interval in hours, only relevant for HYCOM. Must be a multiple of 3 (highest resolution available). Default is 24 (daily). All sources other than HYCOM are downloaded in the best available time resolution.",
        )
        
        dparser.add_argument(
            "-z",
            "--zlim",
            nargs=2,
            type=float,
            default=None,
            help='Minimum and maximum depth "zmin zmax". Defaults to the maximum for source.',
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
        text = print_ocean_info()
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
            default="HYCOM",
            help='Ocean data source. Default = "HYCOM". Optionally others see wiki.',
        )
        parser.add_argument(
            "-m",
            "--model",
            type=str,
            default="default",
            help='Model from source. Default is "default". Optionally others see wiki.',
        )

    def run_download(self, args):
        """Call the DownloadOcean function

        Args:
            args: CLI argument parser
        """
        xlims = tuple([float(x) for x in args.bbox[:2]])
        ylims = tuple([float(x) for x in args.bbox[2:]])

        # Handle zlim - can be None
        zlims = tuple(args.zlim) if args.zlim is not None else None

        self.download_func(
            args.time_start,
            args.time_end,
            xlims,
            ylims,
            zlims=zlims,
            time_interval=args.timestep,
            source=args.source,
            out_path=args.path,
        )

    def run_merge(self, args):
        """Call the MergeOcean function

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
            write_fvc=args.write_fvc,
            reproject=args.reproject,
            local_tz=tz,
            wrapto360=args.wrapto360,
            pad_dry=args.pad_dry,
        )