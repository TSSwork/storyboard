
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import Point, Polygon

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR
OUTPUT_DIR = INPUT_DIR / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# SRI LANKA APPROXIMATE COUNTRY BOUNDARY
# Longitude, latitude
# ---------------------------------------------------------

SRI_LANKA = Polygon([
    (79.65, 9.85),
    (80.10, 9.95),
    (80.75, 9.80),
    (81.20, 9.55),
    (81.85, 8.90),
    (81.90, 8.20),
    (81.75, 7.50),
    (81.55, 6.80),
    (81.25, 6.20),
    (80.85, 5.95),
    (80.35, 5.90),
    (79.85, 6.15),
    (79.65, 6.65),
    (79.70, 7.20),
    (79.75, 7.80),
    (79.70, 8.50),
    (79.65, 9.20),
    (79.65, 9.85),
])


# ---------------------------------------------------------
# ERA5 VARIABLE NAMES
# ---------------------------------------------------------

VARIABLES = {
    "t2m": ["t2m", "2m_temperature"],
    "tp": ["tp", "total_precipitation"],
    "d2m": ["d2m", "2m_dewpoint_temperature"],
    "u10": ["u10", "10m_u_component_of_wind"],
    "v10": ["v10", "10m_v_component_of_wind"],
    "ssrd": ["ssrd", "surface_solar_radiation_downwards"],
}


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def find_coordinate(ds, candidates):
    for name in candidates:
        if name in ds.coords:
            return name
        if name in ds.variables:
            return name

    return None


def find_variable(ds, aliases):
    for name in aliases:
        if name in ds.data_vars:
            return name

    return None


def make_country_mask(ds):
    lat_name = find_coordinate(ds, ["latitude", "lat"])
    lon_name = find_coordinate(ds, ["longitude", "lon"])

    if not lat_name or not lon_name:
        raise ValueError("Latitude/longitude coordinates not found.")

    lat = ds[lat_name].values
    lon = ds[lon_name].values

    lon_grid, lat_grid = np.meshgrid(lon, lat)

    mask = np.zeros(lon_grid.shape, dtype=bool)

    for index in np.ndindex(mask.shape):
        mask[index] = SRI_LANKA.contains(
            Point(
                float(lon_grid[index]),
                float(lat_grid[index])
            )
        )

    if not mask.any():
        raise ValueError("No ERA5 grid cells found inside Sri Lanka.")

    return lat_name, lon_name, mask


def area_weighted_mean(data, lat_name, mask):
    latitudes = data[lat_name].values

    weights = np.cos(np.deg2rad(latitudes))
    weights = xr.DataArray(
        weights,
        dims=[lat_name],
        coords={lat_name: data[lat_name]}
    )

    mask_da = xr.DataArray(
        mask,
        dims=[lat_name, find_coordinate(data.to_dataset(), ["longitude", "lon"])],
        coords={
            lat_name: data[lat_name],
            find_coordinate(data.to_dataset(), ["longitude", "lon"]):
                data[find_coordinate(data.to_dataset(), ["longitude", "lon"])]
        }
    )

    return data.where(mask_da).weighted(weights.where(mask_da)).mean(
        dim=[lat_name, find_coordinate(data.to_dataset(), ["longitude", "lon"])],
        skipna=True
    )


# ---------------------------------------------------------
# FIND NETCDF FILES
# ---------------------------------------------------------

files = sorted(INPUT_DIR.rglob("*.nc"))

if not files:
    sys.exit(f"No .nc files found in {INPUT_DIR}")

print(f"Found {len(files)} NetCDF files.")

datasets = []

for file in files:
    print(f"Opening: {file.name}")

    try:
        ds = xr.open_dataset(file, chunks=None)
        datasets.append(ds)
    except Exception as exc:
        print(f"[SKIPPED] {file.name}: {exc}")

if not datasets:
    sys.exit("No readable NetCDF files found.")


# ---------------------------------------------------------
# COMBINE FILES
# ---------------------------------------------------------

try:
    ds = xr.combine_by_coords(
        datasets,
        combine_attrs="drop_conflicts"
    )
except Exception as exc:
    print(f"Could not combine files automatically: {exc}")
    print("Your files may have incompatible dimensions or variables.")
    sys.exit(1)


time_name = find_coordinate(ds, ["valid_time", "time"])
if not time_name:
    sys.exit("No time coordinate found.")

