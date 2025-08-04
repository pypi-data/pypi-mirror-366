"""
Test the downloader module. These tests focus on the core behaviour of BaseDownloader, and how any specific source downloader
could behave. In this case, we use CFSR and ERA5 to occasionally check inherited behaviour."""

import sys
import tempfile
from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from tfv_get_tools.providers._downloader import BaseDownloader
from tfv_get_tools.providers.atmos.cfsr import DownloadCFSRAtmos


class TestBaseDownloaderValidation:
    """Test the validation methods that actually exist"""
    
    def test_validate_coords_valid(self):
        """Test coordinate validation with valid inputs"""
        coords = BaseDownloader._validate_coords((115.0, 120.0))
        assert coords == (115.0, 120.0)
    
    def test_validate_coords_invalid(self):
        """Test coordinate validation with invalid inputs"""
        with pytest.raises(ValueError, match="must be a tuple of two floats"):
            BaseDownloader._validate_coords((115.0,))  # Only one value
    
    def test_validate_time_interval_valid(self):
        """Test time interval validation"""
        interval = BaseDownloader._validate_time_interval(24)
        assert interval == 24
    
    def test_validate_time_interval_invalid(self):
        """Test invalid time interval"""
        with pytest.raises(ValueError, match="Invalid time interval"):
            BaseDownloader._validate_time_interval(7)


class TestCFSRDownloader:
    """Test inherited behaviour using CFSR."""
    
    def test_cfsr_creation_and_execution(self):
        """Test that CFSR downloader can be created and executed"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create downloader
            downloader = DownloadCFSRAtmos(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                out_path=temp_dir,
                skip_check=True,
                TEST_MODE=True
            )
            
            # Execute download
            result = downloader.execute_download()
            
            # Verify result
            assert hasattr(result, 'total_files')
            assert hasattr(result, 'success_rate')
            assert result.total_files > 0
    
    def test_cfsr_invalid_time_range(self):
        """Test CFSR with dates outside its available range
        I.e. made the start date too early"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Request data from before CFSR starts (1979)
            with pytest.raises(ValueError, match="Time start.*below.*data extent"):
                mr_downloader = DownloadCFSRAtmos(
                    start_date="1940-01-01",  # Before CFSR
                    end_date="1981-12-31",
                    xlims=(115, 120),
                    ylims=(-40, -35),
                    out_path=temp_dir,
                    TEST_MODE=True
                )
                mr_downloader.execute_download()

    def test_cfsr_with_existing_files(self, capsys, tmp_path):
        """Test CFSR skips existing files."""
        # Create an existing file that matches the expected pattern
        existing_file = tmp_path / "CFSR_ATMOS_wnd10m_20220101_20220131.nc"
        existing_file.touch()
        
        # Downloader should skip existing files and report via stdout
        downloader = DownloadCFSRAtmos(
            start_date="2022-01-01",
            end_date="2022-01-31",
            xlims=(115, 120),
            ylims=(-40, -35),
            out_path=str(tmp_path),
            skip_check=False,
            TEST_MODE=True,
        )
        
        downloader.execute_download()
        
        captured = capsys.readouterr()
        

        # Should skip 1, but succeed 5 (all vars except wind)
        assert "Total files processed: 7" in captured.out
        assert "Successful downloads: 6" in captured.out
        assert "Skipped (existing): 1" in captured.out


class TestFileSystemValidation:
    """Test file system related validation"""
    
    def test_nonexistent_directory(self):
        """Test that nonexistent directories are caught"""
        from tfv_get_tools.utilities.parsers import _parse_path
        
        with pytest.raises(NotADirectoryError):
            _parse_path("/this/directory/does/not/exist")
    
    def test_valid_directory(self):
        """Test that valid directories work"""
        from tfv_get_tools.utilities.parsers import _parse_path
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = _parse_path(temp_dir)
            assert result == Path(temp_dir)


class TestDateParsing:
    """Test date parsing functionality"""
    
    def test_valid_date_formats(self):
        """Test that valid date formats work"""
        from tfv_get_tools.utilities.parsers import _parse_date
        
        test_cases = [
            ("2023-01-01", datetime(2023, 1, 1)),
            ("20230101", datetime(2023, 1, 1)),
        ]
        
        for date_str, expected in test_cases:
            result = _parse_date(date_str)
            assert result == expected
    
    def test_invalid_date_formats(self):
        """Test invalid date formats"""
        from tfv_get_tools.utilities.parsers import _parse_date
        
        with pytest.raises(ValueError):
            _parse_date("not-a-date")


class TestNetworkFailures:
    """Test network failure handling"""
    
    @patch('xarray.open_dataset')
    def test_cfsr_network_error(self, mock_xarray):
        """Test CFSR handles network errors gracefully
        Ie xarray open dataset cooks the goose, the downloader should 
        valiantly charge onwards"""
        mock_xarray.side_effect = Exception("Network error")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = DownloadCFSRAtmos(
                start_date="2022-01-01",
                end_date="2022-07-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                out_path=temp_dir,
                skip_check=True,
                TEST_MODE=False  # Actually try to download
            )
            
            result = downloader.execute_download()
            
            # Should handle errors gracefully
            # big long list of failed downloads, but also logged under the total files
            assert result.total_files > 0
            assert len(result.failed_files) > 0
