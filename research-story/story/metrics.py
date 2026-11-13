"""Plain-language numbers for the dashboard. Every value is read from data/; nothing is re-estimated.

No Streamlit here, so these functions are unit-tested in tests/test_metrics.py.
"""
from functools import cache

import numpy as np
import pandas as pd

from story.common import DATA, VEGS, prices

REGIONS = {"Whole island": "nat", "Around Dambulla": "dam", "Hill country (Nuwara Eliya)": "nuw"}
MARKETS = {"Dambulla": "dambulla", "Pettah (Colombo)": "pettah"}

# Stored v2 evidence label -> words for the public
PLAIN = {"supported (corrected)": "Clear help", "suggestive (uncorrected only)": "A hint, not proven",
         "no reliable evidence": "No clear effect", "worse or no gain": "No help"}
TONE = {"Clear help": "good", "A hint, not proven": "soft", "No clear effect": "flat", "No help": "bad"}


@cache
def _comparison():
    c = pd.read_csv(DATA / "forecast_model_comparison_v2.csv")
    return c[c.price_agg == "mean"]


@cache
def _results():
    r = pd.read_csv(DATA / "forecast_results_v2.csv", parse_dates=["target_month"])
    return r[r.price_agg == "mean"]


@cache
def _prices():
    return prices()


def _row(veg, model, market):
    c = _comparison()
    return c[(c.market == market) & (c.model == model) & (c.commodity == veg)].iloc[0]


def _inside(veg, model, market):
    r = _results()
    r = r[(r.market == market) & (r.model == model) & (r.commodity == veg)]
    hit = (r.lo80_log <= r.actual_log) & (r.actual_log <= r.hi80_log)
    return round(float(hit.mean()) * 10, 1)


def rain_kpis(veg: str, region: str, market: str) -> dict:
    model = f"AR+rain:{region}"
    base, rain = _row(veg, "AR", market), _row(veg, model, market)
    label = PLAIN[rain.evidence]
    return dict(miss_without=float(base.mae_lkr), miss_with=float(rain.mae_lkr), gain_pct=float(rain.rmse_gain_vs_AR_pct),
                label=label, tone=TONE[label], inside_without=_inside(veg, "AR", market),
                inside_with=_inside(veg, model, market), n=int(rain.n), mape_with=float(rain.mape_pct))


def verdicts(region: str, market: str) -> list[tuple[str, str, str]]:
    out = []
    for v in VEGS:
        lab = PLAIN[_row(v, f"AR+rain:{region}", market).evidence]
        out.append((v, lab, TONE[lab]))
    return out


def forecast_path(veg: str, region: str, market: str) -> pd.DataFrame:
    r = _results()
    r = r[(r.market == market) & (r.commodity == veg)]
    a = r[r.model == "AR"].set_index("target_month")
    b = r[r.model == f"AR+rain:{region}"].set_index("target_month")
    return pd.DataFrame({"actual": b.actual_lkr, "without": a.pred_lkr, "with": b.pred_lkr,
                         "lo": b.lo80_lkr, "hi": b.hi80_lkr}).sort_index().reset_index()


def month_changes(s: pd.Series) -> pd.Series:
    """Percent change between consecutive calendar months; a missing month gives NaN, never a bridged jump."""
    return s.asfreq("MS").pct_change(fill_method=None).dropna(how="all") * 100


def price_kpis(veg: str) -> dict:
    s = _prices()[veg].dropna()
    ch = month_changes(s).dropna()
    j = ch.abs().idxmax()
    return dict(low=float(s.min()), low_month=s.idxmin(), high=float(s.max()), high_month=s.idxmax(),
                jump_pct=float(ch[j]), jump_month=j, big_move_share=float((ch.abs() > 20).mean()), n_months=len(s))


# ---- "Spot the pattern": exploratory link between rain and next price change ----
# Same construction as the audited table (lag_correlations.csv, research_audit/feasibility_prices.py section D):
# monthly change in log price, minus that calendar month's average change; national rain as a z-score anomaly.
@cache
def _pattern_inputs():
    cb = pd.read_csv(DATA / "cbsl_daily_prices.csv", comment="#", parse_dates=["period"]).set_index("period")
    cols = {v: [c for c in cb.columns if c.startswith(v + " (wholesale, dambulla)")][0] for v in VEGS}
    logp = np.log(cb[list(cols.values())].resample("MS").mean())
    logp.columns = list(cols)
    mon = pd.read_csv(DATA / "era5_monthly.csv", parse_dates=["month"]).set_index("month")
    mon = mon[mon.days_in_month >= 28]
    g = mon.groupby(mon.index.month).rain_mm
    return logp, (mon.rain_mm - g.transform("mean")) / g.transform("std")


def pattern(veg: str, lag: int) -> pd.DataFrame:
    logp, z = _pattern_inputs()
    dp = logp[veg].diff()
    dp = dp - dp.groupby(dp.index.month).transform("mean")
    j = pd.concat([z.shift(lag).rename("rain_z"), (dp * 100).rename("price_chg")], axis=1).dropna()
    return j.rename_axis("month").reset_index()


def pattern_r(veg: str, lag: int) -> float:
    p = pattern(veg, lag)
    return float(np.corrcoef(p.rain_z, p.price_chg)[0, 1])


def strength_word(r: float) -> str:
    a = abs(r)
    return "Strong" if a >= 0.55 else "Moderate" if a >= 0.35 else "Weak" if a >= 0.15 else "Barely any"
