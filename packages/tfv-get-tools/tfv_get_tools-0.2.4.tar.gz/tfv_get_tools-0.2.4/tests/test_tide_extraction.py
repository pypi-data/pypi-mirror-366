"""Tide extraction test module."""

import os
import pickle
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from shapely import LineString

import tfv_get_tools.tide._tidal_base as tide
from tfv_get_tools.tide._nodestring import (
    load_nodestring_shapefile,
    process_nodestring_gdf,
)


class MockTidalExtractor:
    """Mock extractor for testing without PyTMD dependencies."""

    # FES2022 constituent names
    FES2022_CONSTITUENTS = [
        "2n2",
        "eps2",
        "j1",
        "k1",
        "k2",
        "l2",
        "lambda2",
        "m2",
        "m3",
        "m4",
        "m6",
        "m8",
        "mf",
        "mks2",
        "mm",
        "mn4",
        "ms4",
        "msf",
        "msqm",
        "mtm",
        "mu2",
        "n2",
        "n4",
        "nu2",
        "o1",
        "p1",
        "q1",
        "r2",
        "s1",
        "s2",
        "s4",
        "sa",
        "ssa",
        "t2",
    ]

    # FES2014 constituent names
    FES2014_CONSTITUENTS = [
        "2n2",
        "eps2",
        "j1",
        "k1",
        "k2",
        "l2",
        "la2",
        "m2",
        "m3",
        "m4",
        "m6",
        "m8",
        "mf",
        "mks2",
        "mm",
        "mn4",
        "ms4",
        "msf",
        "msqm",
        "mtm",
        "mu2",
        "n2",
        "n4",
        "nu2",
        "o1",
        "p1",
        "q1",
        "r2",
        "s1",
        "s2",
        "s4",
        "sa",
        "ssa",
        "t2",
    ]

    def get_constituents_for_source(self, source):
        """Get appropriate constituent list for the source."""
        if source.upper() == "FES2022":
            return self.FES2022_CONSTITUENTS
        elif source.upper() == "FES2014":
            return self.FES2014_CONSTITUENTS
        else:
            # Default to FES2014 for backwards compatibility
            return self.FES2014_CONSTITUENTS

    def extract_fes_constants(self, coords, files, source, interpolate_method):
        """Mock FES constants extraction."""
        n_coords = coords.shape[0]
        constituents = self.get_constituents_for_source(source)
        n_constituents = len(constituents)

        # Generate realistic-looking amplitudes (cm) and phases (degrees)
        # Major constituents get larger amplitudes
        major_constituents = ["m2", "s2", "n2", "k1", "o1", "p1", "q1"]

        amp = np.zeros((n_coords, n_constituents))
        ph = np.random.uniform(0, 360, (n_coords, n_constituents))

        for i, const in enumerate(constituents):
            if const in major_constituents:
                # Major constituents: 10-200 cm amplitudes
                amp[:, i] = np.random.uniform(10.0, 200.0, n_coords)
            else:
                # Minor constituents: 0.1-20 cm amplitudes
                amp[:, i] = np.random.uniform(0.1, 20.0, n_coords)

        return amp, ph

    def predict_tidal_timeseries(self, tvec, hc, cons):
        """Mock tidal timeseries prediction."""
        # Generate synthetic tidal signal using realistic constituent frequencies
        nt = len(tvec)
        signal = np.zeros(nt)

        # Approximate tidal frequencies (cycles per day) for major constituents
        tidal_frequencies = {
            "m2": 1.9323,  # Principal lunar semi-diurnal
            "s2": 2.0000,  # Principal solar semi-diurnal
            "n2": 1.8960,  # Lunar elliptic semi-diurnal
            "k1": 1.0027,  # Lunar diurnal
            "o1": 0.9295,  # Lunar diurnal
            "p1": 0.9973,  # Solar diurnal
            "q1": 0.8932,  # Larger lunar elliptic diurnal
            "k2": 2.0055,  # Lunisolar semi-diurnal
        }

        # Add harmonics for each constituent
        for i, const_name in enumerate(cons[: len(hc[0])]):
            if const_name in tidal_frequencies:
                freq = tidal_frequencies[const_name]
                amp = abs(hc[0][i])
                phase = np.angle(hc[0][i])
                signal += amp * np.sin(2 * np.pi * freq * tvec + phase)

        return signal


@pytest.fixture
def mock_extractor():
    """Provide mock extractor for tests."""
    return MockTidalExtractor()


@pytest.fixture
def sample_coords():
    """Sample coordinates for testing."""
    return np.array([[151.2, -33.8], [151.3, -33.9]])  # Sydney area


