
#!/usr/bin/env python3

import csv
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
PRODUCTION_DIR = BASE_DIR / "production"

INPUT_FILE = (
    PRODUCTION_DIR
    / "Production_Crops_Livestock_E_All_Data_(Normalized).csv"
)

OUTPUT_DIR = BASE_DIR / "extracted"
OUTPUT_FILE = OUTPUT_DIR / "sri_lanka_crop_production.csv"

# --------------------------------------------------
# Filters
# --------------------------------------------------

COUNTRY = "Sri Lanka"

# Keep crop production and harvested area.
# We can add other elements after inspecting the dataset.
ELEMENTS = {
    "Production",
    "Area harvested",
    "Yield",
}

# --------------------------------------------------
# Extract
# --------------------------------------------------

def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows_written = 0

    print(f"Input: {INPUT_FILE}")
    print(f"Country: {COUNTRY}")
    print(f"Elements: {', '.join(sorted(ELEMENTS))}")

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as source:

        reader = csv.DictReader(source)

        required_columns = {
            "Area",
            "Item",
            "Element",
            "Year",
            "Unit",
            "Value",
            "Flag",
        }

        missing = required_columns - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                f"Missing expected columns: {missing}"
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

                if row["Element"] not in ELEMENTS:
                    continue

                writer.writerow(row)
                rows_written += 1

    print("\nExtraction completed.")
    print(f"Rows: {rows_written}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
