"""Rebuild national ERA5-Land series correctly (read-only on raw data).
- grid cells = cells with finite data (ERA5-Land masks sea as NaN), cos(lat) weights
- tp is ACCUMULATED from 00 UTC (stepType=accum): value at 00:00 of day D+1 = total of day D.
  Hourly series kept raw; daily total(D) := tp at (D+1) 00:00.
Outputs research_audit/derived/era5_national_hourly.csv, era5_daily.csv, era5_monthly.csv, era5_file_checks.csv"""
import xarray as xr, numpy as np, pandas as pd, glob, os
os.chdir(os.path.join(os.path.dirname(__file__), "..", "raw"))
rows, checks = [], []
for f in sorted(glob.glob("EAR5/downloads/*.nc")):
    ds = xr.open_dataset(f)
    w = np.cos(np.deg2rad(ds.latitude))
    land = ds.t2m.isel(valid_time=0).notnull()
    out = {}
    for v in ["t2m", "d2m", "tp"]:
        x = ds[v].where(land)
        out[v] = x.weighted(w.broadcast_like(x).where(land, 0)).mean(["latitude", "longitude"], skipna=True).to_series()
    d = pd.DataFrame(out)
    d["t2m"] -= 273.15; d["d2m"] -= 273.15; d["tp"] *= 1000
    rows.append(d)
    checks.append(dict(file=os.path.basename(f), hours=len(d), first=d.index.min(), last=d.index.max(),
                       land_cells=int(land.sum()), grid=f"{ds.latitude.size}x{ds.longitude.size}",
                       expver=",".join(sorted(set(ds.expver.values.tolist()))), tp_nan=int(d.tp.isna().sum()), t2m_nan=int(d.t2m.isna().sum())))
h = pd.concat(rows).sort_index()
dup = h.index.duplicated().sum()
h = h[~h.index.duplicated(keep="last")]
h.index.name = "valid_time"
h.to_csv("../research_audit/derived/era5_national_hourly.csv")
full = pd.date_range(h.index.min(), h.index.max(), freq="h")
d = pd.DataFrame({"t2m_mean": h.t2m.resample("D").mean(), "t2m_max": h.t2m.resample("D").max(), "t2m_min": h.t2m.resample("D").min(),
                  "d2m_mean": h.d2m.resample("D").mean()})
tp0 = h.tp[h.index.hour == 0]; tp0.index = tp0.index.normalize() - pd.Timedelta(days=1)   # 00UTC(D+1) -> day D
d["rain_mm"] = tp0
d = d[d.index >= h.index.min().normalize()]
d.index.name = "date"; d.to_csv("../research_audit/derived/era5_daily.csv")
m = d.resample("MS").agg({"t2m_mean": "mean", "t2m_max": "mean", "t2m_min": "mean", "d2m_mean": "mean", "rain_mm": "sum"})
m["days_with_rain"] = d.rain_mm.resample("MS").count(); m["days_in_month"] = d.t2m_mean.resample("MS").count()
m.index.name = "month"; m.to_csv("../research_audit/derived/era5_monthly.csv")
pd.DataFrame(checks).to_csv("../research_audit/derived/era5_file_checks.csv", index=False)
print("hourly rows", len(h), "dup hours dropped", dup, "missing hours in range", len(full.difference(h.index)))
