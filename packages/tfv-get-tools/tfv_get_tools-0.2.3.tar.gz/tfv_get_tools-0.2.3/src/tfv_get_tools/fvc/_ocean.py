from typing import Union, List, Optional
from pathlib import Path

import xarray as xr

from tfv_get_tools.fvc._fvc import FVCWriter


class OceanFVCWriter(FVCWriter):
    """Writer for OGCM FVC include files."""

    DEFAULT_VAR_ORDER = ["surf_el", "water_u", "water_v", "salinity", "water_temp"]

    def __init__(self, var_order: Optional[List[str]] = None, source=None, model=None, info_url=None):
        """Initialize ocean FVC writer.

        Args:
            var_order: Optional list specifying order of variables in the boundary condition
        """
        super().__init__(requires_coordinates=True, source=source, model=model, info_url=info_url)
        self.var_order = var_order or self.DEFAULT_VAR_ORDER

    def write_grid_definition(self, lines: List[str], nc_path: str):
        """Write grid definition block.

        Args:
            lines: List to append lines to
            nc_path: Path to the NetCDF file
        """
        xvar, yvar = self.coordinate_vars
        lines.extend(
            [
                f"Grid Definition File == {nc_path}",
                f"  Grid Definition Variables == {xvar}, {yvar}, depth",
                "  Grid Definition Label == ocean",
                "  Boundary Gridmap == 1",
                "End Grid",
                "",
            ]
        )

    def write_boundary_conditions(self, lines: List[str], nc_path: str):
        """Write boundary conditions block.

        Args:
            lines: List to append lines to
            nc_path: Path to the NetCDF file
        """
        vlist = ",".join(self.var_order)
        lines.extend(
            [
                f"BC == OBC_GRID, ocean, {nc_path}",
                f"  BC Nodestrings == #  ! Please supply open boundary ns list",
                "  Sub-type == 6",
                f"  BC Header == {self.time_var},{vlist}",
                "  BC Update dt == 900.",
                "  BC Time Units == hours",
                "  BC Reference Time == 01/01/1990 00:00",
                "  BC Offset == -0.0, 0.0, 0.0, 0.0, 0.0   ! Check Offset -0.0",
                "  BC Default == NaN",
                "  Vertical Coordinate Type == depth",
                "End BC",
                "",
            ]
        )

    def generate(
        self,
        ds: xr.Dataset,
        nc_path: str = "ocean_forcing.nc",
    ) -> List[str]:
        """Generate FVC configuration content for ocean forcing.

        Args:
            ds: Input xarray Dataset containing ocean variables
            nc_path: Path or filename for the NetCDF file (referenced in FVC content)

        Returns:
            List[str]: FVC configuration content as a list of strings
        """
        # Process dataset to detect coordinates and time settings
        self.process_dataset(ds)

        lines = []

        # Write header
        self.write_header(lines, "Ocean Dataset", ds)

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
        """Write FVC content to a file.

        Args:
            lines: FVC configuration content
            output_path: Directory to write the file to
            filename: Optional filename (if None, will use 'ocean_forcing.fvc')
        """
        output_path = Path(output_path)
        filename = filename or "ocean_forcing.fvc"
        if not filename.endswith(".fvc"):
            filename = filename.replace(".nc", ".fvc")

        output_path.mkdir(parents=True, exist_ok=True)
        with open(output_path / filename, "w") as f:
            for line in lines:
                f.write(line + "\n")


def write_ocean_fvc(
    ds: xr.Dataset,
    nc_path: str = "ocean_forcing.nc",
    output_path: Optional[Union[str, Path]] = None,
    filename: Optional[str] = None,
    var_order: Optional[List[str]] = None,
    source: Optional[str] = None,
    model: Optional[str] = None,
    info_url: Optional[str] = None,
) -> List[str]:
    """Generate (and optionally write) TUFLOW-FV ocean forcing configuration.

    Args:
        ds: Input xarray Dataset containing ocean variables
        nc_path: Path or filename for the NetCDF file (referenced in FVC content)
        output_path: Optional path to write FVC file (if None, no file is written)
        filename: Optional filename for FVC file (if None, derives from nc_path)
        var_order: Optional list specifying order of variables
        source: Optional source string for the FVC header
        model: Optional model string for the FVC header
        info_url: Optional URL for source information to be printed in FVC

    Returns:
        List[str]: FVC configuration content as a list of strings

    Examples:
        # Just generate FVC content
        >>> lines = write_ocean_fvc(dataset, nc_path="forcing.nc")

        # Generate and write to file
        >>> lines = write_ocean_fvc(
        ...     dataset,
        ...     nc_path="forcing.nc",
        ...     output_path="path/to/output"
        ... )

        # Generate with custom variable order
        >>> lines = write_ocean_fvc(
        ...     dataset,
        ...     nc_path="forcing.nc",
        ...     var_order=["water_temp", "salinity", "water_u", "water_v", "surf_el"]
        ... )
    """
    writer = OceanFVCWriter(var_order=var_order, source=source, model=model, info_url=info_url)

    lines = writer.generate(ds, nc_path)

    if output_path is not None:
        writer.write_file(lines, output_path, filename)

    return lines
