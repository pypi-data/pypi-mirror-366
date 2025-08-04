# TFV Get Tools

> **⚠️ Beta Package** - This is a beta release. Features may change and improvements are ongoing. Please report any issues to support@tuflow.com.

**Tools to assist with downloading and processing meteorological and ocean data to use with TUFLOW FV**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Project Status: Active](https://img.shields.io/badge/Project%20Status-Active-green.svg)](https://github.com/your-repo/tfv-get-tools)

## Overview

TFV Get Tools is a Python package that simplifies the process of downloading and processing meteorological and ocean data for use with TUFLOW FV models. The tool supports extraction of tidal data, atmospheric conditions, ocean physics, and wave data from various authoritative sources.

### Supported Data Sources

**Atmospheric Data:**
- [ECMWF ERA5](https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5) (*Atmos Default* - registration required, see [CDS API](https://cds.climate.copernicus.eu/api-how-to))
- [NOAA CFSR](https://www.ncei.noaa.gov/data/climate-forecast-system/) (Climate Forecast System Reanalysis)
- [BARRA2](http://www.bom.gov.au/research/projects/reanalysis/) (Australian Bureau of Meteorology)

**Ocean Data:**
- [HYCOM](https://www.hycom.org/) (*Ocean Default* Naval Research Laboratory - Global Ocean Forecast System)
- [Copernicus Marine](https://marine.copernicus.eu/) Global and NWS (registration required, see [Copernicus Marine Service](https://marine.copernicus.eu/))

**Wave Data:**
- [CSIRO CAWCR](https://data.csiro.au/collection/csiro:39819) (*Wave Default* glob_24m, aus_10m, aus_4m, pac_10m, pac_4m)
- [Copernicus Marine](https://marine.copernicus.eu/) Global and NWS
- [ECMWF ERA5](https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5) (registration required, see [CDS API](https://cds.climate.copernicus.eu/api-how-to))

**Tidal Data:**
- [FES2014](https://www.aviso.altimetry.fr/en/data/products/auxiliary-products/global-tide-fes.html) (AVISO+ Finite Element Solution 2014)
- [FES2022](https://www.aviso.altimetry.fr/en/data/products/auxiliary-products/global-tide-fes.html) (*Tide Default* AVISO+ Finite Element Solution 2022)

## Installation

### Conda/Mamba (Recommended)

```bash
# Create a new environment, if required. 
conda create -n tfv python=3.9
conda activate tfv

# Install the package
conda install -c conda-forge tfv-get-tools
```

### Pip

```bash
pip install tfv-get-tools
```

## Quick Start

### Command Line Interface

The package provides command-line tools for downloading and processing data:

**Ocean Data Example:**
```bash
# Download HYCOM data for January 2011 in southeast Queensland
GetOcean A 2011-01-01 2011-02-01 153 156 -29 -24

# Download with custom options (top 20m, 3-hourly data, custom prefix)
GetOcean A -p raw_data -pf SEQ_HYCOM -ts 3 -z 0 20 2011-01-01 2011-02-01 153 156 -29 -24

# Merge downloaded files
GetOcean B -i raw_data -o output -rp 28350 -tz 8 -ltz AWST -n merged_hycom.nc
```

**Atmospheric Data Example:**
```bash
# Download ERA5 atmospheric data
GetAtmos A 2011-01-01 2011-02-01 152 154 -28 -26

# Merge with reprojection and timezone conversion
GetAtmos B -i raw_data -o output -rp 7856 -tz 10 -ltz AEST
```

**Tidal Data Example:**
```bash
# Extract tidal data using a boundary nodestring shapefile
GetTide output/tide_data.nc 2011-01-01 2012-01-01 boundaries/nodestring.shp path/to/fes2022/
```

### Python API

**Ocean Data:**
```python
from tfv_get_tools import DownloadOcean, MergeOcean

# Download HYCOM data
result = DownloadOcean(
    start_date='2011-01-01',
    end_date='2011-02-01',
    xlims=(153, 156),
    ylims=(-29, -24),
    out_path='./raw_data',
    source='HYCOM',
    time_interval=24
)

# Merge downloaded files
MergeOcean(
    in_path='./raw_data',
    out_path='./output',
    source='HYCOM',
    reproject=28350,
    local_tz=(8, 'AWST')
)
```

**Atmospheric Data:**
```python
from tfv_get_tools import DownloadAtmos, MergeAtmos

# Download BARRA2 data
result = DownloadAtmos(
    start_date='2020-01-01',
    end_date='2020-02-01',
    xlims=(152.72, 153.78),
    ylims=(-27.49, -25.39),
    out_path='./raw_data',
    source='BARRA2',
    model='C2'
)

# Merge with reprojection to GDA2020 MGA56
MergeAtmos(
    in_path='./raw_data',
    out_path='./output',
    source='BARRA2',
    model='C2',
    reproject=7856,
    local_tz=(10.0, 'AEST')
)
```

**Tidal Data:**
```python
from pathlib import Path
from tfv_get_tools.tide import ExtractTide

# Basic tidal extraction
ExtractTide(
    start_date='2011-01-01',
    end_date='2012-01-01',
    filename='tide_data.nc',
    out_path='./output',
    freq='15min',
    shapefile='boundaries/nodestring.shv'
)

# Advanced usage with constituent caching
from tfv_get_tools.tide import load_nodestring_shapefile, process_nodestring_gdf, get_constituents

# Load and process boundary shapefile
gdf = load_nodestring_shapefile('boundaries/nodestring.shp', process_ids=[1])
coordinates = process_nodestring_gdf(gdf, spacing=5000)

# Extract constituents once (slow first time, fast afterwards)
constituents = get_constituents(
    coordinates,
    source='FES2022',
    save_cons='boundary_constituents.pkl'
)

# Use cached constituents for faster extraction
ExtractTide(
    start_date='2011-01-01',
    end_date='2012-01-01',
    filename='tide_data.nc',
    out_path='./output',
    freq='15min',
    constituents='boundary_constituents.pkl'
)
```

## Requirements

- Python 3.9+
- Internet connection for data downloads
- Registration required for some data sources:
  - **ERA5**: [Copernicus Climate Data Store (CDS) API](https://cds.climate.copernicus.eu/api-how-to)
  - **Copernicus Marine**: [Copernicus Marine Service](https://marine.copernicus.eu/)
  - **FES Tidal Models**: [AVISO+](https://www.aviso.altimetry.fr/en/data/products/auxiliary-products/global-tide-fes.html) (for tidal constituent files)

## Data Credits and Acknowledgements

This package utilises data from multiple authoritative sources. Please ensure appropriate attribution when using this data:

### Atmospheric Data
- **ECMWF ERA5**: Data provided by the [European Centre for Medium-Range Weather Forecasts (ECMWF)](https://www.ecmwf.int/) through the Copernicus Climate Change Service (C3S). Please acknowledge: "Contains modified Copernicus Climate Change Service information [2025]".
- **NOAA CFSR**: Data provided by the [National Oceanic and Atmospheric Administration (NOAA)](https://www.noaa.gov/) National Centers for Environmental Information.
- **BARRA2**: Data provided by the [Australian Bureau of Meteorology](http://www.bom.gov.au/).

### Ocean Data
- **HYCOM**: All ocean data is supplied by the [HYCOM consortium](https://www.hycom.org/). Please refer to the [HYCOM data acknowledgement and disclaimer](https://www.hycom.org/publications/acknowledgements/hycom-data).
- **Copernicus Marine**: Ocean and wave data provided by the [Copernicus Marine Environment Monitoring Service (CMEMS)](https://marine.copernicus.eu/).

### Wave Data
- **CSIRO CAWCR**: Wave data provided by the [Commonwealth Scientific and Industrial Research Organisation (CSIRO)](https://www.csiro.au/) Centre for Australian Weather and Climate Research.
- **Copernicus Marine**: Wave data provided by the [Copernicus Marine Environment Monitoring Service (CMEMS)](https://marine.copernicus.eu/).

### Tidal Data
- **FES Tidal Models**: Tidal data provided by [AVISO+](https://www.aviso.altimetry.fr/) and the FES development team. FES2014 and FES2022 are products of Noveltis, Legos, and CLS, with support from CNES.
- **PyTMD**: This package utilises the [PyTMD](https://github.com/tsutterley/pyTMD) Python package for tidal analysis and prediction, developed by Tyler Sutterley.

## Support

For questions, bug reports, or feature requests:
- 📧 **Email**: support@tuflow.com
- 🐛 **Issues**: Submit via the project repository

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes with appropriate tests
4. Submit a pull request
5. Email support@tuflow.com to notify the development team

Please ensure your code follows the project's coding standards and includes appropriate documentation.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

Developed by [TUFLOW](https://www.tuflow.com/), 2025

## Project Status

**Active** - This project is actively maintained and in use. For update requests or feature suggestions, please email support@tuflow.com.

---

*Last updated: July 2025*