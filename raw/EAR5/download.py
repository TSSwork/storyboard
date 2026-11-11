
import calendar
from pathlib import Path

import cdsapi

# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

START_YEAR = 2010
END_YEAR = 2026

AREA = [10, 79, 5, 82]

VARIABLES = [
    "total_precipitation",
    "2m_temperature",
    "2m_dewpoint_temperature",
]

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "downloads"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------
# DOWNLOAD MONTH
# ---------------------------------------

def download_month(client, year, month):

    output_file = (
        OUTPUT_DIR
        / f"era5_land_{year}_{month:02d}.nc"
    )

    if output_file.exists():
        print(f"Already exists, skipping: {output_file.name}")
        return

    number_of_days = calendar.monthrange(
        year, month
    )[1]

    days = [
        f"{day:02d}"
        for day in range(1, number_of_days + 1)
    ]

    times = [
        f"{hour:02d}:00"
        for hour in range(24)
    ]

    request = {
        "variable": VARIABLES,
        "year": [str(year)],
        "month": [f"{month:02d}"],
        "day": days,
        "time": times,
        "area": AREA,
        "data_format": "netcdf",
        "download_format": "unarchived",
    }

    print(f"\nDownloading {year}-{month:02d}")

    # Download to a temp name, rename when complete, so an interrupted
    # download is never mistaken for a finished file.
    tmp_file = output_file.with_suffix(".nc.part")

    client.retrieve(
        "reanalysis-era5-land",
        request
    ).download(str(tmp_file))

    tmp_file.replace(output_file)

    print(f"Saved: {output_file}")


# ---------------------------------------
# MAIN
# ---------------------------------------

def main():

    client = cdsapi.Client()

    for year in range(START_YEAR, END_YEAR + 1):

        for month in range(1, 13):

            try:
                download_month(
                    client,
                    year,
                    month
                )

            except Exception as error:
                print(
                    f"FAILED {year}-{month:02d}: {error}"
                )

                # Continue with the next month.
                continue

    print("\nAll requested months processed.")


if __name__ == "__main__":
    main()