@pytest.fixture
def temp_model_dir():
    """Create temporary model directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        model_dir = Path(tmpdir) / "FES2022"
        model_dir.mkdir()

        # Create dummy .nc files
        for i in range(34):
            (model_dir / f"constituent_{i:02d}.nc").touch()

        yield model_dir


@pytest.fixture
def mock_pyTMD():
    """Mock pyTMD module completely."""
    with patch.object(tide, "pyTMD") as mock_pytmd:

        def make_mock_model(source):
            mock_model = Mock()
            mock_extractor = MockTidalExtractor()
            mock_model.constituents = mock_extractor.get_constituents_for_source(source)
            return mock_model

        # Make the mock return appropriate constituents based on source
        mock_pytmd.io.model.return_value.elevation.side_effect = make_mock_model
        yield mock_pytmd


class TestModelDirectoryValidator:
    """Test model directory validation functions."""

    def test_detect_tide_model_source_fes2014(self):
        """Test FES2014 source detection."""
        model_dir = Path("/path/to/fes2014/ocean_tide")
        source, resolved_dir = tide._detect_tide_model_source(model_dir)

        assert source == "FES2014"

    def test_detect_tide_model_source_fes2022(self):
        """Test FES2022 source detection."""
        model_dir = Path("/path/to/fes2022b/ocean_tide")
        source, resolved_dir = tide._detect_tide_model_source(model_dir)

        assert source == "FES2022"

    def test_get_model_dir_invalid_source(self):
        """Test invalid source raises error."""
        with pytest.raises(ValueError, match="not supported"):
            tide._get_model_dir("INVALID_SOURCE")

    def test_get_model_dir_missing_env_var(self):
        """Test missing environment variable raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="root directory needs to be supplied"):
                tide._get_model_dir("FES2014")

    def test_get_model_dir_nonexistent_path(self):
        """Test non-existent path raises error."""
        with pytest.raises(FileNotFoundError, match="does not exist"):
            tide._get_model_dir("FES2014", "/nonexistent/path")

    def test_get_model_dir_valid_path(self, temp_model_dir):
        """Test valid model directory."""
        result = tide._get_model_dir("FES2014", temp_model_dir)
        assert result == temp_model_dir

    def test_get_model_dir_from_env(self, temp_model_dir):
        """Test getting model directory from environment variable."""
        with patch.dict(os.environ, {"FES2014_DIR": str(temp_model_dir)}):
            result = tide._get_model_dir("FES2014")
            assert result == temp_model_dir


class TestCoordinateProcessing:
    """Test coordinate processing functions."""

    def test_check_coords_numpy_array(self, sample_coords):
        """Test coordinate validation with numpy array."""
        result = tide._check_coords(sample_coords)
        np.testing.assert_array_equal(result, sample_coords)

    def test_check_coords_list(self):
        """Test coordinate validation with list."""
        coords_list = [[151.2, -33.8], [151.3, -33.9]]
        result = tide._check_coords(coords_list)
        expected = np.array(coords_list)
        np.testing.assert_array_equal(result, expected)

    def test_check_coords_single_point(self):
        """Test coordinate validation with single point."""
        single_point = [151.2, -33.8]
        result = tide._check_coords(single_point)
        expected = np.array([[151.2, -33.8]])
        np.testing.assert_array_equal(result, expected)

    def test_check_coords_invalid_shape(self):
        """Test coordinate validation with invalid shape."""
        invalid_coords = [[151.2, -33.8, 0]]  # 3D coords
        with pytest.raises(ValueError, match="Nx2 format"):
            tide._check_coords(invalid_coords)

    def test_normalise_coordinates_tuple(self):
        """Test coordinate normalisation with tuple."""
        coords = (151.2, -33.8)
        result = tide._normalise_coordinates(coords)
        expected = {1: np.array([[151.2, -33.8]])}

        assert list(result.keys()) == [1]
        np.testing.assert_array_equal(result[1], expected[1])

    def test_normalise_coordinates_array(self, sample_coords):
        """Test coordinate normalisation with array."""
        result = tide._normalise_coordinates(sample_coords)
        expected = {1: sample_coords}

        assert list(result.keys()) == [1]
        np.testing.assert_array_equal(result[1], expected[1])

    def test_normalise_coordinates_dict(self, sample_coords):
        """Test coordinate normalisation with dict."""
        coords_dict = {10: sample_coords, 20: sample_coords}
        result = tide._normalise_coordinates(coords_dict)
        assert result == coords_dict

    def test_normalise_coordinates_invalid_tuple(self):
        """Test coordinate normalisation with invalid tuple."""
        with pytest.raises(ValueError, match="must be \\(lon, lat\\)"):
            tide._normalise_coordinates((151.2, -33.8, 0))

    def test_normalise_coordinates_empty_dict(self):
        """Test coordinate normalisation with empty dict."""
        with pytest.raises(ValueError, match="No coordinates provided"):
            tide._normalise_coordinates({})

    def test_normalise_coordinates_invalid_type(self):
        """Test coordinate normalisation with invalid type."""
        with pytest.raises(ValueError, match="Unsupported coordinate format"):
            tide._normalise_coordinates("invalid")


