
#!/usr/bin/env python3

import time
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# --------------------------------------------------
# FAOSTAT TRADE - CROPS AND LIVESTOCK PRODUCTS
# Dataset code: TCL
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DOWNLOAD_DIR = BASE_DIR / "downloads"
OUTPUT_DIR = BASE_DIR / "annual"

URL = (
    "https://bulks-faostat.fao.org/production/"
    "Trade_CropsLivestock_E_All_Data_(Normalized).zip"
)

ZIP_FILE = DOWNLOAD_DIR / "trade_crops_livestock_normalized.zip"
TEMP_FILE = DOWNLOAD_DIR / "trade_crops_livestock_normalized.zip.part"

# --------------------------------------------------
# ZIP validation
# --------------------------------------------------

def is_valid_zip(path):

    if not path.exists() or path.stat().st_size == 0:
        return False

    try:
        with zipfile.ZipFile(path, "r") as archive:
            return archive.testzip() is None

    except (zipfile.BadZipFile, OSError):
        return False


# --------------------------------------------------
# Download
# --------------------------------------------------

def download_file():

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    if ZIP_FILE.exists():

        if is_valid_zip(ZIP_FILE):
            print(f"Already downloaded: {ZIP_FILE}")
            return

        print("Existing ZIP is invalid. Removing it.")
        ZIP_FILE.unlink()

    for attempt in range(1, 6):

        try:

            print(f"\nDownloading FAOSTAT TCL")
            print(f"Attempt {attempt}/5")
            print(f"URL: {URL}")

            request = Request(
                URL,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            with urlopen(request, timeout=180) as response:

                total = int(
                    response.headers.get("Content-Length", 0)
                )

                downloaded = 0

                with open(TEMP_FILE, "wb") as file:

                    while True:

                        chunk = response.read(1024 * 1024)

                        if not chunk:
                            break

                        file.write(chunk)
                        downloaded += len(chunk)

                        mb = downloaded / (1024 * 1024)

                        if total:
                            percent = downloaded * 100 / total
                            print(
                                f"\r{mb:.1f} MB "
                                f"({percent:.1f}%)",
                                end="",
                                flush=True
                            )
                        else:
                            print(
                                f"\r{mb:.1f} MB",
                                end="",
                                flush=True
                            )

            print()

            if is_valid_zip(TEMP_FILE):

                TEMP_FILE.replace(ZIP_FILE)

                print(f"\nDownload complete: {ZIP_FILE}")
                return

            print("ZIP validation failed.")
            TEMP_FILE.unlink(missing_ok=True)

        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError
        ) as error:

            print(f"\nDownload error: {error}")
            TEMP_FILE.unlink(missing_ok=True)

        if attempt < 5:

            wait = attempt * 15

            print(f"Retrying in {wait} seconds...")
            time.sleep(wait)

    raise RuntimeError(
        "FAOSTAT download failed after 5 attempts."
    )


# --------------------------------------------------
# Extract
# --------------------------------------------------

def extract_file():

    if not is_valid_zip(ZIP_FILE):
        raise RuntimeError("ZIP file is missing or invalid.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\nExtracting FAOSTAT trade dataset...")

    with zipfile.ZipFile(ZIP_FILE, "r") as archive:

        for member in archive.namelist():

            destination = (OUTPUT_DIR / member).resolve()

            if not destination.is_relative_to(
                OUTPUT_DIR.resolve()
            ):
                raise RuntimeError(
                    f"Unsafe archive path: {member}"
                )

        archive.extractall(OUTPUT_DIR)

    print(f"Extracted to: {OUTPUT_DIR}")


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    download_file()
    extract_file()

    print("\nFAOSTAT annual trade download completed.")


if __name__ == "__main__":
    main()
