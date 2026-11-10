
from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import httpx

API_URL = (
    "https://microdata.worldbank.org/"
    "api/tables/data/fcv/wld_2021_rtfp_v02_m"
)

COUNTRY_CODE = "LKA"
PAGE_SIZE = 1000

OUTPUT_DIR = Path(__file__).resolve().parent

CSV_FILE = OUTPUT_DIR / "food_prices_lka.csv"
JSONL_FILE = OUTPUT_DIR / "food_prices_lka.jsonl"

TEMP_CSV = OUTPUT_DIR / "food_prices_lka.csv.part"
TEMP_JSONL = OUTPUT_DIR / "food_prices_lka.jsonl.part"


def fetch_page(
    client: httpx.Client,
    offset: int,
) -> dict:
    """Fetch one page from the World Bank Data API."""

    params = {
        "format": "json",
        "limit": PAGE_SIZE,
        "offset": offset,
    }

    for attempt in range(4):
        try:
            response = client.get(API_URL, params=params)
            response.raise_for_status()

            payload = response.json()

            if "data" not in payload:
                raise RuntimeError(
                    f"Unexpected API response: {payload}"
                )

            return payload

        except (httpx.HTTPError, ValueError):
            if attempt == 3:
                raise

            wait_seconds = 2 ** attempt
            print(f"Request failed. Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)

    raise RuntimeError("Unable to retrieve API data.")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    country_rows = 0
    total_rows = None
    fieldnames = None

    headers = {
        "User-Agent": "SriLankaFoodResearch/1.0",
        "Accept": "application/json",
    }

    print("Connecting to World Bank Data API...")

    try:
        with httpx.Client(
            timeout=90,
            follow_redirects=True,
            headers=headers,
        ) as client:

            with (
                TEMP_CSV.open(
                    "w", newline="", encoding="utf-8"
                ) as csv_file,
                TEMP_JSONL.open(
                    "w", encoding="utf-8"
                ) as json_file,
            ):
                csv_writer = None
                offset = 0

                while True:
                    payload = fetch_page(client, offset)

                    rows = payload["data"]

                    if total_rows is None:
                        total_rows = int(
                            payload.get(
                                "total",
                                payload.get("found", 0),
                            )
                        )

                        print(f"Total API observations: {total_rows:,}")

                    if not rows:
                        break

                    downloaded += len(rows)

                    # The API table contains multiple countries.
                    sri_lanka_rows = [
                        row
                        for row in rows
                        if row.get("ISO3") == COUNTRY_CODE
                    ]

                    if sri_lanka_rows:
                        if fieldnames is None:
                            fieldnames = list(rows[0].keys())

                            csv_writer = csv.DictWriter(
                                csv_file,
                                fieldnames=fieldnames,
                                extrasaction="ignore",
                            )
                            csv_writer.writeheader()

                        for row in sri_lanka_rows:
                            # Preserve the original API record as JSON.
                            json_file.write(
                                json.dumps(
                                    row,
                                    ensure_ascii=False,
                                ) + "\n"
                            )

                            # Also write it as CSV for analysis.
                            csv_writer.writerow(row)

                        country_rows += len(sri_lanka_rows)

                    offset += len(rows)

                    print(
                        f"Scanned {downloaded:,}/{total_rows:,} "
                        f"| Sri Lanka records: {country_rows:,}",
                        end="\r",
                        flush=True,
                    )

                    if downloaded >= total_rows:
                        break

                    # Avoid sending requests too rapidly.
                    time.sleep(0.15)

        # Only replace final files after successful completion.
        if country_rows == 0:
            raise RuntimeError(
                "No LKA records were found. Check the ISO3 field "
                "and API response."
            )

        TEMP_CSV.replace(CSV_FILE)
        TEMP_JSONL.replace(JSONL_FILE)

        print("\n\nDownload completed.")
        print(f"API records scanned: {downloaded:,}")
        print(f"Sri Lanka records:   {country_rows:,}")
        print(f"CSV:  {CSV_FILE}")
        print(f"JSON: {JSONL_FILE}")

    except Exception:
        print("\nDownload did not complete.")
        print("Temporary .part files are retained for inspection.")
        raise


if __name__ == "__main__":
    main()
