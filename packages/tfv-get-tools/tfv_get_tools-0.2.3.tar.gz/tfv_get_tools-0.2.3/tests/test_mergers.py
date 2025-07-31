"""
Comprehensive test suite for data merger classes.

Uses synthetic data to test core functionality without requiring large test files.
"""

import shutil
import tempfile
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from synthetic_data import create_multi_day_datasets, create_test_dataset_for_source
from tfv_get_tools.providers.atmos.barra2 import MergeBARRA2
from tfv_get_tools.providers.atmos.cfsr import MergeCFSRAtmos
from tfv_get_tools.providers.atmos.era5 import MergeERA5Atmos
from tfv_get_tools.providers.ocean.hycom import MergeHYCOM
from tfv_get_tools.providers.wave.cawcr import MergeCAWCR


class TestSyntheticDataSetup:
    """Test the synthetic data generation works correctly."""
    
    def test_synthetic_era5_structure(self):
        """Test ERA5 synthetic data has correct structure."""
        ds = create_test_dataset_for_source(
            'ERA5_ATMOS', 
            start_date='2022-01-01', 
            end_date='2022-01-03'
        )
        
        # Check ERA5-specific coordinate naming
        assert 'valid_time' in ds.coords
        assert 'latitude' in ds.coords
        assert 'longitude' in ds.coords
        
        # Check has multiple variables
        assert len(ds.data_vars) > 1
        assert 'avg_tmp2m' in ds.data_vars
        
        # Check time dimension
        assert len(ds.valid_time) == 49  # 3 days hourly + 1

    def test_synthetic_hycom_structure(self):
        """Test HYCOM synthetic data has correct structure."""
        ds = create_test_dataset_for_source('HYCOM_OCEAN', date='2022-01-01')
        
        # Check coordinates
        assert 'time' in ds.coords
        assert 'lat' in ds.coords
        assert 'lon' in ds.coords
        assert 'depth' in ds.coords
        
        # Check 3D variables have depth
        assert 'water_temp' in ds.data_vars
        assert 'depth' in ds['water_temp'].dims
        
        # Check 2D variable (surface elevation)
        assert 'surf_el' in ds.data_vars
        assert 'depth' not in ds['surf_el'].dims
        
        # Check 8 timesteps per day (3-hourly)
        assert len(ds.time) == 8


