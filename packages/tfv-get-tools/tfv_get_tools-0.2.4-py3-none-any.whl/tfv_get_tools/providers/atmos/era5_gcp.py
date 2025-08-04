"""
This ERA5 ATMOS model has been branched from the ERA5 Wave Downloader
"""

from tfv_get_tools.providers.wave.era5 import DownloadERA5Wave, MergeERA5Wave

class DownloadERA5AtmosGCP(DownloadERA5Wave):
    def _init_specific(self):
        self.source = 'ERA5_GCP'
        self.mode = 'ATMOS'
        self._load_config()
        
        # User login check not yet performed
        self._logged_in = False        

class MergeERA5Atmos(MergeERA5Wave):
    def _init_specific(self):
        self.source = 'ERA5'
        self.mode = 'ATMOS'
        self._load_config()