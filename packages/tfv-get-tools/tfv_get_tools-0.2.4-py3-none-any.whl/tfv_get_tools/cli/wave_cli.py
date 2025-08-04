"""Wave CLI tool

This tool provides two sub-programs:
- Downloading raw wave hindcast data
- Merging raw wave hindcast data

"""

from argparse import ArgumentParser
import sys
import textwrap

from tfv_get_tools.cli._cli_base import CLIBase, check_bbox
from tfv_get_tools import DownloadWave, MergeWave


def print_wave_info():
    """Returns detailed help text for GetWave"""
    return textwrap.dedent("""
        GetWave
        =======================================
        
        This tool is designed to support users with downloading wave hindcast datasets
        from common online publicly available sources, as well as subsequent 
        pre-processing and collation for TUFLOW FV and Other Wave modelling. 
        The ideology of the tool is to provide the datasets in a true to original
        raw format (program "A"), and then in a processed "simplified"
        merged format ready for model applications (program "B").

        GetWave works with wave hindcast data including significant wave height, 
        wave direction, wave period, and other wave parameters from numerical 
        wave models.

        There are several data sources and sub-models available currently. These are listed 
        below. Some of these may require registration. 
        
        Available data sources and sub-models:
        -------------
        1. (Default) "CAWCR" - CSIRO WaveWatch III Hindcast
            - "glob_24m" - Global model with 24-minute resolution (default)
            - Other resolutions available - see documentation
        
        2. Other wave model sources available - see documentation
        
        Example Usage:
        ---------
        Download CAWCR Wave Data - all defaults
            `GetWave A 2011-01-01 2012-01-01 145 150 -30 -25`
        
        Download with different source/model
            `GetWave A 2011-01-01 2012-01-01 145 150 -30 -25 -s CAWCR -m glob_24m`
        
        Merge Wave Data - all defaults, merge all data in the raw folder
            `GetWave B`

        Merge Wave Data with reprojection and local time
            `GetWave B -tz 10 -ltz AEST -rp 7856` 
    
        For more specific help, please use:
        `GetWave A -h` or `GetWave B -h`
        """)


def entry():
    """This is the entrypoint to the CLI, linked in the pyproject.toml"""
    cli = GetWave()
    sys.argv = check_bbox(sys.argv)
    cli.run_cli()


class GetWave(CLIBase):
    def __init__(self, download_func=None, merge_func=None):
        super().__init__("GetWave", "Tool for downloading and merging Wave data")
        
        # Allow injection of functions for testing
        self.download_func = download_func or DownloadWave
        self.merge_func = merge_func or MergeWave
        
        self.add_download_parser(
            "A", 
            "Download raw wave files for a set time period and bounding box extents"
        )
        self.add_merge_parser(
            "B", 
            "Merge raw Wave files into a single netcdf, and optionally write a TUFLOW FV FVC file"
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
        text = print_wave_info()
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
            default="CAWCR",
            help='Wave data source. Default = "CAWCR" (CSIRO WaveWatch III Hindcast). Optionally others see wiki.',
        )
        parser.add_argument(
            "-m",
            "--model",
            type=str,
            default="glob_24m",
            help='Model from source. Default = "glob_24m" (global model from source "CAWCR"). Optionally others see wiki.',
        )

    def run_download(self, args):
        """Call the DownloadWave function

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
        )

    def run_merge(self, args):
        """Call the MergeWave function

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