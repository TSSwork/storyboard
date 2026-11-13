"""Rainfall across Sri Lanka, cell by cell, for the rain map (data/era5_rain_grid.csv, built by scripts/build_rain_grid.py).

No Streamlit here; tested in tests/test_rain_grid.py against the corrected national and Dambulla-box series.
"""
from functools import cache

import numpy as np
import pandas as pd

from story.common import DATA

BOXES = {"Dambulla": (7.86, 80.65), "Nuwara Eliya": (6.97, 80.77)}   # rain boxes used in the study, ±0.3°
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


def summary(month: pd.Timestamp) -> dict:
    m = month_map(month)
    w = np.cos(np.deg2rad(m.lat))
    top = m.loc[m.rain_mm.idxmax()]
    return dict(island_mm=float((m.rain_mm * w).sum() / w.sum()), wettest_mm=float(top.rain_mm), wettest_lat=float(top.lat),
                wettest_lon=float(top.lon), driest_mm=float(m.rain_mm.min()))
