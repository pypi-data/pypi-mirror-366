"""
Frontend API Integration Tests

Tests that the user-facing functions (DownloadAtmos, DownloadOcean, DownloadWave)
correctly instantiate and call their respective downloader classes.
"""

import tempfile
from unittest.mock import Mock, patch

import pytest

from tfv_get_tools import DownloadAtmos, DownloadOcean, DownloadWave
from tfv_get_tools.providers._downloader import BatchDownloadResult


class TestDownloadAtmosFrontend:
    """Test DownloadAtmos frontend function"""
    
    @patch('tfv_get_tools.providers.atmos.era5.DownloadERA5Atmos')
    def test_era5_instantiation(self, mock_downloader_class):
        """Test ERA5 downloader is correctly instantiated"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadAtmos(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                source="ERA5",
                out_path=temp_dir
            )
        
        # Check class was instantiated with correct args
        mock_downloader_class.assert_called_once()
        call_kwargs = mock_downloader_class.call_args[1]
        assert call_kwargs['start_date'] == "2022-01-01"
        
        # Check execute_download was called
        mock_instance.execute_download.assert_called_once()
        assert isinstance(result, BatchDownloadResult)
    
    @patch('tfv_get_tools.providers.atmos.cfsr.DownloadCFSRAtmos')
    def test_cfsr_instantiation(self, mock_downloader_class):
        """Test CFSR downloader is correctly instantiated"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadAtmos(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                source="CFSR",
                out_path=temp_dir
            )
        
        mock_downloader_class.assert_called_once()
        mock_instance.execute_download.assert_called_once()
        assert isinstance(result, BatchDownloadResult)
    
    @patch('tfv_get_tools.providers.atmos.barra2.DownloadBARRA2')
    def test_barra2_instantiation(self, mock_downloader_class):
        """Test BARRA2 downloader is correctly instantiated"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadAtmos(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                source="BARRA2",
                out_path=temp_dir
            )
        
        mock_downloader_class.assert_called_once()
        mock_instance.execute_download.assert_called_once()
        assert isinstance(result, BatchDownloadResult)
    
    def test_invalid_source(self):
        """Test invalid source raises ValueError"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="Unrecognised source INVALID"):
                DownloadAtmos(
                    start_date="2022-01-01",
                    end_date="2022-01-31",
                    xlims=(115, 120),
                    ylims=(-40, -35),
                    source="INVALID",
                    out_path=temp_dir
                )


