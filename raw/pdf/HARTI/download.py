# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
#     "beautifulsoup4",
# ]
# ///
"""Download HARTI Weekly Food Commodities Bulletin PDFs.

Usage:
    uv run download.py                      # everything, English and Sinhala
    uv run download.py --lang english       # English only
    uv run download.py --years 2026 2025    # selected years
    uv run download.py --html page.html     # parse a saved copy of the page
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://www.harti.gov.lk/weekly-price.php"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HEADERS = {"User-Agent": "Mozilla/5.0 (personal research downloader)"}


def load_html(args: argparse.Namespace) -> str:
    if args.html:
        return Path(args.html).read_text(encoding="utf-8", errors="replace")
    resp = requests.get(PAGE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_rows(html: str) -> list[dict]:
    """Return one dict per table row: start, end, english url, sinhala url."""
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict] = []
    for tr in soup.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) < 4:
            continue
        start = cells[0].get_text(strip=True)
        end = cells[1].get_text(strip=True)
        if not (DATE_RE.match(start) and DATE_RE.match(end)):
            continue
        links = {}
        for lang, cell in (("english", cells[2]), ("sinhala", cells[3])):
            a = cell.find("a", href=True)
            if a:
                links[lang] = urljoin(PAGE_URL, a["href"])
        rows.append({"start": start, "end": end, **links})
    return rows


def allowed_by_robots(url: str) -> bool:
    rp = RobotFileParser()
    rp.set_url(urljoin(PAGE_URL, "/robots.txt"))
    try:
        rp.read()
    except Exception:
        return True
    return rp.can_fetch(HEADERS["User-Agent"], url)


def download(session: requests.Session, url: str, dest: Path) -> str:
    if dest.exists() and dest.stat().st_size > 0:
        return "skipped"
    resp = session.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    if not resp.content.startswith(b"%PDF"):
        return "not a pdf"
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    tmp.write_bytes(resp.content)
    tmp.replace(dest)
    return "ok"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="harti_bulletins", help="output folder")
    ap.add_argument("--lang", choices=["english", "sinhala", "both"], default="both")
    ap.add_argument("--years", nargs="*", help="only these years, for example 2026 2025")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between downloads")
    ap.add_argument("--html", help="parse a saved HTML file instead of fetching the page")
    ap.add_argument("--ignore-robots", action="store_true", help="skip the robots.txt check")
    args = ap.parse_args()

    rows = parse_rows(load_html(args))
    if not rows:
        print(
            "No bulletin rows found. The tables may be loaded by JavaScript.\n"
            "Open the page in your browser, use Save As to store the full HTML,\n"
            "then run: uv run download.py --html saved_page.html",
            file=sys.stderr,
        )
        return 1

    years = set(args.years) if args.years else None
    langs = ["english", "sinhala"] if args.lang == "both" else [args.lang]
    out = Path(args.out)

    jobs = []
    for row in rows:
        year = row["start"][:4]
        if years and year not in years:
            continue
        for lang in langs:
            url = row.get(lang)
            if url:
                name = f"{row['start']}_to_{row['end']}_{lang}.pdf"
                jobs.append((url, out / year / name))

    print(f"Found {len(rows)} weeks, {len(jobs)} files to consider.")
    if not args.ignore_robots and jobs and not allowed_by_robots(jobs[0][0]):
        print("robots.txt disallows fetching these files. Use --ignore-robots only if you are sure.", file=sys.stderr)
        return 2

    counts = {"ok": 0, "skipped": 0, "not a pdf": 0, "failed": 0}
    with requests.Session() as session:
        for i, (url, dest) in enumerate(jobs, 1):
            try:
                status = download(session, url, dest)
            except requests.RequestException as exc:
                status = "failed"
                print(f"[{i}/{len(jobs)}] {dest.name}: {exc}", file=sys.stderr)
            else:
                print(f"[{i}/{len(jobs)}] {dest.name}: {status}")
            counts[status] += 1
            if status == "ok":
                time.sleep(args.delay)

    print("Done.", counts)
    return 0 if counts["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