class TestMergerIntegration:
    """Integration tests using synthetic data."""
    
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
        self, source: str, num_files: int = 3, time_start: str = "2022-01-01", model: str = "default", **kwargs
    ):
        """Helper to create synthetic netcdf datasets that look close enough to real raw datasets."""
        start_timestamp = pd.Timestamp(time_start)
        
        if source == "HYCOM_OCEAN":
            # HYCOM uses daily files
            datasets = create_multi_day_datasets(time_start, num_days=num_files)
            for i, ds in enumerate(datasets):
                date_str = (start_timestamp + timedelta(days=i)).strftime("%Y%m%d")
                filename = f"HYCOM_OCEAN_{date_str}_0000.nc"
                ds.to_netcdf(self.in_path / filename)

        elif source in ["ERA5_ATMOS", "ERA5_WAVE", "CAWCR_WAVE"]:
            # Monthly files - generate month start/end pairs
            month_ranges = pd.date_range(
                start=start_timestamp, periods=num_files, freq="MS"
            )
            
            for i, month_start in enumerate(month_ranges):
                month_end = month_start + pd.offsets.MonthEnd(0)
                start_date = month_start.strftime("%Y-%m-%d")
                end_date = month_end.strftime("%Y-%m-%d")
                
                ds = create_test_dataset_for_source(
                    source, start_date=start_date, end_date=end_date
                )
                
                if source == "ERA5_ATMOS":
                    filename = f"ERA5_ATMOS_{month_start.strftime('%Y%m%d')}_{month_end.strftime('%Y%m%d')}.nc"
                elif source == "ERA5_WAVE":
                    filename = f"ERA5_WAVE_{month_start.strftime('%Y%m%d')}_{month_end.strftime('%Y%m%d')}.nc"
                elif source == "CAWCR_WAVE":
                    model_str = "GLOB_24M" if model == "default" else model
                    filename = f"CAWCR_WAVE_{model_str}_{month_start.strftime('%Y%m%d')}_{month_end.strftime('%Y%m%d')}.nc"
                
                ds.to_netcdf(self.in_path / filename)

        elif source in ["CFSR_ATMOS", "BARRA2_ATMOS"]:
            # Variable-specific files with month ranges
            variables = kwargs.get("variables", ["tmp2m"])
            month_ranges = pd.date_range(
                start=start_timestamp, periods=num_files, freq="MS"
            )
            
            for var in variables:
                for month_start in month_ranges:
                    month_end = month_start + pd.offsets.MonthEnd(0)
                    start_date = month_start.strftime("%Y-%m-%d")
                    end_date = month_end.strftime("%Y-%m-%d")
                    
                    ds = create_test_dataset_for_source(
                        source, variable=var, start_date=start_date, end_date=end_date
                    )
                    
                    if source == "CFSR_ATMOS":
                        filename = f"CFSR_ATMOS_{var.upper()}_{month_start.strftime('%Y%m%d')}_{month_end.strftime('%Y%m%d')}.nc"
                    else:  # BARRA2_ATMOS
                        model_str = "R2" if model == "default" else model
                        filename = f"BARRA2_ATMOS_{model_str}_{var.upper()}_{month_start.strftime('%Y%m%d')}_{month_end.strftime('%Y%m%d')}.nc"
                    
                    ds.to_netcdf(self.in_path / filename)

    def test_era5_atmos_merge(self):
        """Test ERA5 atmospheric data merging."""
        self._create_test_files('ERA5_ATMOS', num_files=2)
        
        merger = MergeERA5Atmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="ERA5",
            mode="ATMOS",
            execute=False,
            verbose=False
        )
        
        file_list = merger.get_file_list()
        assert len(file_list) == 2
        
        merged_ds, skipped = merger.merge_files(file_list)
        
        # Check merge worked
        assert len(skipped) == 0
        assert 'time' in merged_ds.coords  # Should be renamed from valid_time
        assert len(merged_ds.time) > 48  # At least 2 days of hourly data
        
        # Check no duplicates
        time_diffs = np.diff(merged_ds.time.values)
        assert not np.any(time_diffs == np.timedelta64(0, 'ns'))

    def test_cawcr_wave_merge(self):
        """Test CAWCR wave data merging."""
        self._create_test_files('CAWCR_WAVE', num_files=2)
        
        merger = MergeCAWCR(
            in_path=self.in_path,
            out_path=self.out_path,
            source="CAWCR",
            mode="WAVE",
            model="glob_24m",
            execute=False,
            verbose=False
        )
        
        file_list = merger.get_file_list()
        assert len(file_list) == 2
        
        merged_ds, skipped = merger.merge_files(file_list)
        
        # Check wave variables present
        assert 'hs' in merged_ds.data_vars or any('wave' in var.lower() for var in merged_ds.data_vars)
        assert len(skipped) == 0

    def test_cfsr_atmos_merge(self):
        """Test CFSR atmospheric data merging with multiple variables."""
        self._create_test_files('CFSR_ATMOS', num_files=2, variables=['tmp2m', 'wnd10m'])
        
        merger = MergeCFSRAtmos(
            in_path=self.in_path,
            out_path=self.out_path,
            source="CFSR",
            mode="ATMOS",
            execute=False,
            verbose=False
        )
        
        file_list = merger.get_file_list()
        assert len(file_list) == 4  # 2 variables × 2 time periods
        
        merged_ds, skipped = merger.merge_files(file_list)
        
        # Check variables were merged
        assert len(merged_ds.data_vars) >= 2
        assert 'longitude' in merged_ds.coords  # Should be renamed from lon
        assert 'latitude' in merged_ds.coords   # Should be renamed from lat

    def test_hycom_ocean_merge(self):
        """Test HYCOM ocean data merging."""
        self._create_test_files('HYCOM_OCEAN', num_files=3)
        
        merger = MergeHYCOM(
            in_path=self.in_path,
            out_path=self.out_path,
            source="HYCOM",
            mode="OCEAN",
            execute=False,
            verbose=False
        )
        
        file_list = merger.get_file_list()
        assert len(file_list) == 3
        
        merged_ds, skipped = merger.merge_files(file_list)
        
        # Check 3D and 2D variables
        assert 'surf_el' in merged_ds.data_vars
        assert 'water_temp' in merged_ds.data_vars
        assert 'depth' in merged_ds['water_temp'].dims
        assert 'depth' not in merged_ds['surf_el'].dims
        
        # Check time concatenation (3 days × 8 timesteps)
        assert len(merged_ds.time) == 24

    def test_barra2_atmos_merge(self):
        """Test BARRA2 atmospheric data merging.
        AEW - This assumes BARRA2 R2! We could add more tests for submodels..."""
        self._create_test_files('BARRA2_ATMOS', num_files=5, variables=['uasmean', 'psl'])
        
        merger = MergeBARRA2(
            in_path=self.in_path,
            out_path=self.out_path,
            source="BARRA2",
            mode="ATMOS",
            execute=False,
            verbose=False
        )
        
        file_list = merger.get_file_list()
        merged_ds, skipped = merger.merge_files(file_list)
        
        assert len(skipped) == 0
        assert 'psl' in merged_ds.data_vars
        
    def test_empty_file_list(self):
        """Test error handling with empty file list."""
        merger = MergeERA5Atmos(
            in_path=self.in_path,
            out_path=self.out_path,
            execute=False,
            verbose=False
        )
        
        with pytest.raises(ValueError, match="No files provided"):
            merger.merge_files([])
        
    def test_corrupted_file_handling(self):
        """Test handling of corrupted/unreadable files.
        We use ERA5 as an example and we'll bust one up. """
        
        # First we need to make a bunch of synthetic fellas to merge
        self._create_test_files('ERA5_ATMOS', num_files=3)
        
        # Bust one of em up - let's ruin the first one. 
        corrupted_file = self.in_path / "ERA5_ATMOS_20220101_20220131.nc"
        with open(corrupted_file, 'w') as f:
            f.write("Hmmmm! This ain't what I expected?")
        
        merger = MergeERA5Atmos(
            in_path=self.in_path,
            out_path=self.out_path,
            execute=False,
            verbose=False
        )
        
        file_list = merger.get_file_list()
        merged_ds, skipped = merger.merge_files(file_list)
        
        # Should skip the corrupted file
        assert len(skipped) == 1
        assert skipped[0].name == "ERA5_ATMOS_20220101_20220131.nc"
        
    def test_invalid_time_coordinates(self):
        """Test handling files with invalid time coordinates.
        Pretty much as above but we actually have a netcdf that looks close enough to being usable."""
        
        # First we need to make a bunch of synthetic fellas to merge
        self._create_test_files('ERA5_ATMOS', num_files=3)
        
        # Now we bust up the first one, but this time with a real netcdf
        # but messed up time. 

        ds = xr.Dataset(
            {'temp': (('lat', 'lon'), np.random.randn(5, 5))},
            coords={'lon': range(5), 'lat': range(5), 'valid_time': ['invalid', 'time', 'values']}
        )
        
        invalid_file = self.in_path / "ERA5_ATMOS_20220101_20220131.nc"
        ds.to_netcdf(invalid_file)
        
        merger = MergeERA5Atmos(
            in_path=self.in_path,
            out_path=self.out_path,
            execute=False,
            verbose=False
        )
        
        file_list = merger.get_file_list()
        merged_ds, skipped = merger.merge_files(file_list)
        
        # Should skip file with invalid time
        assert len(skipped) == 1


