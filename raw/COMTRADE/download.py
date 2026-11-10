
#!/usr/bin/env python3

import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import dotenv_values

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "annual_api"
FLOW_DIR = OUTPUT_DIR / "flow_pages"
MANIFEST_DIR = OUTPUT_DIR / "manifests"

REPORTER_CODE = 144
START_YEAR = 2010
END_YEAR = 2025

MAX_RECORDS = 100_000

REQUEST_INTERVAL = 1.2
MAX_RETRIES = 5
TIMEOUT = 180

BASE_URL = "https://comtradeapi.un.org/data/v1"

AVAILABILITY_URL = f"{BASE_URL}/getDA/C/A/HS"
DATA_URL = f"{BASE_URL}/get/C/A/HS"

FLOWS = {
    "X": "Exports",
    "M": "Imports",
}


# --------------------------------------------------
# DIRECTORIES
# --------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FLOW_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# API KEYS
# --------------------------------------------------

env = dotenv_values(BASE_DIR / ".env")

API_KEYS = [
    env.get("PRIMARY_KEY"),
    env.get("SECONDARY_KEY"),
]

API_KEYS = [
    key.strip()
    for key in API_KEYS
    if key and key.strip()
]

if not API_KEYS:
    raise RuntimeError("No API keys found in .env")


# --------------------------------------------------
# REQUEST HANDLING
# --------------------------------------------------

session = requests.Session()
last_request_time = 0.0


def rate_limit():
    global last_request_time

    now = time.monotonic()
    wait = REQUEST_INTERVAL - (now - last_request_time)

    if wait > 0:
        time.sleep(wait)

    last_request_time = time.monotonic()


def api_request(url, params):

    last_error = None

    for attempt in range(MAX_RETRIES):

        for key_index, key in enumerate(API_KEYS):

            rate_limit()

            try:
                response = session.get(
                    url,
                    params=params,
                    headers={
                        "Ocp-Apim-Subscription-Key": key,
                        "Accept": "application/json",
                    },
                    timeout=TIMEOUT,
                )

                if response.status_code in (401, 403):
                    last_error = RuntimeError(
                        f"API key {key_index + 1} rejected: "
                        f"HTTP {response.status_code}"
                    )
                    continue

                if response.status_code == 429:

                    retry_after = response.headers.get("Retry-After")

                    try:
                        delay = max(float(retry_after), 5)
                    except (TypeError, ValueError):
                        delay = min(30 * (attempt + 1), 120)

                    print(f"[429] Waiting {delay:.0f} seconds")

                    time.sleep(delay)

                    last_error = RuntimeError("API rate limit")
                    break

                response.raise_for_status()

                result = response.json()

                if result.get("error"):
                    raise RuntimeError(result["error"])

                return result

            except requests.HTTPError as exc:

                status = (
                    exc.response.status_code
                    if exc.response is not None
                    else None
                )

                if status and 400 <= status < 500 and status != 429:
                    raise

                last_error = exc

            except (requests.RequestException, ValueError) as exc:
                last_error = exc

        delay = min(10 * (2 ** attempt), 120)

        print(
            f"[RETRY] Attempt {attempt + 1}/{MAX_RETRIES}: "
            f"{last_error}. Waiting {delay}s"
        )

        time.sleep(delay)

    raise RuntimeError(f"API request failed: {last_error}")


# --------------------------------------------------
# DATA AVAILABILITY
# --------------------------------------------------

def get_available_years():

    print("\nChecking annual data availability...")

    result = api_request(
        AVAILABILITY_URL,
        {"reporterCode": REPORTER_CODE},
    )

    available = []

    for item in result.get("data", []):

        year = int(item["period"])

        if not START_YEAR <= year <= END_YEAR:
            continue

        if int(item["reporterCode"]) != REPORTER_CODE:
            continue

        if item.get("freqCode") != "A":
            continue

        if int(item.get("totalRecords", 0)) <= 0:
            continue

        available.append(item)

    available.sort(key=lambda item: int(item["period"]))

    if not available:
        raise RuntimeError("No annual datasets found.")

    years = [int(item["period"]) for item in available]

    if len(years) != len(set(years)):
        raise RuntimeError("Duplicate annual datasets found.")

    print(f"\nAvailable annual datasets: {len(available)}")

    for item in available:
        print(
            f"{item['period']} | "
            f"{item['classificationCode']} | "
            f"{int(item['totalRecords']):,} records"
        )

    return available


# --------------------------------------------------
# DOWNLOAD ONE TRADE FLOW
# --------------------------------------------------

