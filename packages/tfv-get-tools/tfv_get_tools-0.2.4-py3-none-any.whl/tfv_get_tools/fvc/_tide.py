import re
from pathlib import Path
from typing import List, Optional, Union

import xarray as xr

from tfv_get_tools.fvc._fvc import FVCWriter


class TideFVCWriter(FVCWriter):
    """Writer for TIDE profile FVC files."""

    def __init__(self, source=None, info_url=None):
        """Initialize tide FVC writer."""
        super().__init__(requires_coordinates=False, source=source, info_url=info_url)
        self.nodestrings: Dict[str, str] = {}  # Maps ns prefix to ID

    def detect_nodestrings(self, ds: xr.Dataset) -> None:
        """Detect nodestrings from dataset variables.

        Looks for variables with pattern 'nsX_*' where X is the nodestring identifier.

        Args:
            ds: Input xarray Dataset

        Raises:
            ValueError: If no nodestring variables are found
        """
        # Find all variables starting with 'ns'
        ns_pattern = re.compile(r"^ns(.+)_[^_]*$")

        # Get unique nodestring identifiers
        self.nodestrings = {}
        for var_name in ds.data_vars:
            match = ns_pattern.match(var_name)
            if match:
                ns_id = match.group(1)
                ns_prefix = f"ns{ns_id}"
                self.nodestrings[ns_prefix] = ns_id

        if not self.nodestrings:
            raise ValueError(
                "No nodestring variables found in dataset. "
                "Expected variables with pattern 'nsX_*' where X is the nodestring identifier."
            )

    def validate_nodestring_variables(self, ds: xr.Dataset) -> None:
        """Validate dataset has required variables for each nodestring.

        Args:
            ds: Input xarray Dataset

        Raises:
            ValueError: If required variables are missing
        """
        required_suffixes = ["_chainage", "_wl"]
        missing = []

        for ns_prefix in self.nodestrings:
            for suffix in required_suffixes:
                var_name = f"{ns_prefix}{suffix}"
                if var_name not in ds:
                    missing.append(var_name)

        if missing:
            raise ValueError(
                f"Missing required variables for tide configuration: {', '.join(missing)}"
            )

    def write_boundary_conditions(
        self,
        lines: List[str],
        nc_path: str,
    ) -> None:
        """Write boundary conditions block.

        Args:
            lines: List to append lines to
            nc_path: Path to the NetCDF file
        """
        for ns_prefix, ns_id in sorted(self.nodestrings.items()):
            lines.extend(
                [
                    f"BC == WL_CURT, {ns_id}, {nc_path}",
                    f"  BC Header == {self.time_var}, {ns_prefix}_chainage, dummy, {ns_prefix}_wl",
                    "  BC Update dt == 60.",
                    "  BC Time Units == days",
                    "  BC Reference Time == 01/01/1990 00:00",
                    "  BC Default == NaN",
                    "  Includes MSLP == 0",
                    "End BC",
                    "",
                ]
            )

    def generate(
        self,
        ds: xr.Dataset,
        nc_path: str = "tide_forcing.nc",
    ) -> List[str]:
        """Generate FVC configuration content for tide forcing.

        Args:
            ds: Input xarray Dataset containing tide variables
            nc_path: Path or filename for the NetCDF file (referenced in FVC content)

        Returns:
            List[str]: FVC configuration content as a list of strings

        Raises:
            ValueError: If required variables are missing for any nodestring
        """
        # Process dataset to detect time settings and nodestrings
        self.process_dataset(ds)
        self.detect_nodestrings(ds)
        self.validate_nodestring_variables(ds)

        lines = []

        # Write header with detected nodestrings
        source = ds.attrs.get("source", "")
        self.write_header(lines, f"{source} TIDE Dataset", ds)
        lines.append(f"! Nodestrings: {', '.join(sorted(self.nodestrings.values()))}")
        lines.append("")

        # Write boundary conditions
        self.write_boundary_conditions(lines, nc_path)

        return lines

    def write_file(
        self,
        lines: List[str],
        output_path: Union[str, Path],
        filename: Optional[str] = None,
    ) -> None:
        """Write FVC content to a file."""
        output_path = Path(output_path)
        filename = filename or "tide_forcing.fvc"
        if not filename.endswith(".fvc"):
            filename = filename.replace(".nc", ".fvc")

        output_path.mkdir(parents=True, exist_ok=True)
        with open(output_path / filename, "w") as f:
            for line in lines:
                f.write(line + "\n")


def write_tide_fvc(
    ds: xr.Dataset,
    nc_path: str = "tide_forcing.nc",
    output_path: Optional[Union[str, Path]] = None,
    filename: Optional[str] = None,
    source: Optional[str] = None,
    info_url: Optional[str] = None,
) -> List[str]:
    """Generate (and optionally write) TUFLOW-FV tide forcing configuration.

    Args:
        ds: Input xarray Dataset containing tide variables
        nc_path: Path or filename for the NetCDF file (referenced in FVC content)
        output_path: Optional path to write FVC file (if None, no file is written)
        filename: Optional filename for FVC file (if None, derives from nc_path)
        info_url: Optional URL for source information to be printed in FVC

    Returns:
        List[str]: FVC configuration content as a list of strings

    Examples:
        # Dataset with numeric nodestring identifiers
        >>> ds = xr.Dataset({
        ...     'ns1_chainage': [...],
        ...     'ns1_wl': [...],
        ...     'ns2_chainage': [...],
        ...     'ns2_wl': [...]
        ... })
        >>> lines = write_tide_fvc(ds, nc_path="tide.nc")

        # Dataset with named nodestring identifiers
        >>> ds = xr.Dataset({
        ...     'nsEast_chainage': [...],
        ...     'nsEast_wl': [...],
        ...     'nsWest_chainage': [...],
        ...     'nsWest_wl': [...]
        ... })
        >>> lines = write_tide_fvc(ds, nc_path="tide.nc")
    """
    writer = TideFVCWriter(source=source, info_url=info_url)

    lines = writer.generate(ds, nc_path)

    if output_path is not None:
        writer.write_file(lines, output_path, filename)

    return lines
