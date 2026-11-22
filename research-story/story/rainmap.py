"""Rainfall across Sri Lanka, cell by cell, for the rain map (data/era5_rain_grid.csv, built by ../research-story-materials/scripts/build_rain_grid.py).

No Streamlit here; tested in ../research-story-materials/tests/test_rain_grid.py against the corrected national and Dambulla-box series.
"""
import json
from functools import cache

import numpy as np
import pandas as pd

from story.common import DATA

BOXES = {"Dambulla": (7.86, 80.65), "Nuwara Eliya": (6.97, 80.77)}   # rain boxes used in the study, ±0.3°
ALL_BOXES = {
    "Dambulla": (7.86, 80.65),
    "Nuwara Eliya": (6.97, 80.77),
    "Colombo": (6.94, 79.85),
}
HALF = 0.3


@cache
def grid() -> pd.DataFrame:
    return pd.read_csv(DATA / "era5_rain_grid.csv", parse_dates=["month"])


def months() -> list[pd.Timestamp]:
    return sorted(grid().month.unique())


def month_map(month: pd.Timestamp) -> pd.DataFrame:
    g = grid()
    return g[g.month == month][["lat", "lon", "rain_mm"]].reset_index(drop=True)


def typical_map(calendar_month: int) -> pd.DataFrame:
    """Average rainfall for one calendar month over every year in the grid."""
    g = grid()
    g = g[g.month.dt.month == calendar_month]
    return g.groupby(["lat", "lon"], as_index=False).rain_mm.mean()


def box_series(place: str) -> pd.Series:
    """Cosine-latitude-weighted monthly rainfall series (mm) for a ±0.3° box around Dambulla, Nuwara Eliya, or Colombo."""
    la, lo = ALL_BOXES[place]
    g = grid()
    sub = g[(g.lat >= la - HALF) & (g.lat <= la + HALF) & (g.lon >= lo - HALF) & (g.lon <= lo + HALF)].copy()
    sub["w"] = np.cos(np.deg2rad(sub["lat"]))
    sub["wr"] = sub["rain_mm"] * sub["w"]
    agg = sub.groupby("month")[["wr", "w"]].sum()
    return (agg["wr"] / agg["w"]).sort_index()


def summary(month: pd.Timestamp) -> dict:
    m = month_map(month)
    w = np.cos(np.deg2rad(m.lat))
    top = m.loc[m.rain_mm.idxmax()]
    return dict(island_mm=float((m.rain_mm * w).sum() / w.sum()), wettest_mm=float(top.rain_mm), wettest_lat=float(top.lat),
                wettest_lon=float(top.lon), driest_mm=float(m.rain_mm.min()))


@cache
def _outer_rings() -> list[np.ndarray]:
    g = json.load(open(DATA / "sri_lanka_boundary.geojson"))
    f = [x for x in g["features"] if x["properties"].get("ISO3166-1-Alpha-3") == "LKA"][0]
    return [np.array(poly[0]) for poly in f["geometry"]["coordinates"]]


def _inside(lon: np.ndarray, lat: np.ndarray, ring: np.ndarray) -> np.ndarray:
    """Ray-casting point-in-polygon, vectorised over the points."""
    x, y = ring[:, 0], ring[:, 1]
    x2, y2 = np.roll(x, -1), np.roll(y, -1)
    out = np.zeros(lon.shape, dtype=bool)
    for a, b, c, d in zip(x, y, x2, y2):
        crosses = (b > lat) != (d > lat)
        with np.errstate(divide="ignore", invalid="ignore"):
            xint = (c - a) * (lat - b) / (d - b) + a
        out ^= crosses & (lon < xint)
    return out


def on_island(df: pd.DataFrame) -> pd.DataFrame:
    """Drop cells that lie wholly at sea (ERA5-Land's land mask is coarser than the coastline). For the map only; the series still use every cell."""
    keep = np.zeros(len(df), dtype=bool)
    lon, lat = df.lon.to_numpy(), df.lat.to_numpy()
    h = 0.05
    for dx, dy in [(0, 0), (-h, -h), (h, -h), (-h, h), (h, h)]:
        for ring in _outer_rings():
            keep |= _inside(lon + dx, lat + dy, ring)
    return df[keep]