def download_flow(year, flow_code):

    flow_name = FLOWS[flow_code]

    year_dir = FLOW_DIR / str(year)
    year_dir.mkdir(parents=True, exist_ok=True)

    flow_file = year_dir / f"{flow_code}.json"

    # Reuse an existing verified flow checkpoint.
    if flow_file.exists():

        saved = json.loads(flow_file.read_text(encoding="utf-8"))

        if (
            isinstance(saved, dict)
            and saved.get("year") == year
            and saved.get("flowCode") == flow_code
            and isinstance(saved.get("data"), list)
            and saved.get("count") == len(saved["data"])
        ):

            records = saved["data"]

            print(
                f"[CHECKPOINT] {year} {flow_name}: "
                f"{len(records):,} records"
            )

            return records

        raise RuntimeError(
            f"Invalid checkpoint: {flow_file}. "
            "Inspect or remove it before retrying."
        )

    params = {
        "reporterCode": REPORTER_CODE,
        "period": year,
        "flowCode": flow_code,
        "maxrecords": MAX_RECORDS,
        "includeDesc": "true",
    }

    print(f"[DOWNLOAD] {year}: {flow_name} ({flow_code})")

    result = api_request(DATA_URL, params)

    records = result.get("data", [])
    api_count = int(result.get("count", len(records)))

    if not isinstance(records, list):
        raise RuntimeError(f"{year} {flow_name}: invalid API data.")

    if api_count != len(records):
        raise RuntimeError(
            f"{year} {flow_name}: API count ({api_count}) "
            f"does not match returned rows ({len(records)})."
        )

    if not records:
        raise RuntimeError(
            f"{year} {flow_name}: API returned no records."
        )

    if len(records) >= MAX_RECORDS:
        raise RuntimeError(
            f"{year} {flow_name}: reached the {MAX_RECORDS:,}-record "
            "request limit. The response may be incomplete. "
            "This year has NOT been marked complete."
        )

    # Check that the response contains the requested flow.
    unexpected = {
        record.get("flowCode")
        for record in records
        if record.get("flowCode") != flow_code
    }

    if unexpected:
        raise RuntimeError(
            f"{year} {flow_name}: unexpected flow codes: {unexpected}"
        )

    checkpoint = {
        "year": year,
        "flowCode": flow_code,
        "flowName": flow_name,
        "count": len(records),
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "data": records,
    }

    temporary = flow_file.with_suffix(".tmp")

    temporary.write_text(
        json.dumps(checkpoint, ensure_ascii=False),
        encoding="utf-8",
    )

    os.replace(temporary, flow_file)

    print(
        f"[SUCCESS] {year} {flow_name}: "
        f"{len(records):,} records"
    )

    return records


# --------------------------------------------------
# DOWNLOAD AND BUILD ONE YEAR
# --------------------------------------------------

def download_year(dataset):

    year = int(dataset["period"])
    classification = dataset["classificationCode"]
    expected = int(dataset["totalRecords"])

    output_file = OUTPUT_DIR / f"sri_lanka_trade_{year}.csv"
    manifest_file = MANIFEST_DIR / f"{year}.json"

    print("\n" + "=" * 60)
    print(f"YEAR: {year} | CLASSIFICATION: {classification}")
    print(f"Expected records: {expected:,}")
    print("=" * 60)

    # Skip only a previously verified complete dataset.
    if output_file.exists() and manifest_file.exists():

        manifest = json.loads(manifest_file.read_text())

        if (
            manifest.get("status") == "complete"
            and manifest.get("expected_records") == expected
            and manifest.get("downloaded_records") == expected
            and manifest.get("classification") == classification
        ):
            print(f"[SKIP] {year} already verified")
            return

    all_records = []

    for flow_code in FLOWS:

        records = download_flow(year, flow_code)
        all_records.extend(records)

    # --------------------------------------------------
    # VALIDATE COMBINED DATA
    # --------------------------------------------------

    actual = len(all_records)

    print(f"\n[VALIDATION] {year}")
    print(f"Exports: {sum(r.get('flowCode') == 'X' for r in all_records):,}")
    print(f"Imports: {sum(r.get('flowCode') == 'M' for r in all_records):,}")
    print(f"Combined: {actual:,}")
    print(f"Expected: {expected:,}")

    if actual != expected:
        raise RuntimeError(
            f"{year}: combined flow count ({actual:,}) "
            f"does not match availability ({expected:,}). "
            "CSV has NOT been created."
        )

    # Check for duplicate records.
    unique_records = {
        json.dumps(record, sort_keys=True, ensure_ascii=False)
        for record in all_records
    }

    if len(unique_records) != actual:
        raise RuntimeError(
            f"{year}: duplicate records detected. "
            "CSV has NOT been created."
        )

    # --------------------------------------------------
    # BUILD CSV
    # --------------------------------------------------

    columns = list(
        dict.fromkeys(
            key
            for record in all_records
            for key in record.keys()
        )
    )

    temporary_csv = output_file.with_suffix(".tmp")

    with temporary_csv.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as destination:

        writer = csv.DictWriter(
            destination,
            fieldnames=columns,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(all_records)

    os.replace(temporary_csv, output_file)

    # --------------------------------------------------
    # SAVE MANIFEST
    # --------------------------------------------------

    manifest = {
        "year": year,
        "reporterCode": REPORTER_CODE,
        "classification": classification,
        "expected_records": expected,
        "downloaded_records": actual,
        "exports": sum(
            r.get("flowCode") == "X" for r in all_records
        ),
        "imports": sum(
            r.get("flowCode") == "M" for r in all_records
        ),
        "status": "complete",
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "csv": output_file.name,
    }

    temporary_manifest = manifest_file.with_suffix(".tmp")

    temporary_manifest.write_text(
        json.dumps(manifest, indent=4),
        encoding="utf-8",
    )

    os.replace(temporary_manifest, manifest_file)

    print(f"\n[COMPLETE] {year}")
    print(f"CSV: {output_file}")
    print(f"Records: {actual:,}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("UN COMTRADE ANNUAL DOWNLOADER")
    print("Reporter: Sri Lanka (144)")
    print(f"Years: {START_YEAR}-{END_YEAR}")
    print(f"API keys available: {len(API_KEYS)}")
    print("Workers: 1 (rate limited)")
    print("Download method: Separate imports and exports")

    datasets = get_available_years()

    completed = []
    failed = []

    for dataset in datasets:

        year = int(dataset["period"])

        try:
            download_year(dataset)
            completed.append(year)

        except Exception as exc:
            print(f"\n[FAILED] {year}: {exc}")
            failed.append(year)

    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)

    print(f"Completed: {len(completed)}")
    print(f"Failed: {len(failed)}")

    if completed:
        print("Completed years:", ", ".join(map(str, completed)))

    if failed:
        print("Failed years:", ", ".join(map(str, failed)))
        print("\nFix the issue and run the script again to resume.")

    print("\nDownload process finished.")


if __name__ == "__main__":
    main()
