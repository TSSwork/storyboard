
import requests
from dotenv import dotenv_values

env = dotenv_values(".env")
key = env.get("PRIMARY_KEY") or env.get("SECONDARY_KEY")

if not key:
    raise RuntimeError("No API key found in .env")

headers = {
    "Ocp-Apim-Subscription-Key": key,
    "Accept": "application/json",
}

BASE_URL = "https://comtradeapi.un.org/data/v1/getDa"


def check_availability(frequency):
    url = f"{BASE_URL}/C/{frequency}/HS"

    response = requests.get(
        url,
        params={"reporterCode": 144},
        headers=headers,
        timeout=120,
    )

    print(f"\n{'=' * 65}")
    print(f"{frequency} DATA AVAILABILITY")
    print(f"{'=' * 65}")

    print("HTTP:", response.status_code)
    response.raise_for_status()

    result = response.json()
    records = result.get("data", [])

    print("Available datasets:", len(records))

    for item in sorted(records, key=lambda x: x.get("period", 0)):
        period = item.get("period", "")

        if str(period)[:4].isdigit():
            year = int(str(period)[:4])
            if not 2010 <= year <= 2026:
                continue

        print(
            f"Period: {period} | "
            f"Records: {item.get('totalRecords')} | "
            f"Classification: {item.get('classificationCode')} | "
            f"Dataset: {item.get('datasetCode')}"
        )


check_availability("A")
check_availability("M")
