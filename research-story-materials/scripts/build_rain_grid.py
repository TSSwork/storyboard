"""Build research-story/data/era5_rain_grid.csv: monthly rainfall (mm) for every ERA5-Land cell over Sri Lanka, for the rain map.

Same corrected rule as research_audit/era5_validate.py: tp is accumulated from 00 UTC, so the total of day D is
tp at 00:00 UTC of day D+1 (x1000 for mm). A month is kept only when every day is present.
Read-only on ../raw/. Needs the full research project one level up and xarray (run it from the parent project's env):
    cd .. && uv run python research-story-materials/scripts/build_rain_grid.py
"""
from pathlib import Path

import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parent.parent          # research-story-materials
APP = ROOT.parent / "research-story"
RAW = ROOT.parent / "raw/EAR5/downloads"

daily = []
for f in sorted(RAW.glob("era5_land_*.nc")):
    with xr.open_dataset(f) as ds:
        tp = ds.tp.sel(valid_time=ds.valid_time.dt.hour == 0).load()
    s = tp.to_dataframe(name="tp")["tp"].dropna().reset_index()
    s["day"] = s.valid_time.dt.normalize() - pd.Timedelta(days=1)
    daily.append(s[["day", "latitude", "longitude", "tp"]])
d = pd.concat(daily).drop_duplicates(["day", "latitude", "longitude"])
d["month"] = d.day.dt.to_period("M").dt.to_timestamp()
m = d.groupby(["month", "latitude", "longitude"]).agg(rain_mm=("tp", "sum"), n=("tp", "size")).reset_index()
m = m[m.n == m.month.dt.days_in_month]
m["rain_mm"] = (m.rain_mm * 1000).round(1)
out = m.rename(columns={"latitude": "lat", "longitude": "lon"})[["month", "lat", "lon", "rain_mm"]]
out["month"] = out.month.dt.strftime("%Y-%m")
dest = APP / "data/era5_rain_grid.csv"
out.to_csv(dest, index=False)
print(f"wrote {dest.name}: {len(out)} rows, {out.month.nunique()} months, {out.groupby('month').size().max()} cells/month")
