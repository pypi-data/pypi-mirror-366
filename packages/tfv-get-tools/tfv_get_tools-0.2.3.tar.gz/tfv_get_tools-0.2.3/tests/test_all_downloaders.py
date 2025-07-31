"""Integration tests for downloaders with TEST_MODE enabled.
I.e loopy boy through a bunch of downloaders but don't actually hit API endpoints
Basically a test that the configs work and the coordinates validate ok, etc."""

import tempfile
import pytest

from tfv_get_tools import DownloadAtmos, DownloadOcean, DownloadWave


# Loopy test :) Add new sources here
# Turned off Copernicus because of login checks
# We could mock this properly but I think it 
# is low value... 
# There is a test for login failure low which will only trigger
# if it asks for stdin user/password, which means it is working 
@pytest.mark.parametrize(
    "source,downloader_class,model",
    [
        # ("COPERNICUS", DownloadOcean, "GLO"),
        # ("COPERNICUS", DownloadWave, "GLO"),
        ("HYCOM", DownloadOcean, None),
        ("CAWCR", DownloadWave, "glob_24m"),
        ("CAWCR", DownloadWave, "aus_10m"),
        ("CAWCR", DownloadWave, "aus_4m"),
        ("ERA5", DownloadWave, None),
        ("ERA5", DownloadAtmos, None),
        ("CFSR", DownloadAtmos, None),
        ("BARRA2", DownloadAtmos, "C2"),
    ],
)
def test_downloader_parametrised(source, downloader_class, model):
    """Parametrised test for all downloader combinations.
    It doesn't test anything specifically, just that it didn't break!"""
    with tempfile.TemporaryDirectory() as temp_dir:
        kwargs = {
            "start_date": "2022-01-01",
            "end_date": "2022-03-01",
            "xlims": (114.59198035, 116.15009382),
            "ylims": (-33.00931284, -31.20154456),
            "source": source,
            "out_path": temp_dir,
            "TEST_MODE": True,
            "skip_check": True,
        }

        # Only add model if it's not None
        if model is not None:
            kwargs["model"] = model

        result = downloader_class(**kwargs)
        assert result is not None


class TestDownloaderIntegration:
    """Integration tests for all downloader sources with TEST_MODE."""

    # Test parameters
    start_date = "2022-01-01"
    end_date = "2022-03-01"
    xlims = (114.59198035, 116.15009382)
    ylims = (-33.00931284, -31.20154456)
    test_mode = True
    skip_check = True

    def test_copernicus_ocean_glo(self):
        """Test COPERNICUS ocean downloader with GLO model.
        These could be better - I am testing that copernicus kicks off ok
        and that it triggers a manual user login via terminal"""
        with tempfile.TemporaryDirectory() as temp_dir:
            
            with pytest.raises(OSError,
                               match="reading from stdin"):
                result = DownloadOcean(
                    start_date=self.start_date,
                    end_date=self.end_date,
                    xlims=self.xlims,
                    ylims=self.ylims,
                    source="COPERNICUS",
                    model="GLO",
                    out_path=temp_dir,
                    TEST_MODE=self.test_mode,
                    skip_check=self.skip_check,
                )
            

    def test_copernicus_wave_glo(self):
        """Test COPERNICUS wave downloader with GLO model.
        These could be better - I am testing that copernicus kicks off ok
        and that it triggers a manual user login via terminal"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(OSError,
                    match="reading from stdin"):
                result = DownloadWave(
                    start_date=self.start_date,
                    end_date=self.end_date,
                    xlims=self.xlims,
                    ylims=self.ylims,
                    source="COPERNICUS",
                    model="GLO",
                    out_path=temp_dir,
                    TEST_MODE=self.test_mode,
                    skip_check=self.skip_check,
                )

    def test_hycom_ocean(self):
        """Test HYCOM ocean downloader."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadOcean(
                start_date=self.start_date,
                end_date=self.end_date,
                xlims=self.xlims,
                ylims=self.ylims,
                source="HYCOM",
                out_path=temp_dir,
                TEST_MODE=self.test_mode,
                skip_check=self.skip_check,
            )
            assert result is not None

    def test_cawcr_wave_glob_24m(self):
        """Test CAWCR wave downloader with glob_24m model."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadWave(
                start_date=self.start_date,
                end_date=self.end_date,
                xlims=self.xlims,
                ylims=self.ylims,
                source="CAWCR",
                model="glob_24m",
                out_path=temp_dir,
                TEST_MODE=self.test_mode,
                skip_check=self.skip_check,
            )
            assert result is not None

    def test_cawcr_wave_aus_10m(self):
        """Test CAWCR wave downloader with aus_10m model."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadWave(
                start_date=self.start_date,
                end_date=self.end_date,
                xlims=self.xlims,
                ylims=self.ylims,
                source="CAWCR",
                model="aus_10m",
                out_path=temp_dir,
                TEST_MODE=self.test_mode,
                skip_check=self.skip_check,
            )
            assert result is not None

    def test_cawcr_wave_aus_4m(self):
        """Test CAWCR wave downloader with aus_4m model."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadWave(
                start_date=self.start_date,
                end_date=self.end_date,
                xlims=self.xlims,
                ylims=self.ylims,
                source="CAWCR",
                model="aus_4m",
                out_path=temp_dir,
                TEST_MODE=self.test_mode,
                skip_check=self.skip_check,
            )
            assert result is not None

    def test_era5_wave(self):
        """Test ERA5 wave downloader."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadWave(
                start_date=self.start_date,
                end_date=self.end_date,
                xlims=self.xlims,
                ylims=self.ylims,
                source="ERA5",
                out_path=temp_dir,
                TEST_MODE=self.test_mode,
                skip_check=self.skip_check,
            )
            assert result is not None

    def test_era5_atmos(self):
        """Test ERA5 atmospheric downloader."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadAtmos(
                start_date=self.start_date,
                end_date=self.end_date,
                xlims=self.xlims,
                ylims=self.ylims,
                source="ERA5",
                out_path=temp_dir,
                TEST_MODE=self.test_mode,
                skip_check=self.skip_check,
            )
            assert result is not None

    def test_cfsr_atmos(self):
        """Test CFSR atmospheric downloader."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadAtmos(
                start_date=self.start_date,
                end_date=self.end_date,
                xlims=self.xlims,
                ylims=self.ylims,
                source="CFSR",
                out_path=temp_dir,
                TEST_MODE=self.test_mode,
                skip_check=self.skip_check,
            )
            assert result is not None

    def test_barra2_atmos_c2(self):
        """Test BARRA2 atmospheric downloader with C2 model."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DownloadAtmos(
                start_date=self.start_date,
                end_date=self.end_date,
                xlims=self.xlims,
                ylims=self.ylims,
                source="BARRA2",
                model="C2",
                out_path=temp_dir,
                TEST_MODE=self.test_mode,
                skip_check=self.skip_check,
            )
            assert result is not None
