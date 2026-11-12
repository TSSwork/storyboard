"""Shared constants, design tokens and data loaders. No plotting library is imported here.

All data is read from data/ (a snapshot, so this folder runs on its own).
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PAGES_DIR = ROOT / "story_pages"
EXPORT = ROOT / "storyboard"          # PNG export of the slides (optional; the app does not use it)

# ---- design tokens ----
# Palette: midnight navy (ink + primary), soft blue (tint), coral (the one accent: marks and caution only, never text)
NAVY, SOFT, CORAL = "#002941", "#b6dfed", "#fd6e6e"
PAPER, INK, MUTED, GRID = "#f6fafc", NAVY, "#52707f", "#d8e6ee"
TINT, RAIN, MID, BASE = "#e3f1f7", "#8cc0d6", "#2f7292", "#8aa3b2"
ACC, EXPL, BAD = NAVY, MID, CORAL
EVID_COL = {"supported": NAVY, "exploratory": SOFT, "no evidence": "#a9bcc7", "worse": CORAL}

VEGS = ["Cabbage", "Brinjal", "Carrot", "Tomato", "Snake gourd", "Pumpkin", "Beans"]
SLUGS = {1: "opening", 2: "scope_and_data", 3: "prices_and_rain", 4: "forecast_experiment", 5: "evaluation",
         6: "main_result", 7: "robustness", 8: "accuracy", 9: "wider_context", 10: "conclusions"}

# Stored v2 evidence label -> slide label (read from forecast_model_comparison_v2.csv, never re-derived)
EVID_LABEL = {"supported (corrected)": "supported", "suggestive (uncorrected only)": "exploratory",
              "no reliable evidence": "no evidence", "worse or no gain": "worse"}


# ---- data ----
def prices():
    """Monthly mean Dambulla wholesale price (LKR/kg, nominal); a month needs >= 10 valid daily prices."""
    cb = pd.read_csv(DATA / "cbsl_daily_prices.csv", comment="#", parse_dates=["period"]).set_index("period")
    out = {}
    for v in VEGS:
        col = [c for c in cb.columns if c.startswith(v + " (wholesale, dambulla)")][0]
        s = cb[col].dropna()
        cnt = s.resample("MS").count()
        out[v] = s.resample("MS").mean()[cnt >= 10]
    return pd.DataFrame(out)


def national_rain():
    """(monthly national rain in mm, past-only anomaly in units of 100 mm). Incomplete months are missing."""
    m = pd.read_csv(DATA / "era5_regional_monthly.csv", parse_dates=["month"]).set_index("month")
    r = m.rain_nat.where(m.n_nat == m.days_in_month)
    clim = []
    for t in r.index:
        past = r[(r.index.month == t.month) & (r.index.year < t.year)].dropna()
        clim.append(past.mean() if len(past) else np.nan)
    return r, (r - pd.Series(clim, index=r.index)) / 100


def comparison(market="dambulla", agg="mean", model="AR+rain:nat"):
    c = pd.read_csv(DATA / "forecast_model_comparison_v2.csv")
    c = c[(c.market == market) & (c.price_agg == agg) & (c.model == model)].set_index("commodity")
    return c.loc[VEGS]