class TestFileHandling:
    """Test file discovery and filtering."""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.in_path = Path(self.temp_dir) / "raw"
        self.out_path = Path(self.temp_dir) / "output"
        self.in_path.mkdir()
        self.out_path.mkdir()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_file_pattern_matching(self):
        """Test that file patterns are correctly identified."""
        # Create various files
        test_files = [
            "ERA5_ATMOS_20220101_20220131.nc",
            "HYCOM_OCEAN_GLO_20220101_0000.nc", 
            "CAWCR_WAVE_GLOB_24M_20220101_20220131.nc",
            "RANDOM_FILE.nc",
            "ERA5_WAVE_20220101_20220131.nc"
        ]
        
        for filename in test_files:
            (self.in_path / filename).touch()
        
        # Test ERA5 pattern matching
        merger = MergeERA5Atmos(
            in_path=self.in_path,
            out_path=self.out_path,
            execute=False,
            verbose=False
        )
        
        files = merger.get_file_list()
        era5_files = [f.name for f in files]
        
        assert "ERA5_ATMOS_20220101_20220131.nc" in era5_files
        assert "RANDOM_FILE.nc" not in era5_files
        assert "ERA5_WAVE_20220101_20220131.nc" not in era5_files

    def test_time_filtering_simple_ERA5(self):
        """Test filtering files by time range."""
        # Create files with different dates
        test_files = [
            "ERA5_ATMOS_20220101_20220131.nc",
            "ERA5_ATMOS_20220201_20220228.nc", 
            "ERA5_ATMOS_20220301_20220331.nc"
        ]
        
        for filename in test_files:
            (self.in_path / filename).touch()
        
        # Test filtering with time constraints
        merger = MergeERA5Atmos(
            in_path=self.in_path,
            out_path=self.out_path,
            time_start="2022-01-15",
            time_end="2022-02-15",
            execute=False,
            verbose=False
        )
        
        files = merger.get_file_list()
        filtered_files = [f.name for f in files]
        
        # Should include Jan and Feb files
        assert "ERA5_ATMOS_20220101_20220131.nc" in filtered_files
        assert "ERA5_ATMOS_20220201_20220228.nc" in filtered_files
        # Should exclude March file
        assert "ERA5_ATMOS_20220301_20220331.nc" not in filtered_files
        
    def test_time_filtering_painful_HYCOM(self):
        """Test filtering files by time range."""
        # Create files with different dates
        test_files = [
            "HYCOM_OCEAN_20220101_03h.nc",
            "HYCOM_OCEAN_20220102_03h_somedbase.nc",
            "A_LONG_PREFIX_BOUND_TO_GET_YA_HYCOM_OCEAN_20220103_03h_somedbase.nc",
            "KEEP_ME_HYCOM_OCEAN_20210101_03h.nc",
            "EXCLUDE_ME_HYCOM_OCEAN_20230101_03h.nc",
            "WHY_DID_I_EVER_ALLOW_SUCH_FLEXIBILITY_HYCOM_OCEAN_20220301_03h.nc",
        ]
        
        for filename in test_files:
            (self.in_path / filename).touch()
        
        # Test filtering with time constraints
        merger = MergeHYCOM(
            in_path=self.in_path,
            out_path=self.out_path,
            time_start="2021-01-01", # Keep em all except the EXCLUDE_ME one
            time_end="2022-09-01",
            execute=False,
            verbose=False
        )
        
        files = merger.get_file_list()
        filtered_files = [f.name for f in files]
        
        # Should include Jan and Feb files
        assert "KEEP_ME_HYCOM_OCEAN_20210101_03h.nc" in filtered_files
        
        # Should exclude March file
        assert "EXCLUDE_ME_HYCOM_OCEAN_20230101_03h.nc" not in filtered_files
        

    def test_no_files_found_error(self):
        """Test error handling when no files match pattern."""
        merger = MergeERA5Atmos(
            in_path=self.in_path,
            out_path=self.out_path,
            execute=False,
            verbose=False
        )
        
        with pytest.raises(FileNotFoundError, match="No files found"):
            merger.get_file_list()