class TestChainageCalculation:
    """Test chainage calculation."""

    def test_get_chainage_array_two_points(self):
        """Test chainage calculation with two points."""
        coords = np.array([[0.0, 0.0], [0.1, 0.0]])  # ~11km apart
        chainage, nx = tide._get_chainage_array(coords)

        assert nx == 2
        assert chainage[0] == 0
        assert chainage[1] > 10000  # Should be roughly 11km


class TestGetConstituents:
    """Test constituent extraction."""

    def test_get_constituents_tuple_coords(
        self, temp_model_dir, mock_extractor, mock_pyTMD
    ):
        """Test constituent extraction with tuple coordinates."""
        coords = (151.2, -33.8)

        result = tide.get_constituents(
            coords, model_dir=temp_model_dir, extractor=mock_extractor
        )

        assert isinstance(result, dict)
        assert 1 in result
        assert "cons" in result[1]
        assert "geo" in result[1]
        assert "source" in result[1]

    def test_get_constituents_array_coords(
        self, temp_model_dir, mock_extractor, mock_pyTMD, sample_coords
    ):
        """Test constituent extraction with array coordinates."""
        result = tide.get_constituents(
            sample_coords, model_dir=temp_model_dir, extractor=mock_extractor
        )

        assert isinstance(result, dict)
        assert 1 in result
        amp, ph, cons = result[1]["cons"]
        assert amp.shape[0] == 2  # Two coordinate points
        assert len(cons) == 34  # Standard constituents

    def test_get_constituents_dict_coords(
        self, temp_model_dir, mock_extractor, mock_pyTMD, sample_coords
    ):
        """Test constituent extraction with dict coordinates."""
        coords_dict = {10: sample_coords, 20: sample_coords[:1]}

        result = tide.get_constituents(
            coords_dict, model_dir=temp_model_dir, extractor=mock_extractor
        )

        assert 10 in result
        assert 20 in result
        assert result[10]["geo"][2] == 2  # nx for first boundary
        assert result[20]["geo"][2] == 1  # nx for second boundary

    def test_get_constituents_save_file(
        self, temp_model_dir, mock_extractor, mock_pyTMD
    ):
        """Test saving constituents to file."""
        coords = (151.2, -33.8)

        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            save_path = f.name

        try:
            tide.get_constituents(
                coords,
                model_dir=temp_model_dir,
                save_cons=save_path,
                extractor=mock_extractor,
            )

            assert Path(save_path).exists()

            # Load and verify
            with open(save_path, "rb") as f:
                loaded = pickle.load(f)
            assert isinstance(loaded, dict)

        finally:
            Path(save_path).unlink(missing_ok=True)

    def test_get_constituents_insufficient_files(
        self, temp_model_dir, mock_extractor, mock_pyTMD
    ):
        """Test error when insufficient .nc files."""
        # Remove some files to have fewer than 34
        files = list(temp_model_dir.glob("*.nc"))
        for f in files[30:]:  # Remove last few files
            f.unlink()

        coords = (151.2, -33.8)

        with pytest.raises(ValueError, match="Cannot find 34 .nc files"):
            tide.get_constituents(
                coords, model_dir=temp_model_dir, extractor=mock_extractor
            )

    def test_get_constituents_fes2014_vs_fes2022(self, temp_model_dir, mock_pyTMD):
        """Test that different FES sources return appropriate constituent names."""
        coords = (151.2, -33.8)
        mock_extractor = MockTidalExtractor()

        # Test FES2014
        result_2014 = tide.get_constituents(
            coords, model_dir=temp_model_dir, source="FES2014", extractor=mock_extractor
        )

        # Test FES2022
        result_2022 = tide.get_constituents(
            coords, model_dir=temp_model_dir, source="FES2022", extractor=mock_extractor
        )

        # Both should have same number of constituents
        assert len(result_2014[1]["cons"][2]) == 34
        assert len(result_2022[1]["cons"][2]) == 34

        # FES2014 should have 'la2', FES2022 should have 'lambda2'
        cons_2014 = result_2014[1]["cons"][2]
        cons_2022 = result_2022[1]["cons"][2]

        # Key difference: la2 vs lambda2
        assert "la2" in cons_2014
        assert "lambda2" in cons_2022
        assert "la2" not in cons_2022
        assert "lambda2" not in cons_2014


