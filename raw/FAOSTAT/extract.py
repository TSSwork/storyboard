
#!/usr/bin/env python3

import csv
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR
    / "production"
    / "Production_Crops_Livestock_E_All_Data_(Normalized).csv"
)

OUTPUT_DIR = BASE_DIR / "extracted"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "sri_lanka_crop_production.csv"
)

# --------------------------------------------------
# Filters
# --------------------------------------------------

COUNTRY = "Sri Lanka"

ELEMENT_CODES = {
    "5312",  # Area harvested
    "5412",  # Yield
    "5510",  # Production
}

# --------------------------------------------------
# Extraction
# --------------------------------------------------

def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(INPUT_FILE)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows_written = 0

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as source:

        reader = csv.DictReader(source)

        required_columns = {
            "Area",
            "Item",
            "Item Code",
            "Element Code",
            "Element",
            "Year",
            "Unit",
            "Value",
            "Flag",
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

    print("\nExtraction completed.")
    print(f"Country: {COUNTRY}")
    print(f"Rows extracted: {rows_written}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
