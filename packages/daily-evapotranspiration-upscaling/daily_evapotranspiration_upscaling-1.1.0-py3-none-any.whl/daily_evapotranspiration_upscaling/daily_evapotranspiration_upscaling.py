import datetime
from datetime import datetime
from typing import Union
from sun_angles import SHA_deg_from_DOY_lat, daylight_from_SHA, sunrise_from_SHA, calculate_daylight
from dateutil import parser
import rasters as rt
from rasters import Raster
import numpy as np
import pandas as pd

from rasters import SpatialGeometry

from verma_net_radiation import daily_Rn_integration_verma

# latent heat of vaporization for water at 20 Celsius in Joules per kilogram
LAMBDA_JKG_WATER_20C = 2450000.0

def celcius_to_kelvin(T_C: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    convert temperature in celsius to kelvin.
    :param T_C: temperature in celsius
    :return: temperature in kelvin
    """
    return T_C + 273.15

def lambda_Jkg_from_Ta_K(Ta_K: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    # Calculate the latent heat of vaporization (J kg-1)
    return (2.501 - 0.002361 * (Ta_K - 273.15)) * 1e6

def lambda_Jkg_from_Ta_C(Ta_C: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    Ta_K = celcius_to_kelvin(Ta_C)
    lambda_Jkg = lambda_Jkg_from_Ta_K(Ta_K)

    return lambda_Jkg

def calculate_evaporative_fraction(
        LE: Union[Raster, np.ndarray],
        Rn: Union[Raster, np.ndarray],
        G: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate the evaporative fraction.
    """
    return rt.where((LE == 0) | ((Rn - G) == 0), 0, LE / (Rn - G))

def daily_ET_from_daily_LE(
        LE_daylight: Union[Raster, np.ndarray, float], 
        daylight_hours: Union[Raster, np.ndarray, float] = None,
        DOY: Union[Raster, np.ndarray, int] = None,
        lat: Union[Raster, np.ndarray, float] = None,
        datetime_UTC: datetime = None,
        geometry: SpatialGeometry = None,
        lambda_Jkg: Union[Raster, np.ndarray, float] = LAMBDA_JKG_WATER_20C) -> Union[Raster, np.ndarray]:
    """
    Calculate daily evapotranspiration (ET) from daily latent heat flux (LE).

    Parameters:
        LE_daily (Union[Raster, np.ndarray]): Daily latent heat flux.
        daylight_hours (Union[Raster, np.ndarray]): Length of day in hours.
        latent_vaporization (float, optional): Latent heat of vaporization. Defaults to LATENT_VAPORIZATION.

    Returns:
        Union[Raster, np.ndarray]: Daily evapotranspiration in kilograms.
    """
    if daylight_hours is None:
        daylight_hours = calculate_daylight(DOY=DOY, lat=lat, datetime_UTC=datetime_UTC, geometry=geometry)

    # convert length of day in hours to seconds
    daylight_seconds = daylight_hours * 3600.0

    # factor seconds out of watts to get joules and divide by latent heat of vaporization to get kilograms
    ET_daily_kg = rt.clip(LE_daylight * daylight_seconds / LAMBDA_JKG_WATER_20C, 0.0, None)

    return ET_daily_kg

def daily_ET_from_instantaneous(
        LE_instantaneous_Wm2: Union[Raster, np.ndarray, float],
        Rn_instantaneous_Wm2: Union[Raster, np.ndarray, float],
        G_instantaneous_Wm2: Union[Raster, np.ndarray, float],
        day_of_year: Union[Raster, np.ndarray, int] = None,
        lat: Union[Raster, np.ndarray, float] = None,
        hour_of_day: Union[Raster, np.ndarray, float] = None,
        sunrise_hour: Union[Raster, np.ndarray, float] = None,
        daylight_hours: Union[Raster, np.ndarray, float] = None,
        time_UTC: Union[datetime, str, np.ndarray, list] = None,
        geometry: SpatialGeometry = None,
        lambda_Jkg: Union[Raster, np.ndarray, float] = LAMBDA_JKG_WATER_20C
    ) -> Union[Raster, np.ndarray]:
    """
    Calculate daily evapotranspiration (ET) from instantaneous latent heat flux (LE).

    Parameters:
        LE_instantaneous_Wm2 (Union[Raster, np.ndarray]): Instantaneous latent heat flux.
        Rn_instantaneous_Wm2 (Union[Raster, np.ndarray]): Instantaneous net radiation.
        G_instantaneous_Wm2 (Union[Raster, np.ndarray]): Instantaneous soil heat flux.
        lambda_Jkg (float, optional): Latent heat of vaporization. Defaults to LAMBDA_JKG_WATER_20C.

    Returns:
        Union[Raster, np.ndarray]: Daily evapotranspiration in kilograms.
    """
    if lat is None and geometry is not None:
        lat = geometry.lat

    # Calculate evaporative fraction
    EF = calculate_evaporative_fraction(
        LE=LE_instantaneous_Wm2,
        Rn=Rn_instantaneous_Wm2,
        G=G_instantaneous_Wm2
    )

    # Calculate daylight hours if not provided
    if daylight_hours is None:
        daylight_hours = calculate_daylight(
            day_of_year=day_of_year,
            lat=lat,
            time_UTC=time_UTC,
            geometry=geometry
        )

    # Calculate sunrise hour if not provided
    if sunrise_hour is None:
        sunrise_hour = sunrise_from_SHA(SHA_deg_from_DOY_lat(day_of_year, lat))

    # Integrate net radiation over the day
    Rn_daylight = daily_Rn_integration_verma(
        Rn=Rn_instantaneous_Wm2,
        hour_of_day=hour_of_day,
        DOY=day_of_year,
        lat=lat,
        sunrise_hour=sunrise_hour,
        daylight_hours=daylight_hours
    )

    # Calculate latent heat flux during daylight
    LE_daylight = EF * Rn_daylight

    # Calculate daily ET
    ET = daily_ET_from_daily_LE(LE_daylight, daylight_hours=daylight_hours, DOY=day_of_year, lat=lat, datetime_UTC=time_UTC, geometry=geometry, lambda_Jkg=lambda_Jkg)

    return ET
