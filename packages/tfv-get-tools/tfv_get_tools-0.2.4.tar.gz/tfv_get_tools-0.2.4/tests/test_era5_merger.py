"""
Set of ERA5 tests focussing on problems we've had in the past.
- Longitude wrapping on the merger.
    (The downloader is fine because CDSAPI works with anything as long as it's West->East. )
- Local timezones are added correctly with attributes
- Reprojection works by adding new x/y variables but maintaining longitude, latitude

"""

import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from synthetic_data import create_test_dataset_for_source
from tfv_get_tools import MergeAtmos


class TestERA5LongtitudeWrapping:
    """Test that ERA5 doesn't go all skitz mix on us when we try to merge across different longitudes."""

    def setup_method(self):
        """Set up temporary directories for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.in_path = Path(self.temp_dir) / "raw"
        self.out_path = Path(self.temp_dir) / "output"
        self.in_path.mkdir()
        self.out_path.mkdir()

    def teardown_method(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)

    def _create_test_files(
        self,
        num_files: int = 6,
        time_start: str = "2022-01-01",
        lon=None,
        lat=None,
        **kwargs,
    ):
        """Helper to create ERA5 synthetic netcdf datasets for longitude wrap battles"""
        start_timestamp = pd.Timestamp(time_start)

        # Monthly files - generate month start/end pairs
        month_ranges = pd.date_range(
            start=start_timestamp, periods=num_files, freq="MS"
        )

        for month_start in month_ranges:
            month_end = month_start + pd.offsets.MonthEnd(0)
            start_date = month_start.strftime("%Y-%m-%d")
            end_date = month_end.strftime("%Y-%m-%d")

            ds = create_test_dataset_for_source(
                "ERA5_ATMOS",
                start_date=start_date,
                end_date=end_date,
                lon=lon,
                lat=lat,
                **kwargs,
            )

            filename = f"ERA5_ATMOS_{month_start.strftime('%Y%m%d')}_{month_end.strftime('%Y%m%d')}.nc"

            ds.to_netcdf(self.in_path / filename)

    def test_era5_basic_merge(self):
        """Test basic ERA5 merge with standard longitude range."""
        self._create_test_files(
            num_files=2, lon=np.linspace(135, 165, 7), lat=np.linspace(-45, -25, 8)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            wrapto360=False,
        )

        # Check longitude range is maintained
        assert ds.longitude.min() >= 135
        assert ds.longitude.max() <= 165
        assert len(ds.longitude) == 7
        assert len(ds.latitude) == 8

    def test_era5_prime_meridian_crossing(self):
        """Test longitude wrapping across prime meridian (0°)."""
        self._create_test_files(
            num_files=3, lon=np.linspace(-15, 15, 10), lat=np.linspace(45, 65, 6)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            wrapto360=False,
        )

        # Should maintain negative and positive longitudes
        assert ds.longitude.min() < 0
        assert ds.longitude.max() > 0
        assert len(ds.longitude) == 10

    def test_era5_dateline_crossing(self):
        """Test longitude wrapping across international date line (180°/-180°)."""
        self._create_test_files(
            num_files=2, lon=np.linspace(170, -170, 8), lat=np.linspace(-20, 0, 5)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            wrapto360=False,
        )

        # Check that dateline crossing is handled properly
        assert len(ds.longitude) == 8
        lons = ds.longitude.values
        assert np.all(lons <= 170)
        assert np.all(lons >= -170)

    def test_era5_wrapto360_false(self):
        """Test longitude handling with wrapto360=False (default)."""
        self._create_test_files(
            num_files=2, lon=np.linspace(-180, 180, 12), lat=np.linspace(-30, 30, 8)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            wrapto360=False,
        )

        # Should maintain -180 to 180 range
        assert ds.longitude.min() >= -180
        assert ds.longitude.max() <= 180
        assert np.any(ds.longitude < 0)

    def test_era5_wrapto360_true(self):
        """Test longitude handling with wrapto360=True."""
        self._create_test_files(
            num_files=2, lon=np.linspace(-180, 180, 12), lat=np.linspace(-30, 30, 8)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            wrapto360=True,
        )

        # Should convert to 0-360 range
        assert ds.longitude.min() >= 0
        assert ds.longitude.max() <= 360
        assert np.all(ds.longitude >= 0)

    def test_era5_complex_dateline_wrapto360_false(self):
        """Test complex dateline crossing with wrapto360=False."""
        # Create longitude array that crosses dateline multiple times
        lon_vals = np.array([170, 175, 180, -175, -170, -165, 160, 165])

        self._create_test_files(num_files=2, lon=lon_vals, lat=np.linspace(10, 30, 6))

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            wrapto360=False,
        )

        # Should maintain original longitude structure
        assert len(ds.longitude) == len(lon_vals)
        assert np.any(ds.longitude > 160)
        assert np.any(ds.longitude < -160)

    def test_era5_complex_dateline_wrapto360_true(self):
        """Test complex dateline crossing with wrapto360=True."""
        lon_vals = np.array([170, 175, 180, -175, -170, -165, 160, 165])

        self._create_test_files(num_files=2, lon=lon_vals, lat=np.linspace(10, 30, 6))

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            wrapto360=True,
        )

        # All longitudes should be in 0-360 range
        assert np.all(ds.longitude >= 0)
        assert np.all(ds.longitude <= 360)
        assert len(ds.longitude) == len(lon_vals)


class TestERA5ProjectedCoordinates:
    """Test ERA5 reprojection functionality."""

    def setup_method(self):
        """Set up temporary directories for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.in_path = Path(self.temp_dir) / "raw"
        self.out_path = Path(self.temp_dir) / "output"
        self.in_path.mkdir()
        self.out_path.mkdir()

    def teardown_method(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)

    def _create_test_files(
        self,
        num_files: int = 2,
        time_start: str = "2022-01-01",
        lon=None,
        lat=None,
        **kwargs,
    ):
        """Helper to create ERA5 synthetic netcdf datasets."""
        start_timestamp = pd.Timestamp(time_start)

        month_ranges = pd.date_range(
            start=start_timestamp, periods=num_files, freq="MS"
        )

        for month_start in month_ranges:
            month_end = month_start + pd.offsets.MonthEnd(0)
            start_date = month_start.strftime("%Y-%m-%d")
            end_date = month_end.strftime("%Y-%m-%d")

            ds = create_test_dataset_for_source(
                "ERA5_ATMOS",
                start_date=start_date,
                end_date=end_date,
                lon=lon,
                lat=lat,
                **kwargs,
            )

            filename = f"ERA5_ATMOS_{month_start.strftime('%Y%m%d')}_{month_end.strftime('%Y%m%d')}.nc"
            ds.to_netcdf(self.in_path / filename)

    def test_era5_no_reprojection(self):
        """Test that without reprojection, only lon/lat coordinates exist."""
        self._create_test_files(
            lon=np.linspace(145, 155, 5), lat=np.linspace(-40, -30, 4)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            reproject=None,
        )

        # Should have original coordinates
        assert "longitude" in ds.coords
        assert "latitude" in ds.coords
        # Should not have projected coordinates
        assert "x" not in ds.coords
        assert "y" not in ds.coords

    def test_era5_mga_reprojection(self):
        """Test reprojection with some Aussie coords (EPSG:7855 - GDA2020 / MGA Zone 55)."""
        # Australian region coordinates
        self._create_test_files(
            lon=np.linspace(148, 152, 5), lat=np.linspace(-38, -34, 4)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            reproject=7855,  # MGA 55 
        )

        # Should maintain original coordinates
        assert "longitude" in ds.coords
        assert "latitude" in ds.coords
        # Should add projected coordinates
        assert "x" in ds.coords
        assert "y" in ds.coords

        # Check that x/y values are in reasonable range
        assert ds.x.min() > 500000  # easting values
        assert ds.x.max() < 1000000
        assert ds.y.min() > 5000000  # northing values
        assert ds.y.max() < 7000000
        
        # Let's see that the attrs look good
        assert ds.x.attrs['axis'] == 'X'
        assert ds.y.attrs['axis'] == 'Y'
        
        assert ds.x.attrs['long_name'] == 'Easting'
        assert ds.x.attrs['standard_name'] == 'projection_x_coordinate'
        
        assert ds.y.attrs['long_name'] == 'Northing'
        assert ds.y.attrs['standard_name'] == 'projection_y_coordinate'
        
        assert ds.x.attrs['units'] == 'metre'
        assert ds.x.attrs['epsg'] == 7855
        assert ds.x.attrs['name'] == 'GDA2020 / MGA zone 55'


    def test_era5_reprojection_with_wrapto360(self):
        """Test reprojection combined with longitude wrapping."""
        self._create_test_files(
            lon=np.linspace(-180, 180, 8), lat=np.linspace(-45, -35, 4)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            reproject=32755,  # UTM Zone 55S
            wrapto360=True,
        )

        # Should have both coordinate systems
        assert "longitude" in ds.coords
        assert "latitude" in ds.coords
        assert "x" in ds.coords
        assert "y" in ds.coords

        # Longitude should be wrapped to 0-360
        assert np.all(ds.longitude >= 0)
        assert np.all(ds.longitude <= 360)