class TestConfigurationValidation:
    """Test input validation and configuration."""
    
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
    
    def test_filename_validation(self):
        """Test filename validation."""
        with pytest.raises(ValueError, match="must end with '.nc'"):
            MergeERA5Atmos(
                in_path=self.in_path,
                out_path=self.out_path,
                fname="invalid_filename.txt",
                execute=False
            )

    def test_epsg_validation(self):
        """Test EPSG code validation."""
        with pytest.raises(ValueError, match="Invalid EPSG code"):
            MergeERA5Atmos(
                in_path=self.in_path,
                out_path=self.out_path,
                reproject=999,  # Invalid EPSG
                execute=False
            )

    def test_timezone_validation(self):
        """Test timezone validation."""
        with pytest.raises(ValueError, match="must be a tuple"):
            MergeERA5Atmos(
                in_path=self.in_path,
                out_path=self.out_path,
                local_tz="invalid",
                execute=False
            )
        
        with pytest.raises(ValueError, match="format \\(float, str\\)"):
            MergeERA5Atmos(
                in_path=self.in_path,
                out_path=self.out_path,
                local_tz=("invalid", 123),
                execute=False
            )

    def test_class_resolution(self):
        """
        Debug: Check class inheritance.
        NOTE AEW - I got confused about the init chain...
        This just makes sure that the ERA5Atmos calls ERA5Wave 
        which then calls BaseMerger's init. 
        """
        atmos = MergeERA5Atmos(
            in_path=self.in_path,
            out_path=self.out_path,
            execute=False
        )
        print(f"MRO: {MergeERA5Atmos.__mro__}")
        print(f"Has _validate_fname: {hasattr(atmos, '_validate_fname')}")

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])