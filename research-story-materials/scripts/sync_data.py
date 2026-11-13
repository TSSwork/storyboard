"""Refresh research-story/data/ from the full research project (only works when research-story sits inside it).

Everything the app and the PNG export read lives in data/. This script copies those files from the analysis
outputs (research_audit/) and raw inputs (raw/) one level up. The app itself never needs this script: the
data/ folder is already a complete snapshot.

Run:  uv run python scripts/sync_data.py
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # research-story-materials
PROJECT = ROOT.parent
DATA = PROJECT / "research-story" / "data"

COPY = {  # file in data/  <-  path in the full project
    "forecast_model_comparison_v2.csv": "research_audit/forecast_model_comparison_v2.csv",
    "forecast_results_v2.csv": "research_audit/forecast_results_v2.csv",
    "rain_window_comparison.csv": "research_audit/forecast_validation_v2/rain_window_comparison.csv",
    "interval_coverage.csv": "research_audit/forecast_validation_v2/interval_coverage.csv",
    "era5_regional_monthly.csv": "research_audit/derived/era5_regional_monthly.csv",
    "era5_monthly.csv": "research_audit/derived/era5_monthly.csv",
    "dcs_national_yala.csv": "research_audit/derived/dcs_national_yala.csv",
    "rice_annual_balance.csv": "research_audit/derived/rice_annual_balance.csv",
    "cbsl_daily_prices.csv": "raw/cbsl-daily-prices.csv",
    "usd_lkr_spot_rate.csv": "raw/pdf/Indicative Rate of the USD_LKR SPOT Exchange Rate.csv",
}
BOUNDARY_SRC = "raw/chirp/boundaries/countries.geojson"  # world file; only the Sri Lanka feature is kept


def main():
    if not (PROJECT / "research_audit").exists():
        sys.exit("Full research project not found next to research-story/. Nothing to sync (the data/ folder is already complete).")
    DATA.mkdir(exist_ok=True)
    for dest, src in COPY.items():
        shutil.copy2(PROJECT / src, DATA / dest)
        print("copied", dest)
    world = json.load(open(PROJECT / BOUNDARY_SRC))
    lka = [f for f in world["features"] if f["properties"].get("ISO3166-1-Alpha-3") == "LKA"]
    json.dump({"type": "FeatureCollection", "features": lka}, open(DATA / "sri_lanka_boundary.geojson", "w"))
    print("wrote sri_lanka_boundary.geojson")


if __name__ == "__main__":
    main()