class TestERA5LocalTimezone:
    """Test ERA5 local timezone functionality."""

    def setup_method(self):
        """Set up temporary directories for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.in_path = Path(self.temp_dir) / "raw"
        self.out_path = Path(self.temp_dir) / "output"
        self.in_path.mkdir()
        self.out_path.mkdir()

    def teardown_method(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)

    def _create_test_files(
        self,
        num_files: int = 2,
        time_start: str = "2022-01-01",
        lon=None,
        lat=None,
        **kwargs,
    ):
        """Helper to create ERA5 synthetic netcdf datasets."""
        start_timestamp = pd.Timestamp(time_start)

        month_ranges = pd.date_range(
            start=start_timestamp, periods=num_files, freq="MS"
        )

        for month_start in month_ranges:
            month_end = month_start + pd.offsets.MonthEnd(0)
            start_date = month_start.strftime("%Y-%m-%d")
            end_date = month_end.strftime("%Y-%m-%d")

            ds = create_test_dataset_for_source(
                "ERA5_ATMOS",
                start_date=start_date,
                end_date=end_date,
                lon=lon,
                lat=lat,
                **kwargs,
            )

            filename = f"ERA5_ATMOS_{month_start.strftime('%Y%m%d')}_{month_end.strftime('%Y%m%d')}.nc"
            ds.to_netcdf(self.in_path / filename)

    def test_era5_no_local_timezone(self):
        """Test that without local_tz, no timezone variables are added."""
        self._create_test_files(
            lon=np.linspace(145, 155, 5), lat=np.linspace(-40, -30, 4)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            local_tz=None,
        )

        # Should not have local timezone variables
        assert "local_time" not in ds.coords
        assert "local_time" not in ds.data_vars

        # Check that no timezone attributes are present
        time_attrs = ds.time.attrs
        assert "tz" in time_attrs
        assert time_attrs["tz"] == "UTC"

    def test_era5_australian_timezone(self):
        """Test Australian Eastern Standard Time (AEST) timezone."""
        self._create_test_files(
            lon=np.linspace(145, 155, 5), lat=np.linspace(-40, -30, 4)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            local_tz=(10.0, "AEST"),  # +10 hours
        )

        # First assert the time attribute is still UTC
        time_attrs = ds.time.attrs
        assert "tz" in time_attrs
        assert time_attrs["tz"] == "UTC"
        
        # Now we should have a hotdangin local_time variable
        assert 'local_time' in ds.coords
        local_time_attrs = ds.local_time.attrs
        assert local_time_attrs["tz"] == "AEST"
        
        # Also check the offset worked in the correct direction.
        assert ds['local_time'][0].values - pd.Timedelta('10h') == ds['time'][0].values

    def test_era5_negative_timezone_offset(self):
        """Test negative timezone offset (e.g., US Pacific Time)."""
        self._create_test_files(
            lon=np.linspace(-125, -115, 5), lat=np.linspace(32, 42, 4)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            local_tz=(-8.0, "PST"),  # -8 hours
        )

        # Check timezone attributes
        time_attrs = ds.local_time.attrs
        assert time_attrs["tz"] == "PST"

    def test_era5_fractional_timezone_offset(self):
        """Test fractional timezone offset (e.g., Adelaide, Australia)."""
        self._create_test_files(
            lon=np.linspace(138, 142, 3), lat=np.linspace(-36, -34, 3)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            local_tz=(9.5, "ACST"),  # +9.5 hours
        )

        # Check fractional timezone handling
        time_attrs = ds.local_time.attrs
        assert time_attrs["tz"] == "ACST"

    def test_era5_timezone_with_reprojection(self):
        """Test local timezone combined with reprojection."""
        self._create_test_files(
            lon=np.linspace(145, 155, 5), lat=np.linspace(-40, -30, 4)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            local_tz=(10.0, "AEST"),
            reproject=32755,  # UTM Zone 55S
        )

        # Should have both timezone and projection features
        assert "x" in ds.coords
        assert "y" in ds.coords
        time_attrs = ds.local_time.attrs
        assert "tz" in time_attrs

    def test_era5_timezone_with_longitude_wrapping(self):
        """Test local timezone combined with longitude wrapping."""
        self._create_test_files(
            lon=np.linspace(170, -170, 6), lat=np.linspace(-50, -40, 4)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            local_tz=(12.0, "NZST"),  # New Zealand Standard Time
            wrapto360=True,
        )

        # Should handle both timezone and longitude wrapping
        assert np.all(ds.longitude >= 0)
        assert np.all(ds.longitude <= 360)
        time_attrs = ds.local_time.attrs
        assert time_attrs["tz"] == "NZST"


class TestERA5ComprehensiveIntegration:
    """Integration tests combining multiple features."""

    def setup_method(self):
        """Set up temporary directories for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.in_path = Path(self.temp_dir) / "raw"
        self.out_path = Path(self.temp_dir) / "output"
        self.in_path.mkdir()
        self.out_path.mkdir()

    def teardown_method(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)

    def _create_test_files(
        self,
        num_files: int = 2,
        time_start: str = "2022-01-01",
        lon=None,
        lat=None,
        **kwargs,
    ):
        """Helper to create ERA5 synthetic netcdf datasets."""
        start_timestamp = pd.Timestamp(time_start)

        month_ranges = pd.date_range(
            start=start_timestamp, periods=num_files, freq="MS"
        )

        for month_start in month_ranges:
            month_end = month_start + pd.offsets.MonthEnd(0)
            start_date = month_start.strftime("%Y-%m-%d")
            end_date = month_end.strftime("%Y-%m-%d")

            ds = create_test_dataset_for_source(
                "ERA5_ATMOS",
                start_date=start_date,
                end_date=end_date,
                lon=lon,
                lat=lat,
                **kwargs,
            )

            filename = f"ERA5_ATMOS_{month_start.strftime('%Y%m%d')}_{month_end.strftime('%Y%m%d')}.nc"
            ds.to_netcdf(self.in_path / filename)

    def test_era5_all_features_combined(self):
        """Test all features together: dateline crossing + reprojection + timezone + wrapto360."""
        # Create data crossing dateline
        self._create_test_files(
            num_files=3, lon=np.linspace(175, -175, 8), lat=np.linspace(-45, -35, 6)
        )

        ds = MergeAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            write=False,
            wrapto360=True,
            reproject=32760,  # UTM Zone 60S (covers NZ/Pacific)
            local_tz=(12.0, "NZST"),
        )

        # Check all features are applied correctly
        # Longitude wrapping
        assert np.all(ds.longitude >= 0)
        assert np.all(ds.longitude <= 360)

        # Reprojection
        assert "x" in ds.coords
        assert "y" in ds.coords
        assert "longitude" in ds.coords  # Original coords maintained
        assert "latitude" in ds.coords

        # Timezone
        time_attrs = ds.time.attrs
        assert time_attrs["tz"] == "UTC"
        
        # Local timezone
        local_time_attrs = ds.local_time.attrs
        assert local_time_attrs["tz"] == "NZST"

        # Coords
        assert len(ds.longitude) == 8
        assert len(ds.latitude) == 6
        
        assert 'x' in ds.coords
        assert 'y' in ds.coords
        assert ds['x'].attrs['name'] == 'WGS 84 / UTM zone 60S'
        
        assert ds['longitude'].attrs['axis'] == 'X'
        assert ds['longitude'].attrs['epsg'] == 4326


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
