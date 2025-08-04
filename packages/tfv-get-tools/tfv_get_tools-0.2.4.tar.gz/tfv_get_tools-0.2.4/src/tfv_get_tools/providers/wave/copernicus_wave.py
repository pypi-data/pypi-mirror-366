"""
This copernicus wave model is branched from the Copernicus ocean downloader.
"""

from tfv_get_tools.providers.ocean.copernicus_ocean import (
    DownloadCopernicusOcean,
    MergeCopernicusOcean,
)
import logging


class DownloadCopernicusWave(DownloadCopernicusOcean):
    def _init_specific(self):
        if self.model == "default":
            self.log("Default model has been selected == 'GLO'")
            self.model = "GLO"

        self.source = "COPERNICUS"
        self.mode = "WAVE"
        self._load_config()

        # User login check not yet performed
        self._logged_in = False

        # Cache for temporal extents
        self._temporal_extents_cache = {}

        if not self.verbose:
            logging.getLogger("copernicusmarine").setLevel(logging.WARNING)


class MergeCopernicusWave(MergeCopernicusOcean):
    def _init_specific(self):
        self.source = "COPERNICUS"
        self.mode = "WAVE"
        if self.model == "default":
            self.model = "GLO"
        self._load_config()
