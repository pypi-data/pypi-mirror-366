# Usage

This package provides a set of functions for upscaling instantaneous or daily energy balance and meteorological data to daily evapotranspiration (ET) estimates. Below is a summary of each function and its usage:

[![CI](https://github.com/gregory-halverson-jpl/daily-evapotranspiration-upscaling/actions/workflows/ci.yml/badge.svg)](https://github.com/gregory-halverson-jpl/daily-evapotranspiration-upscaling/actions/workflows/ci.yml)

The `daily-evapotranspiration-upscaling` Python package provides utilities for upscaling energy balance and meteorological data to daily ET, supporting raster, numpy array, and scalar inputs. It is designed for remote sensing, land surface modeling, and geospatial analysis.

[Gregory H. Halverson](https://github.com/gregory-halverson-jpl) (they/them)<br>
[gregory.h.halverson@jpl.nasa.gov](mailto:gregory.h.halverson@jpl.nasa.gov)<br>
NASA Jet Propulsion Laboratory 329G

## Installation

This package is available on PyPI as `daily-evapotranspiration-upscaling` (with dashes):

```bash
pip install daily-evapotranspiration-upscaling
```

## Usage

Import this package as `daily_evapotranspiration_upscaling` (with underscores):

```python
import daily_evapotranspiration_upscaling
```

### 1. `celcius_to_kelvin(T_C)`
- **Description:** Convert Celsius to Kelvin.
- **Parameters:** `T_C` (float, array, or raster): Temperature in Celsius.
- **Returns:** Temperature in Kelvin.

### 2. `lambda_Jkg_from_Ta_K(Ta_K)`
- **Description:** Calculate latent heat of vaporization from air temperature (Kelvin).
- **Parameters:** `Ta_K` (float, array, or raster): Air temperature in Kelvin.
- **Returns:** Latent heat of vaporization (J/kg).

### 3. `lambda_Jkg_from_Ta_C(Ta_C)`
- **Description:** Calculate latent heat of vaporization from air temperature (Celsius).
- **Parameters:** `Ta_C` (float, array, or raster): Air temperature in Celsius.
- **Returns:** Latent heat of vaporization (J/kg).

### 4. `calculate_evaporative_fraction(LE, Rn, G)`
- **Description:** Compute evaporative fraction from latent heat flux, net radiation, and soil heat flux.
- **Parameters:**
	- `LE` (float, array, or raster): Latent heat flux (W/m²)
	- `Rn` (float, array, or raster): Net radiation (W/m²)
	- `G` (float, array, or raster): Soil heat flux (W/m²)
- **Returns:** Evaporative fraction (unitless).

### 5. `daily_ET_from_daily_LE(LE_daylight, ...)`
- **Description:** Estimate daily ET from daily latent heat flux (LE) and supporting parameters.
- **Parameters:** See function docstring for details.
- **Returns:** Daily evapotranspiration (mm/day).

### 6. `daily_ET_from_instantaneous(LE_instantaneous, Rn_instantaneous, G_instantaneous, DOY, lat, hour_of_day, ...)`
- **Description:** Estimate daily ET from instantaneous measurements of latent heat flux, net radiation, and soil heat flux.
- **Parameters:**
	- `LE_instantaneous` (float, array, or raster): Instantaneous latent heat flux (W/m²)
	- `Rn_instantaneous` (float, array, or raster): Instantaneous net radiation (W/m²)
	- `G_instantaneous` (float, array, or raster): Instantaneous soil heat flux (W/m²)
	- `DOY` (int): Day of year
	- `lat` (float): Latitude in degrees
	- `hour_of_day` (float): Local solar time (hours)
- **Returns:** Daily evapotranspiration (mm/day).

# References

- Allen, R.G., Pereira, L.S., Raes, D., Smith, M., 1998. Crop evapotranspiration-Guidelines for computing crop water requirements-FAO Irrigation and drainage paper 56. FAO, Rome, 300(9).
- Bastiaanssen, W.G.M., Menenti, M., Feddes, R.A., Holtslag, A.A.M., 1998. A remote sensing surface energy balance algorithm for land (SEBAL): 1. Formulation. Journal of hydrology, 212, 198-212.
- Duffie, J. A., & Beckman, W. A. (2013). Solar Engineering of Thermal Processes (4th ed.). Wiley.

## License

See [LICENSE](LICENSE) for details.