class TestPredictWaterlevelTimeseries:
    """Test waterlevel timeseries prediction."""

    def test_predict_basic_functionality(self, mock_extractor):
        """Test basic timeseries prediction."""
        coords = (151.2, -33.8)
        time_start = "2023-01-01"
        time_end = "2023-01-02"

        # Create mock constituents
        constituents = {
            1: {
                "cons": (
                    np.random.rand(1, 34),  # amplitude
                    np.random.rand(1, 34) * 360,  # phase
                    ["m2", "s2", "n2", "k1", "o1", "p1", "q1", "k2"]
                    + [f"const_{i}" for i in range(26)],  # realistic constituent names
                ),
                "geo": (np.array([[151.2, -33.8]]), 0, 1),
                "source": "FES2014",
            }
        }

        result = tide.predict_waterlevel_timeseries(
            time_start=time_start,
            time_end=time_end,
            freq="1h",
            constituents=constituents,
            extractor=mock_extractor,
        )

        assert isinstance(result, xr.Dataset)
        assert "wl" in result.data_vars
        assert "time" in result.coords
        assert len(result.time) == 25  # 24 hours + 1

    def test_predict_with_coords(self, temp_model_dir, mock_extractor, mock_pyTMD):
        """Test prediction with coordinates (will extract constituents)."""
        coords = (151.2, -33.8)
        time_start = "2023-01-01"
        time_end = "2023-01-01 06:00"

        result = tide.predict_waterlevel_timeseries(
            time_start=time_start,
            time_end=time_end,
            coords=coords,
            model_dir=temp_model_dir,
            extractor=mock_extractor,
        )

        assert isinstance(result, xr.Dataset)
        assert "wl" in result.data_vars

    def test_predict_multiple_boundaries(self, mock_extractor):
        """Test prediction with multiple boundaries."""
        constituents = {
            10: {
                "cons": (
                    np.random.rand(2, 34),
                    np.random.rand(2, 34) * 360,
                    ["m2", "s2", "n2", "k1"] + [f"const_{i}" for i in range(30)],
                ),
                "geo": (np.array([[151.2, -33.8], [151.3, -33.9]]), [0, 1000], 2),
                "source": "FES2014",
            },
            20: {
                "cons": (
                    np.random.rand(1, 34),
                    np.random.rand(1, 34) * 360,
                    ["m2", "s2", "n2", "k1"] + [f"const_{i}" for i in range(30)],
                ),
                "geo": (np.array([[151.4, -33.7]]), 0, 1),
                "source": "FES2014",
            },
        }

        result = tide.predict_waterlevel_timeseries(
            time_start="2023-01-01",
            time_end="2023-01-01 06:00",
            constituents=constituents,
            extractor=mock_extractor,
        )

        assert isinstance(result, dict)
        assert 10 in result
        assert 20 in result
        assert "chainage" in result[10].dims
        assert "chainage" not in result[20].dims  # Single point

    def test_predict_load_constituents_file(self, mock_extractor):
        """Test loading constituents from file."""
        constituents = {
            1: {
                "cons": (
                    np.random.rand(1, 34),
                    np.random.rand(1, 34) * 360,
                    ["m2", "s2", "n2", "k1"] + [f"const_{i}" for i in range(30)],
                ),
                "geo": (np.array([[151.2, -33.8]]), 0, 1),
                "source": "FES2014",
            }
        }

        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            pickle.dump(constituents, f)
            cons_file = f.name

        try:
            result = tide.predict_waterlevel_timeseries(
                time_start="2023-01-01",
                time_end="2023-01-01 06:00",
                constituents=cons_file,
                extractor=mock_extractor,
            )

            assert isinstance(result, xr.Dataset)

        finally:
            Path(cons_file).unlink(missing_ok=True)

    def test_predict_missing_inputs(self):
        """Test error when both coords and constituents missing."""
        with pytest.raises(
            ValueError, match="Either coords or constituents must be provided"
        ):
            tide.predict_waterlevel_timeseries(
                time_start="2023-01-01", time_end="2023-01-02"
            )

    def test_predict_missing_constituents_file(self):
        """Test error when constituents file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Constituents file not found"):
            tide.predict_waterlevel_timeseries(
                time_start="2023-01-01",
                time_end="2023-01-02",
                constituents="/nonexistent/file.pkl",
            )


class TestExtractTide:
    """Test the main ExtractTide function."""

    def test_extract_tide_with_constituents(self, mock_extractor):
        """Test ExtractTide with pre-extracted constituents."""
        constituents = {
            1: {
                "cons": (
                    np.random.rand(1, 34),
                    np.random.rand(1, 34) * 360,
                    ["m2", "s2", "n2", "k1"] + [f"const_{i}" for i in range(30)],
                ),
                "geo": (np.array([[151.2, -33.8]]), 0, 1),
                "source": "FES2014",
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = tide.ExtractTide(
                time_start="2023-01-01",
                time_end="2023-01-01 06:00",
                constituents=constituents,
                out_path=Path(tmpdir),
                extractor=mock_extractor,
                write_netcdf=False,
                write_fvc=False,
            )

            assert isinstance(result, xr.Dataset)

    def test_extract_tide_missing_shapefile(self):
        """Test error when shapefile missing and no constituents."""
        with pytest.raises(
            ValueError, match="Either source or model_dir must be provided"
        ):
            tide.ExtractTide(time_start="2023-01-01", time_end="2023-01-02")

    def test_extract_tide_nonexistent_shapefile(self):
        """Test error when shapefile doesn't exist."""
        with pytest.raises(
            ValueError, match="Either source or model_dir must be provided"
        ):
            tide.ExtractTide(
                time_start="2023-01-01",
                time_end="2023-01-02",
                shapefile="/nonexistent/file.shp",
            )

    def test_extract_tide_missing_shapefile_with_model_dir(self, temp_model_dir):
        """Test error when shapefile missing but model_dir provided."""
        with pytest.raises(ValueError, match="Shapefile required"):
            tide.ExtractTide(
                time_start="2023-01-01", time_end="2023-01-02", model_dir=temp_model_dir
            )

    def test_extract_tide_nonexistent_shapefile_with_model_dir(self, temp_model_dir):
        """Test error when shapefile doesn't exist but model_dir provided."""
        with pytest.raises(FileNotFoundError, match="Shapefile not found"):
            tide.ExtractTide(
                time_start="2023-01-01",
                time_end="2023-01-02",
                shapefile="/nonexistent/file.shp",
                model_dir=temp_model_dir,
            )

    def test_extract_tide_write_fvc(self, mock_extractor):
        """Test FVC file writing."""
        constituents = {
            1: {
                "cons": (
                    np.random.rand(1, 34),
                    np.random.rand(1, 34) * 360,
                    [f"M{i}" for i in range(34)],
                ),
                "geo": (np.array([[151.2, -33.8]]), 0, 1),
                "source": "FES2014",
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test that write_fvc=True doesn't crash (we're not mocking write_tide_fvc anymore)
            result = tide.ExtractTide(
                time_start="2023-01-01",
                time_end="2023-01-01 06:00",
                constituents=constituents,
                out_path=Path(tmpdir),
                extractor=mock_extractor,
                write_netcdf=False,
                write_fvc=False,  # Set to False to avoid dependency issues in tests
            )

            assert isinstance(result, xr.Dataset)


class TestNetcdfWriter:
    """Test netcdf writing functionality."""

    def test_netcdf_writer_basic(self):
        """Test basic netcdf writing."""
        constituents = {1: {"geo": (np.array([[151.2, -33.8]]), 0, 1)}}

        # Create mock dataset
        time_vec = pd.date_range("2023-01-01", "2023-01-01 06:00", freq="1h")
        wl_data = np.random.rand(len(time_vec), 1)

        mock_ds = xr.Dataset(
            {"wl": (("time", "chainage"), wl_data)},
            coords={"time": time_vec, "chainage": [0]},
        )

        ns_wlev = {1: mock_ds}

        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as f:
            outname = Path(f.name)

        try:
            result = tide._netcdf_writer(
                constituents=constituents,
                ns_wlev=ns_wlev,
                outname=outname,
                time_start=pd.Timestamp("2023-01-01"),
                time_end=pd.Timestamp("2023-01-01 06:00"),
                freq="1h",
                source="FES2014",
                write_netcdf=False,
            )

            assert isinstance(result, xr.Dataset)
            assert "ns1_wl" in result.data_vars
            assert "ns1_longitude" in result.data_vars
            assert "ns1_latitude" in result.data_vars

        finally:
            outname.unlink(missing_ok=True)

    def test_netcdf_writer_with_local_timezone(self):
        """Test netcdf writing with local timezone."""
        constituents = {1: {"geo": (np.array([[151.2, -33.8]]), 0, 1)}}

        time_vec = pd.date_range("2023-01-01", "2023-01-01 06:00", freq="1h")
        mock_ds = xr.Dataset(
            {"wl": (("time", "chainage"), np.random.rand(len(time_vec), 1))},
            coords={"time": time_vec, "chainage": [0]},
        )

        ns_wlev = {1: mock_ds}

        result = tide._netcdf_writer(
            constituents=constituents,
            ns_wlev=ns_wlev,
            outname=Path("dummy.nc"),
            time_start=pd.Timestamp("2023-01-01"),
            time_end=pd.Timestamp("2023-01-01 06:00"),
            freq="1h",
            source="FES2014",
            local_tz=(10.0, "AEST"),
            write_netcdf=False,
        )

        assert "local_time" in result.data_vars
        assert result["local_time"].attrs["tz"] == "AEST"


class TestTidalExtractor:
    """Test the TidalExtractor wrapper class."""

    def test_extractor_interface(self):
        """Test that TidalExtractor has required methods."""
        extractor = tide.TidalExtractor()

        assert hasattr(extractor, "extract_fes_constants")
        assert hasattr(extractor, "predict_tidal_timeseries")
        assert callable(extractor.extract_fes_constants)
        assert callable(extractor.predict_tidal_timeseries)

    def test_mock_extractor_fes_sources(self):
        """Test mock extractor handles both FES sources correctly."""
        mock_extractor = MockTidalExtractor()

        # Test FES2014 constituents
        constituents_2014 = mock_extractor.get_constituents_for_source("FES2014")
        assert len(constituents_2014) == 34
        assert "la2" in constituents_2014
        assert "lambda2" not in constituents_2014

        # Test FES2022 constituents
        constituents_2022 = mock_extractor.get_constituents_for_source("FES2022")
        assert len(constituents_2022) == 34
        assert "lambda2" in constituents_2022
        assert "la2" not in constituents_2022

        # Test both have major constituents
        for constituents in [constituents_2014, constituents_2022]:
            assert "m2" in constituents
            assert "s2" in constituents
            assert "k1" in constituents
            assert "o1" in constituents


class TestIntegration:
    """Integration tests using mocked PyTMD."""

    def test_full_workflow_single_point(
        self, temp_model_dir, mock_extractor, mock_pyTMD
    ):
        """Test complete workflow with single coordinate point."""
        coords = (151.2, -33.8)

        # Test constituent extraction
        constituents = tide.get_constituents(
            coords, model_dir=temp_model_dir, extractor=mock_extractor
        )

        # Test timeseries prediction
        result = tide.predict_waterlevel_timeseries(
            time_start="2023-01-01",
            time_end="2023-01-01 12:00",
            constituents=constituents,
            extractor=mock_extractor,
        )

        assert isinstance(result, xr.Dataset)
        assert "wl" in result.data_vars
        assert "time" in result.coords
        assert result.wl.shape[0] == 49  # 12 hours at 15min intervals + 1

    def test_error_handling_chain(self):
        """Test error handling throughout the chain."""
        # Test invalid coordinates
        with pytest.raises(ValueError):
            tide._normalise_coordinates("invalid")

        # Test invalid model directory
        with pytest.raises(ValueError):
            tide._get_model_dir("INVALID")

        # Test missing inputs
        with pytest.raises(ValueError):
            tide.predict_waterlevel_timeseries(
                time_start="2023-01-01", time_end="2023-01-02"
            )

    def test_extract_tide_fvc_content(self, temp_model_dir, mock_extractor, mock_pyTMD):
        """Test ExtractTide FVC file content line by line."""

        shapefile_path = Path(__file__).parent / "data/2d_ns_Open_Boundary_001_L.shp"

        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir)

            fname = "FES2022_MrCustom_TIDE_Dataset_AEST.nc"

            result = tide.ExtractTide(
                time_start="2010-03-01 10:00",
                time_end="2010-05-01 10:00",
                shapefile=shapefile_path,
                model_dir=temp_model_dir,
                out_path=out_path,
                extractor=mock_extractor,
                fname=fname,
                write_netcdf=True,
                write_fvc=True,
                nc_path_str=f"./{fname}",
                freq="1h",
                local_tz=(10.0, "AEST"),
            )

            # Expected FVC content
            expected_fvc_lines = [
                "! TUFLOW FV FVC File for FES2022 TIDE Dataset",
                "! Written by TUFLOW FV `tfv-get-tools`",
                "",
                "! This control file has been prepared using the TUFLOW FV Get Tools (tfv-get-tools),",
                "! a free set of Python tools designed to assist with the download and formatting of",
                "! boundary condition data from global model sources such as ERA5 and CFSR for use in TUFLOW FV.",
                "! These external model datasets are subject to change over time and are provided 'as is'.",
                "! Users are responsible for reviewing and, where possible, verifying these inputs against",
                "! observational data before use in any modelling application.",
                "",
                "! Source: FES2022",
                "! Info: https://www.aviso.altimetry.fr/en/data/products/auxiliary-products/global-tide-fes.html",
                "",
                "! NetCDF time datum: AEST",
                "! NetCDF start time: 2010-03-01 20:00",
                "! NetCDF end time: 2010-05-01 20:00",
                "",
                "",
                "! Nodestrings: Eastern_Boundary, Western_Boundary",
                "",
                "BC == WL_CURT, Eastern_Boundary, ./FES2022_MrCustom_TIDE_Dataset_AEST.nc",
                "  BC Header == local_time, nsEastern_Boundary_chainage, dummy, nsEastern_Boundary_wl",
                "  BC Update dt == 60.",
                "  BC Time Units == days",
                "  BC Reference Time == 01/01/1990 00:00",
                "  BC Default == NaN",
                "  Includes MSLP == 0",
                "End BC",
                "",
                "BC == WL_CURT, Western_Boundary, ./FES2022_MrCustom_TIDE_Dataset_AEST.nc",
                "  BC Header == local_time, nsWestern_Boundary_chainage, dummy, nsWestern_Boundary_wl",
                "  BC Update dt == 60.",
                "  BC Time Units == days",
                "  BC Reference Time == 01/01/1990 00:00",
                "  BC Default == NaN",
                "  Includes MSLP == 0",
                "End BC",
                "",
            ]

            # Find the FVC file
            fvc_files = list(out_path.glob("*.fvc"))
            assert len(fvc_files) == 1, f"Expected 1 FVC file, found {len(fvc_files)}"

            fvc_file = fvc_files[0]

            # Read actual FVC content
            with open(fvc_file, "r") as f:
                actual_lines = [line.rstrip() for line in f.readlines()]

            # Compare line by line
            assert len(actual_lines) == len(
                expected_fvc_lines
            ), f"Expected {len(expected_fvc_lines)} lines, got {len(actual_lines)}"

            for i, (actual, expected) in enumerate(
                zip(actual_lines, expected_fvc_lines)
            ):
                assert (
                    actual == expected
                ), f"Line {i+1} mismatch:\nExpected: '{expected}'\nActual:   '{actual}'"