class TestDownloadOceanFrontend:
    """Test DownloadOcean frontend function"""
    
    @patch('tfv_get_tools.providers.ocean.hycom.DownloadHycom')
    def test_hycom_instantiation(self, mock_downloader_class):
        """Test HYCOM downloader is correctly instantiated"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadOcean(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                zlims=(0, 100),
                source="HYCOM",
                out_path=temp_dir
            )
        
        # Check class was instantiated with correct args
        mock_downloader_class.assert_called_once()
        call_kwargs = mock_downloader_class.call_args[1]
        assert call_kwargs['zlims'] == (0, 100)
        
        mock_instance.execute_download.assert_called_once()
        assert isinstance(result, BatchDownloadResult)
    
    @patch('tfv_get_tools.providers.ocean.copernicus_ocean.DownloadCopernicusOcean')
    def test_copernicus_instantiation(self, mock_downloader_class):
        """Test Copernicus Ocean downloader is correctly instantiated"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadOcean(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                source="Copernicus",
                out_path=temp_dir
            )
        
        mock_downloader_class.assert_called_once()
        mock_instance.execute_download.assert_called_once()
        assert isinstance(result, BatchDownloadResult)
    
    def test_invalid_source(self):
        """Test invalid source raises ValueError"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="Unrecognised source INVALID"):
                DownloadOcean(
                    start_date="2022-01-01",
                    end_date="2022-01-31",
                    xlims=(115, 120),
                    ylims=(-40, -35),
                    source="INVALID",
                    out_path=temp_dir
                )


class TestDownloadWaveFrontend:
    """Test DownloadWave frontend function"""
    
    @patch('tfv_get_tools.providers.wave.cawcr.DownloadCAWCR')
    def test_cawcr_instantiation(self, mock_downloader_class):
        """Test CAWCR downloader is correctly instantiated"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadWave(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                source="CAWCR",
                out_path=temp_dir
            )
        
        mock_downloader_class.assert_called_once()
        call_kwargs = mock_downloader_class.call_args[1]
        
        mock_instance.execute_download.assert_called_once()
        assert isinstance(result, BatchDownloadResult)
    
    @patch('tfv_get_tools.providers.wave.copernicus_wave.DownloadCopernicusWave')
    def test_copernicus_instantiation(self, mock_downloader_class):
        """Test Copernicus Wave downloader is correctly instantiated"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadWave(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                source="Copernicus",
                out_path=temp_dir
            )
        
        mock_downloader_class.assert_called_once()
        mock_instance.execute_download.assert_called_once()
        assert isinstance(result, BatchDownloadResult)
    
    @patch('tfv_get_tools.providers.wave.era5.DownloadERA5Wave')
    def test_era5_instantiation(self, mock_downloader_class):
        """Test ERA5 Wave downloader is correctly instantiated"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadWave(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                source="ERA5",
                out_path=temp_dir
            )
        
        mock_downloader_class.assert_called_once()
        mock_instance.execute_download.assert_called_once()
        assert isinstance(result, BatchDownloadResult)
    
    def test_invalid_source(self):
        """Test invalid source raises ValueError"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="Unrecognised source INVALID"):
                DownloadWave(
                    start_date="2022-01-01",
                    end_date="2022-01-31",
                    xlims=(115, 120),
                    ylims=(-40, -35),
                    source="INVALID",
                    out_path=temp_dir
                )


class TestParameterPassing:
    """Test that parameters are correctly passed through to downloaders"""
    
    @patch('tfv_get_tools.providers.atmos.era5.DownloadERA5Atmos')
    def test_custom_parameters_passed(self, mock_downloader_class):
        """Test custom parameters are passed correctly"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            DownloadAtmos(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                source="ERA5",
                model="custom_model",
                prefix="TEST",
                verbose=True,
                variables=["temperature", "pressure"],
                skip_check=True,
                out_path=temp_dir,
                custom_arg="test_value"
            )
        
        # Check all parameters were passed
        call_kwargs = mock_downloader_class.call_args[1]
        assert call_kwargs['model'] == "custom_model"
        assert call_kwargs['prefix'] == "TEST"
        assert call_kwargs['verbose'] is True
        assert call_kwargs['variables'] == ["temperature", "pressure"]
        assert call_kwargs['skip_check'] is True
        assert call_kwargs['custom_arg'] == "test_value"
    
    @patch('tfv_get_tools.providers.ocean.hycom.DownloadHycom')
    def test_ocean_specific_parameters(self, mock_downloader_class):
        """Test ocean-specific parameters like zlims and time_interval"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            DownloadOcean(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                zlims=(0, 200),
                time_interval=12,
                source="HYCOM",
                out_path=temp_dir
            )
        
        call_kwargs = mock_downloader_class.call_args[1]
        assert call_kwargs['zlims'] == (0, 200)
        assert call_kwargs['time_interval'] == 12


class TestDefaultValues:
    """Test that default values are correctly applied"""
    
    @patch('tfv_get_tools.providers.atmos.era5.DownloadERA5Atmos')
    def test_atmos_defaults(self, mock_downloader_class):
        """Test DownloadAtmos applies correct defaults"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            DownloadAtmos(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                source="ERA5",
                out_path=temp_dir
            )
        
        call_kwargs = mock_downloader_class.call_args[1]
        assert call_kwargs['model'] == "default"
        assert call_kwargs['prefix'] is None
        assert call_kwargs['verbose'] is False
        assert call_kwargs['variables'] is None
        assert call_kwargs['skip_check'] is False
    
    @patch('tfv_get_tools.providers.ocean.hycom.DownloadHycom')
    def test_ocean_defaults(self, mock_downloader_class):
        """Test DownloadOcean applies correct defaults"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            DownloadOcean(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                out_path=temp_dir
            )
        
        call_kwargs = mock_downloader_class.call_args[1]
        assert call_kwargs['model'] == "default"
        assert call_kwargs['time_interval'] == 24
        assert call_kwargs['zlims'] is None
    
    @patch('tfv_get_tools.providers.wave.cawcr.DownloadCAWCR')
    def test_wave_defaults(self, mock_downloader_class):
        """Test DownloadWave applies correct defaults"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            DownloadWave(
                start_date="2022-01-01",
                end_date="2022-01-31",
                xlims=(115, 120),
                ylims=(-40, -35),
                out_path=temp_dir
            )
        
        call_kwargs = mock_downloader_class.call_args[1]
        assert call_kwargs['model'] == "default"


class TestCaseInsensitivity:
    """Test that source names are case insensitive"""
    
    @patch('tfv_get_tools.providers.atmos.era5.DownloadERA5Atmos')
    def test_case_insensitive_sources(self, mock_downloader_class):
        """Test source names work regardless of case"""
        mock_instance = Mock()
        mock_instance.execute_download.return_value = BatchDownloadResult()
        mock_downloader_class.return_value = mock_instance
        
        test_cases = ["era5", "ERA5", "Era5", "eRa5"]
        
        for source_case in test_cases:
            with tempfile.TemporaryDirectory() as temp_dir:
                result = DownloadAtmos(
                    start_date="2022-01-01",
                    end_date="2022-01-31",
                    xlims=(115, 120),
                    ylims=(-40, -35),
                    source=source_case,
                    out_path=temp_dir
                )
                assert isinstance(result, BatchDownloadResult)


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"])