if time_name != "time":
    ds = ds.rename({time_name: "time"})

lat_name, lon_name, country_mask = make_country_mask(ds)

print("\nAvailable variables:")
for name in ds.data_vars:
    print(f"  {name}: {ds[name].attrs.get('units', 'unknown units')}")

print(f"\nSri Lanka grid cells selected: {country_mask.sum()}")


# ---------------------------------------------------------
# EXTRACT NATIONAL DAILY DATA
# ---------------------------------------------------------

daily_results = {}

for standard_name, aliases in VARIABLES.items():

    actual_name = find_variable(ds, aliases)

    if not actual_name:
        print(f"[NOT FOUND] {standard_name}")
        continue

    print(f"[PROCESSING] {standard_name} -> {actual_name}")

    data = ds[actual_name]

    # Select Sri Lankan grid cells
    mask_da = xr.DataArray(
        country_mask,
        dims=[lat_name, lon_name],
        coords={
            lat_name: ds[lat_name],
            lon_name: ds[lon_name]
        }
    )

    data = data.where(mask_da)

    # Area-weighted spatial average
    weights = np.cos(np.deg2rad(ds[lat_name]))

    spatial_weights = weights.broadcast_like(data).where(
        mask_da,
        0
    )

    national = data.weighted(
        spatial_weights
    ).mean(
        dim=[lat_name, lon_name],
        skipna=True
    )

    # Unit conversions
    units = str(data.attrs.get("units", "")).lower()

    if standard_name in ["t2m", "d2m"]:
        if units in ["k", "kelvin"]:
            national = national - 273.15
            national.attrs["units"] = "degC"

    elif standard_name == "tp":
        # ERA5 precipitation is generally in metres.
        # Convert before daily accumulation.
        if units in ["m", "metres", "meters"]:
            national = national * 1000
            national.attrs["units"] = "mm"

        # Accumulated precipitation: sum over the day.
        national = national.resample(time="1D").sum(
            skipna=True,
            min_count=1
        )

    elif standard_name == "ssrd":
        # ERA5-Land accumulated radiation is generally J/m².
        # Daily accumulated energy is converted to MJ/m².
        if units in ["j m**-2", "j/m**2", "j m-2"]:
            national = national / 1_000_000
            national.attrs["units"] = "MJ/m2"

        national = national.resample(time="1D").sum(
            skipna=True,
            min_count=1
        )

    else:
        # Daily averages for temperature, dewpoint and wind.
        national = national.resample(time="1D").mean()

    daily_results[standard_name] = national.to_series()


# ---------------------------------------------------------
# BUILD DAILY CSV
# ---------------------------------------------------------

if not daily_results:
    sys.exit("No supported weather variables were extracted.")

daily = pd.DataFrame(daily_results)
daily.index.name = "date"
daily = daily.reset_index()

daily.to_csv(
    OUTPUT_DIR / "sri_lanka_daily_weather.csv",
    index=False
)

print("\n[COMPLETE] Daily data saved.")


# ---------------------------------------------------------
# BUILD MONTHLY CSV
# ---------------------------------------------------------

monthly_results = {}

for column in daily.columns:
    if column == "date":
        continue

    series = daily.set_index("date")[column]

    if column == "tp" or column == "ssrd":
        monthly_results[column] = series.resample("MS").sum(
            min_count=1
        )
    else:
        monthly_results[column] = series.resample("MS").mean()

monthly = pd.DataFrame(monthly_results)
monthly.index.name = "month"
monthly = monthly.reset_index()

monthly.to_csv(
    OUTPUT_DIR / "sri_lanka_monthly_weather.csv",
    index=False
)

print("[COMPLETE] Monthly data saved.")


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

print("\n" + "=" * 55)
print("ERA5-LAND EXTRACTION SUMMARY")
print("=" * 55)

print(f"Input files: {len(files)}")
print(f"Grid cells: {country_mask.sum()}")
print(f"Daily records: {len(daily)}")
print(f"Monthly records: {len(monthly)}")
print(f"Variables extracted: {', '.join(daily_results.keys())}")

print(f"\nOutput directory: {OUTPUT_DIR}")

print("\nFiles created:")
print("  sri_lanka_daily_weather.csv")
print("  sri_lanka_monthly_weather.csv")

# Close opened datasets
ds.close()
for dataset in datasets:
    dataset.close()