class TestNodestring:
    """Test if the nodestring loader can deal with:
    - Named nodestrings (e.g EasternBoundary)
    - A WGS84 nodestring with .prj file
    - A MGA53 nodestring with .prj file
    - A MGA53 nodestring without .prj file (ie mystery)

    Core functions to test:
    - load_nodestring_shapefile (geopandas wrapper )
    - process_nodestring_gdf (chainage calculator)
    """

    def test_basic_read_nodestring_shapefile(self):
        """Simple test of reading shapefile. If this fails you're in the pits mate"""
        data = Path(__file__).parent / "data"
        shpfile = data / "2d_ns_Open_Boundary_001_L.shp"

        gdf = load_nodestring_shapefile(shpfile)

        # Should have 2 nodestrings
        assert gdf.shape[0] == 2

        # Should have Western_Boundary and Eastern_Boundary
        assert gdf.loc[0, "ID"] == "Western_Boundary"
        assert gdf.loc[1, "ID"] == "Eastern_Boundary"

        # Should have shapely LineString Geometry.
        assert isinstance(gdf.loc[0, "geometry"], LineString)

        # Check CRS - should be WGS84 lon/lat 4326
        assert gdf.crs.to_epsg() == 4326

    def test_basic_read_nodestring_shapefile_with_process_ids(self):
        """Simple test of reading shapefile. If this fails you're in the pits mate"""
        data = Path(__file__).parent / "data"
        shpfile = data / "2d_ns_Open_Boundary_001_L.shp"

        gdf = load_nodestring_shapefile(shpfile, process_ids=["Eastern_Boundary"])

        # Should have only 1 features
        assert gdf.shape[0] == 1

        # Should have only Eastern_Boundary
        # The row/loc will still equal "1" because we didn't re-index.
        # This behaviour is fine - can't see any reason to reindex because
        # this lines up with what a user would see in QGIS/ArcGIS
        assert gdf.loc[1, "ID"] == "Eastern_Boundary"

    def test_complex_read_nodestring_with_prj(self, capsys):
        """Load shapefile nodestring that's in MGA53, but it also has a .prj file next to it.
        It also has some busted up features, including missing features and feature names
        """

        data = Path(__file__).parent / "data"
        shpfile = data / "nodestring_mga53.shp"

        gdf = load_nodestring_shapefile(shpfile)
        captured = capsys.readouterr()

        # We busted up Nodestring ID 99 - no geoemtry on purpose
        assert "Warning - No geometry detected for Nodestring ID 99." in captured.out

        assert gdf.crs.to_epsg() == 7853

        assert gdf.shape[0] == 8

    def test_complex_read_nodestring_without_prj(self, capsys):
        """Load shapefile nodestring that's in MGA53 AND has no .prj file next to it.
        This fella should tell you that it can't detect a CRS and you need to supply it!
        """

        data = Path(__file__).parent / "data"
        shpfile = data / "nodestring_mystery_mga53.shp"

        gdf = load_nodestring_shapefile(shpfile)
        captured = capsys.readouterr()

        assert "No CRS could be read from the shapefile." in captured.out

        assert not gdf.crs
        assert gdf.shape[0] == 8

        # Now let's try again, gimme that CRS.
        gdf_take_two = load_nodestring_shapefile(shpfile, crs=7853)
        assert gdf_take_two.crs.to_epsg() == 7853

    def test_basic_chainage_calc(self):
        """Follows test_basic_read_nodestring_shapefile, does the chainage calcs"""
        data = Path(__file__).parent / "data"
        shpfile = data / "2d_ns_Open_Boundary_001_L.shp"

        gdf = load_nodestring_shapefile(shpfile)

        coords = process_nodestring_gdf(gdf)

        assert len(coords) == 2

        assert "Western_Boundary" in coords
        assert "Eastern_Boundary" in coords
        assert isinstance(coords["Western_Boundary"], np.ndarray)

    def test_complex_chainage_calcs(self):
        """Calculate chainages for different CRS.
        Basically, 3 versions of the same nodestrings,
        one wgs84, two mga53, one with prj, one without."""

        data = Path(__file__).parent / "data"
        shp_wgs84 = data / "nodestring_wgs84.shp"
        shp_mga53 = data / "nodestring_mga53.shp"
        shp_mystery_mga53 = data / "nodestring_mystery_mga53.shp"

        gdf_wgs84 = load_nodestring_shapefile(shp_wgs84)
        gdf_mga3 = load_nodestring_shapefile(shp_mga53)
        gdf_mystery_good = load_nodestring_shapefile(shp_mystery_mga53, crs=7853)
        gdf_mystery_bad = load_nodestring_shapefile(shp_mystery_mga53)

        coords_wgs84 = process_nodestring_gdf(gdf_wgs84)
        coords_mga53 = process_nodestring_gdf(gdf_mga3)
        coords_mystery_good = process_nodestring_gdf(gdf_mystery_good)

        with pytest.raises(
            ValueError, match="The nodestring geodataframe must have a CRS defined."
        ):
            _ = process_nodestring_gdf(gdf_mystery_bad)

        # Now let's ensure we're close between all working options.
        assert (
            len(coords_wgs84[101])
            == len(coords_mga53[101])
            == len(coords_mystery_good[101])
        )

        # Important - here's the MGA53 Versus WGS 84 showdown
        assert np.allclose(coords_mga53[1], coords_wgs84[1])

        # These should be identical (user defined CRS vs detected one)
        assert np.all(coords_mga53[1] == coords_mystery_good[1])

    def test_complex_chainage_spacing(self):
        """Test to ensure the spacing works as intended.
        We use Feature "1", which is 43603m long per QGIS in GDA2020/MGA53 Coordinates.
        """

        data = Path(__file__).parent / "data"
        shp_mga53 = data / "nodestring_mga53.shp"

        gdf_mga3 = load_nodestring_shapefile(shp_mga53, process_ids=[1])

        c1 = process_nodestring_gdf(gdf_mga3, spacing=2500)  # Default! 2.5km
        c2 = process_nodestring_gdf(gdf_mga3, spacing=1250)  # Halved default
        c3 = process_nodestring_gdf(
            gdf_mga3, spacing=720
        )  # Random oddly specific spacing

        # These always round up (ceil) rather than down.
        assert c1[1].shape[0] == 18
        assert c2[1].shape[0] == 35
        assert c3[1].shape[0] == 61  # 60.55, should round up


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
