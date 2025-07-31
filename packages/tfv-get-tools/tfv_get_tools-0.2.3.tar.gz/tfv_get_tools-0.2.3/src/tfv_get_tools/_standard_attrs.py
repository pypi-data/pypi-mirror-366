"""
Set of standard variable attributes for the merged dataset
"""

STDVARS = {
    "u10": {
        "long_name": "10m_eastward_wind",
        "standard_name": "eastward_wind",
        "units": "m s-1"
    },
    "v10": {
        "long_name": "10m_northward_wind",
        "standard_name": "northward_wind",
        "units": "m s-1"
    },
    "mslp": {
        "long_name": "mean_sea_level_pressure",
        "standard_name": "air_pressure_at_sea_level",
        "units": "Pa"
    },
    "dlwrf": {
        "long_name": "surface_downward_longwave_flux",
        "standard_name": "surface_downwelling_longwave_flux_in_air",
        "units": "W m-2"
    },
    "dswrf": {
        "long_name": "surface_downward_shortwave_flux",
        "standard_name": "surface_downwelling_shortwave_flux_in_air",
        "units": "W m-2"
    },
    "t2m": {
        "long_name": "2m_air_temperature",
        "standard_name": "air_temperature",
        "units": "K"
    },
    "prate": {
        "long_name": "precipitation_rate",
        "standard_name": "precipitation_flux",
        "units": "kg m-2 s-1"
    },
    "relhum": {
        "long_name": "relative_humidity",
        "standard_name": "relative_humidity",
        "units": "1"
    },
    "water_u": {
        "long_name": "eastward_sea_water_velocity",
        "standard_name": "eastward_sea_water_velocity",
        "units": "m s-1"
    },
    "water_v": {
        "long_name": "northward_sea_water_velocity",
        "standard_name": "northward_sea_water_velocity",
        "units": "m s-1"
    },
    "surf_el": {
        "long_name": "sea_surface_height_above_geoid",
        "standard_name": "sea_surface_height_above_geoid",
        "units": "m"
    },
    "water_temp": {
        "long_name": "sea_water_temperature",
        "standard_name": "sea_water_temperature",
        "units": "K"
    },
    "salinity": {
        "long_name": "sea_water_salinity",
        "standard_name": "sea_water_practical_salinity",
        "units": "1e-3"
    },
    # Wave parameters
    "hs": {
        "long_name": "significant_wave_height",
        "standard_name": "sea_surface_wave_significant_height",
        "units": "m"
    },
    "tp": {
        "long_name": "peak_wave_period",
        "standard_name": "sea_surface_wave_period_at_variance_spectral_density_maximum",
        "units": "s"
    },
    "tm02": {
        "long_name": "mean_wave_period_tm02",
        "standard_name": "sea_surface_wave_mean_period_from_variance_spectral_density_second_frequency_moment",
        "units": "s"
    },
    "tm10": {
        "long_name": "mean_wave_period_tm10",
        "standard_name": "sea_surface_wave_mean_period_from_variance_spectral_density_inverse_frequency_moment",
        "units": "s"
    },
    "mwd": {
        "long_name": "mean_wave_direction",
        "standard_name": "sea_surface_wave_from_direction",
        "units": "degree"
    },
    "pwd": {
        "long_name": "peak_wave_direction",
        "standard_name": "sea_surface_wave_from_direction_at_variance_spectral_density_maximum",
        "units": "degree"
    },
    "spr": {
        "long_name": "mean_wave_directional_spreading",
        "standard_name": "sea_surface_wave_directional_spread",
        "units": "degree"
    }
}