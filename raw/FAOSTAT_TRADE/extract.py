
#!/usr/bin/env python3

import csv
from collections import Counter
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR
    / "annual"
    / "Trade_CropsLivestock_E_All_Data_(Normalized).csv"
)

OUTPUT_DIR = BASE_DIR / "extracted"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "sri_lanka_agricultural_trade.csv"
)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

COUNTRY = "Sri Lanka"

ELEMENT_CODES = {
    "5607", "5608", "5609", "5610",  # Import quantity
    "5622",                         # Import value
    "5907", "5908", "5909", "5910",  # Export quantity
    "5922",                         # Export value
}

# --------------------------------------------------
# Extraction
# --------------------------------------------------

def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(INPUT_FILE)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows_written = 0
    element_counts = Counter()
    years = set()
    items = set()
    missing_values = 0

    print("Extracting FAOSTAT agricultural trade data...")
    print(f"Country: {COUNTRY}")

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as source:

        reader = csv.DictReader(source)

        required_columns = {
            "Area",
            "Item Code",
            "Item",
            "Element Code",
            "Element",
            "Year",
            "Unit",
            "Value",
            "Flag",
            "Note",
        }

        missing = required_columns - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

        with OUTPUT_FILE.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as destination:

            writer = csv.DictWriter(
                destination,
                fieldnames=reader.fieldnames
            )

            writer.writeheader()

            for row in reader:

                if row["Area"] != COUNTRY:
                    continue

                if row["Element Code"] not in ELEMENT_CODES:
                    continue

                writer.writerow(row)

                rows_written += 1

                element_counts[
                    (row["Element Code"], row["Element"])
                ] += 1

                years.add(int(row["Year"]))
                items.add(row["Item Code"])

                if not row["Value"].strip():
                    missing_values += 1

    # --------------------------------------------------
    # Report
    # --------------------------------------------------

    print("\nExtraction completed.")
    print("-" * 45)

    print(f"Country: {COUNTRY}")
    print(f"Records extracted: {rows_written}")
    print(f"Unique commodities: {len(items)}")

    if years:
        print(f"Year range: {min(years)} - {max(years)}")
        print(f"Number of years: {len(years)}")

    print(f"Missing values: {missing_values}")

    print("\nRecords by element:")

    for (code, name), count in sorted(element_counts.items()):
        print(f"{code} | {name}: {count}")

    print(f"\nOutput: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
