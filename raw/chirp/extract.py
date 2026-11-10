
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import requests
from rasterio.mask import mask
from shapely.geometry import mapping, shape

# --------------------------------------------------
# PATHS
# --------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parents[1]

BOUNDARY_DIR = SCRIPT_DIR / "boundaries"
BOUNDARY_FILE = BOUNDARY_DIR / "countries.geojson"

OUTPUT_DIR = PROJECT_DIR / "raw" / "chirp"

BOUNDARY_URL = (
    "https://raw.githubusercontent.com/"
    "datasets/geo-countries/main/data/countries.geojson"
)

BOUNDARY_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# DOWNLOAD SRI LANKA BOUNDARY
# --------------------------------------------------

def download_boundary():
    if BOUNDARY_FILE.exists():
        print("Using cached country boundaries.")
        return

    print("Downloading country boundaries...")

    response = requests.get(BOUNDARY_URL, timeout=120)
    response.raise_for_status()

    BOUNDARY_FILE.write_bytes(response.content)


def get_sri_lanka_geometry():
    download_boundary()

    with open(BOUNDARY_FILE, encoding="utf-8") as file:
        geojson = json.load(file)

    for feature in geojson["features"]:
        properties = feature["properties"]

        if properties.get("ISO3166-1-Alpha-3") == "LKA":
            return shape(feature["geometry"])

    raise ValueError("Sri Lanka boundary not found.")


# --------------------------------------------------
# EXTRACT RAINFALL
# --------------------------------------------------

def extract_rainfall(tif_file, sri_lanka):
    print(f"\nProcessing: {tif_file.name}")

    with rasterio.open(tif_file) as src:

        geometry = sri_lanka

        # Reproject boundary if raster CRS differs from WGS84.
        if src.crs and src.crs.to_epsg() != 4326:
            from rasterio.warp import transform_geom

            geometry = shape(
                transform_geom(
                    "EPSG:4326",
                    src.crs,
                    mapping(sri_lanka)
                )
            )

        image, transform = mask(
            src,
            [mapping(geometry)],
            crop=True,
            filled=False
        )

        rainfall = image[0]

        rows, cols = np.where(~rainfall.mask)

        values = rainfall.data[rows, cols]

        # Exclude invalid or negative rainfall values.
        valid = np.isfinite(values) & (values >= 0)

        rows = rows[valid]
        cols = cols[valid]
        values = values[valid]

        if len(values) == 0:
            print("No valid rainfall pixels found.")
            return None, None

        # Pixel centre coordinates.
        longitudes, latitudes = rasterio.transform.xy(
            transform,
            rows,
            cols,
            offset="center"
        )

        date_match = re.search(
            r"(\d{4})\.(\d{2})\.(\d{2})",
            tif_file.name
        )

        if not date_match:
            raise ValueError(
                f"Cannot identify date from filename: {tif_file.name}"
            )

        date = "-".join(date_match.groups())

        pixels = pd.DataFrame({
            "date": date,
            "latitude": latitudes,
            "longitude": longitudes,
            "rainfall_mm": values
        })

        daily = pd.DataFrame([{
            "date": date,
            "mean_rainfall_mm": float(np.mean(values)),
            "median_rainfall_mm": float(np.median(values)),
            "min_rainfall_mm": float(np.min(values)),
            "max_rainfall_mm": float(np.max(values)),
            "pixel_count": len(values)
        }])

        print(f"Date: {date}")
        print(f"Valid pixels: {len(values)}")
        print(f"Mean rainfall: {np.mean(values):.2f} mm")

        return pixels, daily


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    sri_lanka = get_sri_lanka_geometry()

    tif_files = sorted(SCRIPT_DIR.glob("chirps-v3.0.rnl.*.tif"))

    if not tif_files:
        print("No CHIRPS TIFF files found.")
        return

    all_pixels = []
    all_daily = []

    for tif_file in tif_files:
        pixels, daily = extract_rainfall(
            tif_file,
            sri_lanka
        )

        if pixels is not None:
            all_pixels.append(pixels)
            all_daily.append(daily)

    if not all_pixels:
        print("No rainfall data extracted.")
        return

    pixel_data = pd.concat(all_pixels, ignore_index=True)
    daily_data = pd.concat(all_daily, ignore_index=True)

    pixel_output = OUTPUT_DIR / "sri_lanka_rainfall_pixels.csv"
    daily_output = OUTPUT_DIR / "sri_lanka_daily_rainfall.csv"

    pixel_data.to_csv(pixel_output, index=False)
    daily_data.to_csv(daily_output, index=False)

    print("\nExtraction completed!")
    print(f"Pixel data: {pixel_output}")
    print(f"Daily summary: {daily_output}")


if __name__ == "__main__":
    main()
