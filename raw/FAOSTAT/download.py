
#!/usr/bin/env python3

import time
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# --------------------------------------------------
# FAOSTAT: Crops and livestock products (QCL)
# --------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent

URL = (
    "https://bulks-faostat.fao.org/production/"
    "Production_Crops_Livestock_E_All_Data_(Normalized).zip"
)

ZIP_FILE = DATA_DIR / "production_crops_livestock_normalized.zip"
TEMP_FILE = DATA_DIR / "production_crops_livestock_normalized.zip.part"

# --------------------------------------------------
# Download
# --------------------------------------------------

def download_file():

    if ZIP_FILE.exists():
        if is_valid_zip(ZIP_FILE):
            print(f"Already downloaded: {ZIP_FILE.name}")
            return
        else:
            print("Existing ZIP is invalid. Removing it.")
            ZIP_FILE.unlink()

    for attempt in range(1, 6):

        try:
            print(f"\nDownloading FAOSTAT QCL")
            print(f"Attempt {attempt}/5")
            print(f"URL: {URL}")

            request = Request(
                URL,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            with urlopen(request, timeout=120) as response:
                total = int(response.headers.get("Content-Length", 0))
                downloaded = 0

                with open(TEMP_FILE, "wb") as file:

                    while True:
                        chunk = response.read(1024 * 1024)

                        if not chunk:
                            break

                        file.write(chunk)
                        downloaded += len(chunk)

                        if total:
                            percent = downloaded * 100 / total
                            print(
                                f"\rDownloaded "
                                f"{downloaded / 1024 / 1024:.1f} MB "
                                f"({percent:.1f}%)",
                                end="",
                                flush=True,
                            )
                        else:
                            print(
                                f"\rDownloaded "
                                f"{downloaded / 1024 / 1024:.1f} MB",
                                end="",
                                flush=True,
                            )

            print()

            if is_valid_zip(TEMP_FILE):
                TEMP_FILE.replace(ZIP_FILE)
                print(f"\nSaved: {ZIP_FILE}")
                return

            print("Downloaded file is not a valid ZIP.")
            TEMP_FILE.unlink(missing_ok=True)

        except (HTTPError, URLError, TimeoutError, OSError) as error:

            print(f"\nDownload error: {error}")
            TEMP_FILE.unlink(missing_ok=True)

        if attempt < 5:
            wait = attempt * 10
            print(f"Retrying in {wait} seconds...")
            time.sleep(wait)

    raise RuntimeError("Download failed after 5 attempts.")


# --------------------------------------------------
# Validate ZIP
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
# Extract
# --------------------------------------------------

def extract_file():

    if not is_valid_zip(ZIP_FILE):
        raise RuntimeError("ZIP file is missing or invalid.")

    extract_dir = DATA_DIR / "production"

    extract_dir.mkdir(exist_ok=True)

    print("\nExtracting FAOSTAT dataset...")

    with zipfile.ZipFile(ZIP_FILE, "r") as archive:

        for member in archive.namelist():

            # Prevent extracting files outside the destination.
            destination = (extract_dir / member).resolve()

            if not destination.is_relative_to(extract_dir.resolve()):
                raise RuntimeError(
                    f"Unsafe archive path: {member}"
                )

        archive.extractall(extract_dir)

    print(f"Extracted to: {extract_dir}")


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    download_file()
    extract_file()

    print("\nFAOSTAT production download completed.")


if __name__ == "__main__":
    main()
