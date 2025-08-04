from pathlib import Path
from typing import Union, List, Optional, Dict

import xarray as xr

from tfv_get_tools.fvc._fvc import FVCWriter


class AtmosFVCWriter(FVCWriter):
    """Writer for ATMOS FVC files."""

    # Default mappings of dataset variables to TUFLOW-FV variables
    DEFAULT_VAR_MAPPINGS = {
        "t2m": {
            "tfv_var": "AIR_TEMP_GRID",
            "bc_scale": 1.0,
            "bc_offset": -273.15,  # K to C
        },
        "relhum": {"tfv_var": "REL_HUM_GRID", "bc_scale": 1.0, "bc_offset": 0.0},
        "u10": {
            "tfv_var": "W10_GRID",  # Special case - paired with vwnd10m
            "bc_scale": 1.0,
            "bc_offset": 0.0,
        },
        "v10": {
            "tfv_var": "W10_GRID",  # Special case - paired with uwnd10m
            "bc_scale": 1.0,
            "bc_offset": 0.0,
        },
        "mslp": {
            "tfv_var": "MSLP_GRID",  # Special case - paired with uwnd10m
            "bc_scale": 0.01,
            "bc_offset": 0.0,
        },
        "prate": {"tfv_var": "PRECIP_GRID", "bc_scale": 1.0, "bc_offset": 0.0},
        "dlwrf": {"tfv_var": "LW_RAD_GRID", "bc_scale": 1.0, "bc_offset": 0.0},
        "dswrf": {"tfv_var": "SW_RAD_GRID", "bc_scale": 1.0, "bc_offset": 0.0},
    }

    def __init__(self, var_mappings: Optional[Dict] = None, source=None, model=None, info_url=None):
        """Initialize atmospheric FVC writer.

        Args:
            var_mappings: Optional dictionary overriding default variable mappings
        """
        super().__init__(requires_coordinates=True, source=source, model=model, info_url=info_url)
        self.var_mappings = var_mappings or self.DEFAULT_VAR_MAPPINGS
        self.available_vars = set()

    def detect_variables(self, ds: xr.Dataset) -> None:
        """Detect available variables in the dataset.

        Args:
            ds: Input xarray Dataset
        """
        self.available_vars = set(ds.data_vars) & set(self.var_mappings.keys())

        # Verify wind components come in pairs
        if ("uwnd10m" in self.available_vars) != ("vwnd10m" in self.available_vars):
            raise ValueError(
                "Both uwnd10m and vwnd10m must be present for wind configuration"
            )

    def write_grid_definition(self, lines: List[str], nc_path: str) -> None:
        """Write grid definition block."""
        xvar, yvar = self.coordinate_vars
        lines.extend(
            [
                f"Grid Definition File == {nc_path}",
                f"  Grid Definition Variables == {xvar}, {yvar}",
                "  Grid Definition Label == atmos",
                "End Grid",
                "",
            ]
        )

    def write_boundary_conditions(self, lines: List[str], nc_path: str) -> None:
        """Write boundary conditions block."""
        wind_written = False

        for var_name in sorted(self.available_vars):
            config = self.var_mappings[var_name]
            tfv_var = config["tfv_var"]
            bc_scale = config["bc_scale"]
            bc_offset = config["bc_offset"]

            # Handle wind components specially
            if tfv_var == "W10_GRID":
                if wind_written:
                    continue
                wind_written = True
                lines.extend(
                    [
                        f"BC == {tfv_var}, atmos, {nc_path}",
                        f"  BC Header == {self.time_var}, u10, v10",
                    ]
                )
                if bc_scale != 1.0:
                    lines.append(f"  BC Scale == {bc_scale}, {bc_scale}")
                if bc_offset != 0.0:
                    lines.append(f"  BC Offset == {bc_offset}, {bc_offset}")
            else:
                lines.extend(
                    [
                        f"BC == {tfv_var}, atmos, {nc_path}",
                        f"  BC Header == {self.time_var}, {var_name}",
                    ]
                )
                if bc_scale != 1.0:
                    lines.append(f"  BC Scale == {bc_scale}")
                if bc_offset != 0.0:
                    lines.append(f"  BC Offset == {bc_offset}")

            # Common BC settings
            lines.extend(
                [
                    "  BC Update dt == 3600.",
                    "  BC Time Units == hours",
                    "  BC Reference Time == 01/01/1990 00:00",
                    "  BC Default == NaN",
                    "End BC",
                    "",
                ]
            )

    def generate(
        self,
        ds: xr.Dataset,
        nc_path: str = "atmos_forcing.nc",
    ) -> List[str]:
        """Generate FVC configuration content for atmospheric forcing.

        Args:
            ds: Input xarray Dataset containing atmospheric variables
            nc_path: Path or filename for the NetCDF file (referenced in FVC content)

        Returns:
            List[str]: FVC configuration content as a list of strings
        """
        # Process dataset to detect coordinates, time settings, and variables
        self.process_dataset(ds)
        self.detect_variables(ds)

        if not self.available_vars:
            raise ValueError("No supported atmospheric variables found in dataset")

        lines = []

        # Write header
        self.write_header(lines, "Atmospheric Dataset", ds)

        # Write grid definition
        self.write_grid_definition(lines, nc_path)

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
        filename = filename or "atmos_forcing.fvc"
        if not filename.endswith(".fvc"):
            filename = filename.replace(".nc", ".fvc")

        with open(output_path / filename, "w") as f:
            for line in lines:
                f.write(line + "\n")


def write_atmos_fvc(
    ds: xr.Dataset,
    nc_path: str = "atmos_forcing.nc",
    output_path: Optional[Union[str, Path]] = None,
    filename: Optional[str] = None,
    var_mappings: Optional[Dict] = None,
    source: Optional[str] = None,
    model: Optional[str] = None,
    info_url: Optional[str] = None,
) -> List[str]:
    """Generate (and optionally write) TUFLOW-FV atmospheric forcing configuration.

    Args:
        ds: Input xarray Dataset containing atmospheric variables
        nc_path: Path or filename for the NetCDF file (referenced in FVC content)
        output_path: Optional path to write FVC file (if None, no file is written)
        filename: Optional filename for FVC file (if None, derives from nc_path)
        var_mappings: Optional dictionary to override default variable mappings
        source: Optional source string for the FVC header
        model: Optional model string for the FVC header
        info_url: Optional URL for source information to be printed in FVC

    Returns:
        List[str]: FVC configuration content as a list of strings

    Examples:
        # Just generate FVC content with auto-detected variables
        >>> lines = write_atmos_fvc(dataset, nc_path="forcing.nc")

        # Generate and write to file
        >>> lines = write_atmos_fvc(
        ...     dataset,
        ...     nc_path="forcing.nc",
        ...     output_path="path/to/output"
        ... )

        # Generate with custom variable mappings
        >>> custom_mappings = {
        ...     "temperature": {"tfv_var": "T2_GRID", "bc_scale": 1.0, "bc_offset": -273.15}
        ... }
        >>> lines = write_atmos_fvc(
        ...     dataset,
        ...     nc_path="forcing.nc",
        ...     var_mappings=custom_mappings
        ... )
    """
    writer = AtmosFVCWriter(var_mappings=var_mappings, source=source, model=model, info_url=info_url)

    lines = writer.generate(ds, nc_path)

    if output_path is not None:
        writer.write_file(lines, output_path, filename)

    return lines
