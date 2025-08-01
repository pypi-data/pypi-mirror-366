# daily-evapotranspiration-upscaling

`daily-evapotranspiration-upscaling` is a Python package providing utilities for upscaling instantaneous or daily energy balance and meteorological data to daily evapotranspiration (ET) estimates. It is designed for use with raster (spatial) or array-based data, making it suitable for remote sensing, land surface modeling, and geospatial analysis. The package implements methods based on physical principles of the surface energy balance, commonly used in remote sensing algorithms such as SEBAL and related models. It enables upscaling of point-in-time or daily energy flux measurements to daily evapotranspiration, a key variable in hydrology, agriculture, and climate studies.

Gregory H. Halverson (they/them)<br>
[gregory.h.halverson@jpl.nasa.gov](mailto:gregory.h.halverson@jpl.nasa.gov)<br>
NASA Jet Propulsion Laboratory 329G

## Features

- Convert temperature between Celsius and Kelvin
- Calculate latent heat of vaporization as a function of air temperature
- Compute evaporative fraction from energy balance components
- Estimate daily ET from daily or instantaneous latent heat flux (LE)
- Integrate net radiation over daylight hours using solar geometry
- Support for raster, numpy array, and scalar inputs
- Utilities for daylight duration and sunrise calculations

## Installation

```
pip install daily-evapotranspiration-upscaling
```

## Usage Example

```python
from daily_evapotranspiration_upscaling import daily_ET_from_instantaneous

# Example inputs (replace with your data)
LE_instantaneous = ...  # Latent heat flux (W/m^2)
Rn_instantaneous = ...  # Net radiation (W/m^2)
G_instantaneous = ...   # Soil heat flux (W/m^2)
DOY = 150               # Day of year
lat = 34.0              # Latitude in degrees
hour_of_day = 13.0      # Local solar time

ET_daily = daily_ET_from_instantaneous(
	LE_instantaneous_Wm2=LE_instantaneous,
	Rn_instantaneous_Wm2=Rn_instantaneous,
	G_instantaneous_Wm2=G_instantaneous,
	DOY=DOY,
	lat=lat,
	hour_of_day=hour_of_day
)
print(ET_daily)
```

## API Reference

- `celcius_to_kelvin(T_C)`: Convert Celsius to Kelvin
- `lambda_Jkg_from_Ta_K(Ta_K)`: Latent heat of vaporization from temperature (K)
- `lambda_Jkg_from_Ta_C(Ta_C)`: Latent heat of vaporization from temperature (C)
- `calculate_evaporative_fraction(LE, Rn, G)`: Compute evaporative fraction
- `daily_ET_from_daily_LE(LE_daylight, ...)`: Daily ET from daily LE
- `daily_ET_from_instantaneous(LE_instantaneous, Rn_instantaneous, G_instantaneous, ...)`: Daily ET from instantaneous measurements

## License

See [LICENSE](LICENSE) for details.
