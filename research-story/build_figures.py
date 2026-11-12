"""Build the 18 storyboard images (storyboard/NN_slug/storyboard.png) from existing derived data.

Reads only; never modifies raw or research_audit files.
Run:  uv run python research-story/build_figures.py [page numbers...]
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
RA = WORK / "research_audit"
D = RA / "derived"
V2 = RA / "forecast_validation_v2"
OUT = ROOT / "storyboard"

# ---- design tokens (one accent; evidence class carried by colour AND label) ----
PAPER, INK, MUTED, GRID = "#fbfaf7", "#1c2430", "#667085", "#e6e2d9"
BASE, ACC, EXPL, BAD = "#8a929c", "#0f6b78", "#b7791f", "#a8403a"
EVID_COL = {"supported": ACC, "exploratory": EXPL, "no evidence": BASE, "worse": BAD}
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.facecolor": PAPER,
                     "figure.facecolor": PAPER, "axes.grid": False})

VEGS = ["Cabbage", "Brinjal", "Carrot", "Tomato", "Snake gourd", "Pumpkin", "Beans"]
SLUGS = {1: "opening", 2: "research_scope", 3: "data", 4: "price_series", 5: "rainfall_signal",
         6: "initial_evidence", 7: "forecast_experiment", 8: "evaluation_design", 9: "main_finding",
         10: "rain_window_check", 11: "geography_check", 12: "forecast_uncertainty",
         13: "what_is_established", 14: "paddy_and_weather", 15: "rice_imports", 16: "exchange_rates",
         17: "vulnerability_matrix", 18: "conclusion"}
ACTS = {**{i: "ACT I · FORECASTING STUDY" for i in range(1, 14)},
        **{i: "ACT II · FOOD-SYSTEM CONTEXT" for i in (14, 15, 16)},
        **{i: "ACT III · SYNTHESIS" for i in (17, 18)}}


def evidence(row_gain, p_holm):
    """Label used in v2/validation (primary comparison)."""
    if row_gain <= 0:
        return "worse"
    if p_holm < 0.05:
        return "supported"
    if p_holm < 0.15:
        return "exploratory"
    return "no evidence"


def frame(n, headline, source, sub=None):
    fig = plt.figure(figsize=(16, 9), dpi=100)
    fig.text(0.05, 0.945, f"{n:02d}  ·  {ACTS[n]}", fontsize=11, color=MUTED, fontweight="bold")
    fig.text(0.05, 0.885, headline, fontsize=23, fontweight="bold", va="center")
    if sub:
        fig.text(0.05, 0.835, sub, fontsize=12.5, color=MUTED, va="center")
    fig.text(0.05, 0.035, "Source: " + source, fontsize=9.5, color=MUTED)
    fig.text(0.95, 0.035, "Exploratory · not causal", fontsize=9.5, color=MUTED, ha="right")
    return fig


def save(fig, n):
    d = OUT / f"{n:02d}_{SLUGS[n]}"
    (d / "assets").mkdir(parents=True, exist_ok=True)
    fig.savefig(d / "storyboard.png", dpi=100, facecolor=PAPER)
    plt.close(fig)
    print("wrote", d / "storyboard.png")


def box(ax, xy, w, h, text, fc="white", ec=GRID, tc=INK, fs=12, bold=False, lw=1.4):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.01,rounding_size=0.015", fc=fc, ec=ec, lw=lw))
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=fs, color=tc,
            fontweight="bold" if bold else "normal", linespacing=1.4)


def arrow(ax, a, b, col=MUTED):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=16, lw=1.6, color=col))


def blank(fig, rect=(0.05, 0.08, 0.9, 0.7)):
    ax = fig.add_axes(rect)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    return ax


# ---- data ----
def prices():
    cb = pd.read_csv(WORK / "raw/cbsl-daily-prices.csv", comment="#", parse_dates=["period"]).set_index("period")
    out = {}
    for v in VEGS:
        col = [c for c in cb.columns if c.startswith(v + " (wholesale, dambulla)")][0]
        s = cb[col].dropna()
        cnt = s.resample("MS").count()
        m = s.resample("MS").mean()[cnt >= 10]
        out[v] = m
    return pd.DataFrame(out)


def national_rain():
    m = pd.read_csv(D / "era5_regional_monthly.csv", parse_dates=["month"]).set_index("month")
    r = m.rain_nat.where(m.n_nat == m.days_in_month)
    clim = []
    for t in r.index:
        past = r[(r.index.month == t.month) & (r.index.year < t.year)].dropna()
        clim.append(past.mean() if len(past) else np.nan)
    return r, (r - pd.Series(clim, index=r.index)) / 100


def comp():
    c = pd.read_csv(RA / "forecast_model_comparison_v2.csv")
    c = c[(c.market == "dambulla") & (c.price_agg == "mean") & (c.model == "AR+rain:nat")].set_index("commodity")
    return c.loc[VEGS]


def style_axes(ax, grid_y=True):
    ax.tick_params(length=0, labelsize=10)
    if grid_y:
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)


# ---------------- pages ----------------
def p01():
    fig = frame(1, "Can rainfall help anticipate vegetable prices?",
                "CBSL daily wholesale prices (Dambulla); ERA5-Land corrected national rainfall", "One-month-ahead forecasts, tested out of sample. Not a claim that rain causes price changes.")
    pr = prices()["Cabbage"].loc["2016":]
    a = fig.add_axes([0.06, 0.45, 0.88, 0.27])
    a.plot(pr.index, pr.values, color=ACC, lw=2)
    a.set_ylabel("Cabbage, LKR/kg (nominal)", fontsize=10); style_axes(a)
    a.set_xticklabels([])
    r, _ = national_rain()
    r = r.loc["2016":]
    b = fig.add_axes([0.06, 0.13, 0.88, 0.22])
    b.bar(r.index, r.values, width=24, color=BASE)
    b.set_ylabel("National rain, mm/month", fontsize=10); style_axes(b)
    fig.text(0.5, 0.775, "Wholesale price and observed rainfall, 2016–2026", ha="center", fontsize=11, color=MUTED)
    save(fig, 1)


def p02():
    fig = frame(2, "One country, seven vegetables, one month ahead",
                "CBSL daily prices; ERA5-Land; boxes are ±0.3° hand-drawn proxies, not growing areas")
    g = json.load(open(WORK / "raw/chirp/boundaries/countries.geojson"))
    f = [x for x in g["features"] if x["properties"].get("ISO3166-1-Alpha-3") == "LKA"][0]
    polys = f["geometry"]["coordinates"]
    ax = fig.add_axes([0.05, 0.08, 0.38, 0.72])
    for poly in polys:
        for ring in poly:
            xs, ys = zip(*ring)
            ax.fill(xs, ys, fc="#efece4", ec=BASE, lw=1)
    pts = {"Dambulla": (80.65, 7.86, ACC), "Nuwara Eliya": (80.77, 6.97, EXPL)}
    for nme, (x, y, c) in pts.items():
        ax.add_patch(Rectangle((x - 0.3, y - 0.3), 0.6, 0.6, fc="none", ec=c, ls="--", lw=1.6))
        ax.plot(x, y, "o", color=c, ms=7)
        ax.annotate(nme + " box", (x + 0.32, y), fontsize=10, color=c, va="center")
    ax.plot(79.85, 6.94, "s", color=INK, ms=7)
    ax.annotate("Pettah (robustness market)", (79.9, 6.7), fontsize=10, va="top")
    ax.set_aspect(1); ax.axis("off")
    box_ax = fig.add_axes([0.47, 0.08, 0.48, 0.72]); box_ax.axis("off"); box_ax.set_xlim(0, 1); box_ax.set_ylim(0, 1)
    rows = [("Main market", "CBSL Dambulla wholesale"), ("Robustness check", "Pettah wholesale (not independent validation)"),
            ("Vegetables", "cabbage · brinjal · carrot · tomato\nsnake gourd · pumpkin · beans"),
            ("Frequency", "monthly mean of valid daily prices (≥10 days)"), ("Horizon", "one month ahead"),
            ("Extra information", "observed rainfall only (no rainfall forecasts)")]
    for i, (k, v) in enumerate(rows):
        y = 0.92 - i * 0.155
        box_ax.text(0, y, k.upper(), fontsize=9.5, color=MUTED, fontweight="bold", va="top")
        box_ax.text(0, y - 0.04, v, fontsize=13, va="top", linespacing=1.35)
    save(fig, 2)


def p03():
    fig = frame(3, "Two sources, explicit rules for aggregation and missing data",
                "CBSL via Macro Lab; ERA5-Land (corrected accumulation); research_audit/07_data_quality_report.md")
    ax = blank(fig)
    steps_top = ["CBSL daily\nwholesale prices", "Monthly mean\n(≥10 valid days)", "log price\n(forecast target)"]
    steps_bot = ["ERA5-Land hourly\nprecipitation", "Corrected daily\nrainfall", "Monthly rainfall\n(complete months only)", "Anomaly\n(past-only climatology)"]
    for i, t in enumerate(steps_top):
        box(ax, (0.02 + i * 0.22, 0.68), 0.17, 0.2, t, fs=12)
        if i: arrow(ax, (0.02 + i * 0.22 - 0.05, 0.78), (0.02 + i * 0.22, 0.78))
    for i, t in enumerate(steps_bot):
        box(ax, (0.02 + i * 0.22, 0.3), 0.17, 0.2, t, fs=12)
        if i: arrow(ax, (0.02 + i * 0.22 - 0.05, 0.4), (0.02 + i * 0.22, 0.4))
    box(ax, (0.80, 0.52), 0.19, 0.2, "Forecasting\nexperiment", fc=ACC, ec=ACC, tc="white", bold=True, fs=13)
    arrow(ax, (0.60, 0.78), (0.80, 0.66)); arrow(ax, (0.82, 0.40), (0.90, 0.52))
    notes = ["⚠ The earlier ERA5 precipitation bug (overstated totals) is fixed; only corrected series are used.",
             "Incomplete rainfall months (2009-12, 2026-11) are set to missing, never used as partial totals.",
             "Prices are nominal. No deflator is applied."]
    for i, t in enumerate(notes):
        ax.text(0.02, 0.17 - i * 0.065, t, fontsize=12, color=INK if i else BAD)
    save(fig, 3)


def p04():
    fig = frame(4, "Prices have their own dynamics — rainfall must add to them",
                "CBSL Dambulla wholesale, monthly mean; nominal LKR/kg; shaded = 2022")
    pr = prices()
    gs = fig.add_gridspec(2, 4, left=0.05, right=0.96, bottom=0.1, top=0.78, hspace=0.45, wspace=0.25)
    for i, v in enumerate(VEGS):
        ax = fig.add_subplot(gs[i // 4, i % 4])
        s = pr[v].dropna()
        ax.axvspan(pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31"), color=GRID, lw=0)
        ax.plot(s.index, s.values, color=ACC, lw=1.6)
        ax.set_title(v, fontsize=12, loc="left", fontweight="bold"); style_axes(ax)
        ax.tick_params(labelsize=8.5)
    ax = fig.add_subplot(gs[1, 3]); ax.axis("off")
    ax.text(0, 0.85, "Forecast target:\nlog of the monthly\nmean price", fontsize=12, va="top", linespacing=1.5)
    ax.text(0, 0.3, "Nominal prices — rising lines\nare not real-price changes.", fontsize=10.5, color=MUTED, va="top")
    save(fig, 4)


def p05():
    fig = frame(5, "Rain becomes a predictor through past-only anomalies",
                "ERA5-Land corrected; research_audit/derived/era5_regional_monthly.csv",
                "Anomaly = (rain − mean of the same calendar month in earlier years) / 100 mm")
    _, an = national_rain()
    an = an.loc["2016":]
    a = fig.add_axes([0.06, 0.34, 0.88, 0.38])
    a.bar(an.index, an.values, width=24, color=[ACC if v >= 0 else EXPL for v in an.fillna(0)])
    a.axhline(0, color=INK, lw=0.8); a.set_ylabel("anomaly (×100 mm)", fontsize=10); style_axes(a)
    a.text(0.01, 0.92, "wetter than usual ▲", transform=a.transAxes, color=ACC, fontsize=10)
    a.text(0.01, 0.06, "drier than usual ▼", transform=a.transAxes, color=EXPL, fontsize=10)
    ax = fig.add_axes([0.06, 0.07, 0.88, 0.2]); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 2)
    for i, lab in enumerate(["t−3", "t−2", "t−1", "t"]):
        ax.add_patch(Rectangle((i * 1.2, 0.6), 1.1, 0.8, fc="white", ec=GRID))
        ax.text(i * 1.2 + 0.55, 1.0, lab, ha="center", va="center", fontsize=11)
    ax.add_patch(Rectangle((4 * 1.2 - 1.2, 0.6), 1.1, 0.8, fc="#dff0f2", ec=ACC, lw=2))
    ax.text(4.9, 1.45, "A0 = month t", fontsize=11, color=ACC, fontweight="bold")
    ax.text(4.9, 0.95, "A3 (primary) = mean of t−2, t−1, t  → overlaps A0 (corr 0.57)", fontsize=11)
    ax.text(4.9, 0.45, "A3 (check)  = mean of t−3, t−2, t−1  → no overlap (corr −0.05)", fontsize=11)
    ax.text(4.9, -0.05, "Neither uses future rain: both are known when the forecast is made.", fontsize=10.5, color=MUTED)
    save(fig, 5)


def p06():
    lag = pd.DataFrame({0: [0.10, 0.03, -0.06, 0.19, 0.16, 0.02, 0.21], 1: [0.60, 0.40, 0.44, 0.26, 0.20, 0.14, 0.08],
                        2: [0.16, -0.29, 0.20, 0.01, -0.15, 0.04, 0.03], 3: [-0.06, 0.18, 0.00, -0.26, -0.14, -0.07, -0.09]},
                       index=VEGS)
    lag.to_csv(ROOT / "storyboard/06_initial_evidence/assets/lag_correlations.csv")
    fig = frame(6, "Exploratory correlations motivate the test — they are not the result",
                "research_audit/_profiles/prices_out.txt (section D): de-seasonalised Δlog price vs national rain anomaly",
                "10 of 28 tests had p<0.05 (about 1.4 expected by chance). Many tests, short series.")
    a = fig.add_axes([0.08, 0.1, 0.5, 0.65])
    im = a.imshow(lag.values, cmap="RdBu_r", vmin=-0.6, vmax=0.6, aspect="auto")
    a.set_xticks(range(4)); a.set_xticklabels([f"lag {k}" for k in range(4)], fontsize=11)
    a.set_yticks(range(7)); a.set_yticklabels(VEGS, fontsize=12)
    a.xaxis.tick_top(); a.tick_params(length=0)
    for i in range(7):
        for j in range(4):
            a.text(j, i, f"{lag.values[i, j]:+.2f}", ha="center", va="center", fontsize=11,
                   color="white" if abs(lag.values[i, j]) > 0.35 else INK, fontweight="bold" if (j == 1 and i < 3) else "normal")
    for s in a.spines.values(): s.set_visible(False)
    a.add_patch(Rectangle((0.5, -0.5), 1, 3, fill=False, ec=INK, lw=2.5))
    t = fig.add_axes([0.63, 0.1, 0.32, 0.65]); t.axis("off")
    t.text(0, 0.95, "What stands out", fontsize=13, fontweight="bold", va="top")
    t.text(0, 0.86, "Lag-1 (rain last month):\ncabbage +0.60, carrot +0.44,\nbrinjal +0.40.\n\n3-month cumulative anomaly:\ncabbage +0.37, carrot +0.34.\n\nThese pick the commodities to\nlook at — the forecast test, not\nthe correlation, is the evidence.",
           fontsize=12, va="top", linespacing=1.4)
    save(fig, 6)


def p07():
    fig = frame(7, "The test: does rainfall improve a model that already knows past prices?",
                "research_audit/forecast_backtest_report_v2.md", "At the end of month t, two models forecast the price of month t+1")
    ax = blank(fig)
    box(ax, (0.02, 0.74), 0.3, 0.2, "Price-only AR\nlag set chosen by AIC\non the training window", fs=12, bold=True)
    box(ax, (0.02, 0.4), 0.3, 0.26, "AR + rainfall\nthe SAME price lags\n+ A0 and A3 (rain through t)", fc="#dff0f2", ec=ACC, fs=12, bold=True)
    box(ax, (0.55, 0.57), 0.2, 0.2, "Forecast of\nprice in t+1", fs=13, bold=True)
    arrow(ax, (0.32, 0.84), (0.55, 0.7)); arrow(ax, (0.32, 0.53), (0.55, 0.64))
    box(ax, (0.82, 0.57), 0.17, 0.2, "Compare\nout-of-sample\nerrors", fs=12)
    arrow(ax, (0.75, 0.67), (0.82, 0.67))
    for i, t in enumerate(["Expanding window, refit at every origin", "Naive and seasonal-naive benchmarks also scored",
                           "FX excluded: it worsened every forecast in the pilot", "No machine learning, no future rainfall"]):
        ax.text(0.02, 0.26 - i * 0.07, "•  " + t, fontsize=12.5, color=INK)
    save(fig, 7)


def p08():
    fig = frame(8, "62 one-month-ahead forecasts per vegetable, from an expanding window",
                "forecast_validation_v2/evaluation_samples.csv",
                "Test period was already seen in the pilot → exploratory; the 62 errors are serially dependent")
    ax = blank(fig, (0.05, 0.12, 0.9, 0.62))
    for k, y in enumerate([0.8, 0.62, 0.44]):
        w = 0.5 + k * 0.1
        ax.add_patch(Rectangle((0.02, y), w, 0.1, fc="#dfe7ea", ec="none"))
        ax.add_patch(Rectangle((0.02 + w, y), 0.035, 0.1, fc=ACC, ec="none"))
        ax.text(0.02 + w / 2, y + 0.05, "training data", ha="center", va="center", fontsize=11)
        ax.text(0.02 + w + 0.06, y + 0.05, "forecast t+1", va="center", fontsize=11, color=ACC)
    ax.text(0.02, 0.35, "⋮ refit and forecast at each of 62 origins", fontsize=11, color=MUTED)
    ax.text(0.02, 0.2, "Origins Aug 2021 → Sep 2026  ·  targets Sep 2021 → Oct 2026  ·  n = 62 per vegetable", fontsize=12.5, fontweight="bold")
    ax.text(0.02, 0.09, "Tests: Clark–West (nested, Newey–West lag 3) · Diebold–Mariano (supplementary) · moving-block bootstrap (3/6/12) · Holm across 7 vegetables",
            fontsize=11.5, color=INK)
    save(fig, 8)


def p09():
    c = comp()
    gain, p = c.rmse_gain_vs_AR_pct.values, c.cw_p_holm.values
    ev = [evidence(g, q) for g, q in zip(gain, p)]
    fig = frame(9, "Rainfall helps some vegetables far more than others",
                "forecast_model_comparison_v2.csv · Dambulla wholesale, national ERA5 rain, 62 forecasts each",
                "Bar = size of improvement. Colour and label = strength of evidence (Holm-adjusted Clark–West p).")
    a = fig.add_axes([0.14, 0.1, 0.5, 0.64])
    y = np.arange(7)[::-1]
    a.barh(y, gain, color=[EVID_COL[e] for e in ev], height=0.62)
    a.axvline(0, color=INK, lw=1)
    a.set_yticks(y); a.set_yticklabels(VEGS, fontsize=13)
    a.set_xlabel("RMSE reduction vs price-only AR (%)", fontsize=11); a.tick_params(length=0, labelsize=10)
    for yy, g in zip(y, gain):
        a.text(g + (0.5 if g >= 0 else -0.5), yy, f"{g:+.1f}%", va="center", ha="left" if g >= 0 else "right", fontsize=12, fontweight="bold")
    a.set_xlim(-4, 24)
    t = fig.add_axes([0.68, 0.1, 0.28, 0.64]); t.axis("off"); t.set_ylim(-0.5, 6.5); t.set_xlim(0, 1)
    t.text(0, 6.75, "Holm p", fontsize=10.5, color=MUTED, fontweight="bold")
    t.text(0.4, 6.75, "Evidence", fontsize=10.5, color=MUTED, fontweight="bold")
    lab = {"supported": "supported", "exploratory": "exploratory only", "no evidence": "no reliable evidence", "worse": "rain does not help"}
    for yy, q, e in zip(y, p, ev):
        t.text(0, yy, f"{q:.4f}" if q < 0.01 else f"{q:.3f}", va="center", fontsize=12)
        t.text(0.4, yy, "● " + lab[e], va="center", fontsize=11.5, color=EVID_COL[e], fontweight="bold")
    save(fig, 9)


def p10():
    rw = pd.read_csv(V2 / "rain_window_comparison.csv").set_index(["commodity", "model"])
    prim = [rw.loc[(v, "nat_incl"), "rmse_gain_vs_AR_pct"] for v in VEGS]
    prior = [rw.loc[(v, "nat_prior"), "rmse_gain_vs_AR_pct"] for v in VEGS]
    fig = frame(10, "The ranking survives removing the overlap between A0 and A3",
                "forecast_validation_v2/rain_window_comparison.csv · national rain",
                "No vegetable changes evidence class. Brinjal is the most sensitive (−2.0 pp).")
    a = fig.add_axes([0.1, 0.12, 0.84, 0.62])
    x = np.arange(7); w = 0.36
    a.bar(x - w / 2, prim, w, color=ACC, label="Primary: A3 = mean(t−2…t)")
    a.bar(x + w / 2, prior, w, color="#7fb3ba", label="Check: A3 = mean(t−3…t−1)")
    a.axhline(0, color=INK, lw=1)
    for xi, p1, p2 in zip(x, prim, prior):
        a.text(xi - w / 2, p1 + (0.4 if p1 >= 0 else -0.4), f"{p1:.1f}", ha="center", va="bottom" if p1 >= 0 else "top", fontsize=10)
        a.text(xi + w / 2, p2 + (0.4 if p2 >= 0 else -0.4), f"{p2:.1f}", ha="center", va="bottom" if p2 >= 0 else "top", fontsize=10)
    a.set_xticks(x); a.set_xticklabels(VEGS, fontsize=12); a.set_ylabel("RMSE reduction vs AR (%)", fontsize=11)
    style_axes(a); a.legend(frameon=False, fontsize=11, loc="upper right")
    fig.text(0.05, 0.075, "Multiplicity: one tomato cell (Dambulla box, non-overlapping window) reaches Holm p = 0.036. It is one of six specifications and is NOT promoted.",
             fontsize=10.5, color=EXPL)
    save(fig, 10)


def p11():
    rw = pd.read_csv(V2 / "rain_window_comparison.csv").set_index(["commodity", "model"])
    specs = [("nat_incl", "National (primary)", ACC), ("dam_incl", "Dambulla box", EXPL), ("nuw_incl", "Nuwara Eliya box", BASE)]
    fig = frame(11, "The pattern holds across rainfall geographies",
                "forecast_validation_v2/rain_window_comparison.csv · primary A3 window",
                "Boxes are ±0.3° hand-drawn proxies, not crop-growing areas. Pettah is a consistency check, not replication.")
    a = fig.add_axes([0.1, 0.12, 0.84, 0.62]); x = np.arange(7); w = 0.27
    for k, (m, lab, col) in enumerate(specs):
        vals = [rw.loc[(v, m), "rmse_gain_vs_AR_pct"] for v in VEGS]
        a.bar(x + (k - 1) * w, vals, w, color=col, label=lab)
    a.axhline(0, color=INK, lw=1); a.set_xticks(x); a.set_xticklabels(VEGS, fontsize=12)
    a.set_ylabel("RMSE reduction vs AR (%)", fontsize=11); style_axes(a); a.legend(frameon=False, fontsize=11)
    save(fig, 11)


def p12():
    r = pd.read_csv(RA / "forecast_results_v2.csv", parse_dates=["origin", "target_month"])
    r = r[(r.market == "dambulla") & (r.price_agg == "mean") & (r.commodity == "Cabbage")]
    ar = r[r.model == "AR"].set_index("target_month"); rn = r[r.model == "AR+rain:nat"].set_index("target_month")
    mc = comp(); ic = pd.read_csv(V2 / "interval_coverage.csv")
    ic = ic[ic.model == "nat_incl"].set_index("commodity").loc[VEGS]
    fig = frame(12, "Better does not mean accurate: errors stay large, bands under-cover",
                "forecast_results_v2.csv; forecast_validation_v2/interval_coverage.csv",
                "Cabbage, Dambulla. Empirical 80% bands from past out-of-sample errors.")
    a = fig.add_axes([0.06, 0.1, 0.56, 0.64])
    a.fill_between(rn.index, rn.lo80_lkr, rn.hi80_lkr, color=ACC, alpha=0.14, lw=0, label="AR+rain 80% band")
    a.plot(ar.index, ar.actual_lkr, color=INK, lw=2, label="Actual")
    a.plot(ar.index, ar.pred_lkr, color=BASE, lw=1.6, label="Price-only AR")
    a.plot(rn.index, rn.pred_lkr, color=ACC, lw=2, label="AR + rain")
    a.set_ylabel("LKR/kg", fontsize=10); style_axes(a); a.legend(frameon=False, fontsize=10, loc="upper left")
    t = fig.add_axes([0.67, 0.1, 0.29, 0.64]); t.axis("off"); t.set_xlim(0, 1); t.set_ylim(-0.5, 7.5)
    t.text(0, 7.4, "", fontsize=1)
    t.text(0.38, 7.2, "MAPE %", fontsize=10, color=MUTED, fontweight="bold"); t.text(0.72, 7.2, "80% cover", fontsize=10, color=MUTED, fontweight="bold")
    for i, v in enumerate(VEGS):
        yy = 6.4 - i
        t.text(0, yy, v, fontsize=11.5, va="center")
        t.text(0.4, yy, f"{mc.loc[v, 'mape_pct']:.1f}", fontsize=11.5, va="center")
        cov = ic.loc[v, "coverage"]
        t.text(0.74, yy, f"{cov:.2f}", fontsize=11.5, va="center", color=INK if cov >= 0.75 else BAD)
    t.text(0, -0.4, "Nominal coverage 0.80; red = below 0.75.", fontsize=9.5, color=MUTED)
    save(fig, 12)


def p13():
    import textwrap
    fig = frame(13, "What the forecasting chapter does and does not establish", "v2 backtest, validation report, 06_recommended_research_direction.md")
    ax = blank(fig, (0.05, 0.08, 0.9, 0.74))
    cols = [("SUPPORTED (primary, corrected)", ACC, ["Rain adds out-of-sample information beyond past prices for cabbage and brinjal", "Carrot: positive and corrected-significant, but modest and borderline", "Benefit is commodity-specific"]),
            ("EXPLORATORY", EXPL, ["Tomato: +4.8%, Holm p = 0.109", "Geography, anomaly and window variants are sensitivity checks, not new findings", "Pettah shows the same pattern (consistency, not replication)"]),
            ("NOT ESTABLISHED", BAD, ["That rain causes price changes", "Skill at 2-3 month horizons or for consumer prices", "Calibrated 80% intervals", "Independent confirmation on a new test period"])]
    for i, (h, c, items) in enumerate(cols):
        x0 = 0.01 + i * 0.335
        ax.add_patch(Rectangle((x0, 0.0), 0.32, 1.0, fc="white", ec=GRID))
        ax.add_patch(Rectangle((x0, 0.95), 0.32, 0.05, fc=c, ec="none"))
        ax.text(x0 + 0.015, 0.87, h, fontsize=12.5, fontweight="bold", color=c, va="center")
        y = 0.77
        for it in items:
            t = "\n".join(textwrap.wrap(it, 34))
            ax.text(x0 + 0.015, y, t, fontsize=12.5, va="top", linespacing=1.4)
            y -= 0.06 + 0.055 * (t.count("\n") + 1)
    save(fig, 13)


def p14():
    mon = pd.read_csv(D / "era5_monthly.csv", parse_dates=["month"]).set_index("month")
    yl = pd.read_csv(D / "dcs_national_yala.csv")
    yl["y"] = yl.season_label.astype(str).str[:4].astype(int); yl = yl[(yl.y >= 2010) & (yl.y <= 2025)].copy()
    yl["rain"] = [mon.loc[f"{y}-03":f"{y}-08", "rain_mm"].sum() for y in yl.y]
    yl["hs"] = yl.harv_000ha / yl.sown_000ha

    def detr(s, yrs):
        b = np.polyfit(yrs, s, 1); return s - np.polyval(b, yrs)
    x, yv = detr(yl.rain.values, yl.y.values), detr(yl.hs.values, yl.y.values)
    r = np.corrcoef(x, yv)[0, 1]
    fig = frame(14, "Paddy: Yala rainfall tracks how much of the sown area is harvested",
                "ERA5-Land national (Mar–Aug) vs DCS Yala harvested/sown ratio; both detrended; 2010–2025",
                f"r = {r:+.2f}, n = {len(yl)}. Short series, policy shocks (2021–22) → association only.")
    a = fig.add_axes([0.08, 0.1, 0.4, 0.64])
    a.scatter(x, yv, s=60, color=ACC, zorder=3)
    for xi, yi, yy in zip(x, yv, yl.y):
        if yy in (2017, 2022): a.annotate(str(yy), (xi, yi), xytext=(6, 4), textcoords="offset points", fontsize=10)
    b = np.polyfit(x, yv, 1); xs = np.linspace(x.min(), x.max(), 10); a.plot(xs, np.polyval(b, xs), color=BASE, lw=1.5)
    a.set_xlabel("Yala rain (Mar–Aug), detrended, mm", fontsize=10); a.set_ylabel("harvested / sown, detrended", fontsize=10); style_axes(a)
    rb = pd.read_csv(D / "rice_annual_balance.csv"); rb = rb[(rb.y >= 2010) & (rb.y <= 2025)]
    b2 = fig.add_axes([0.58, 0.1, 0.38, 0.64])
    b2.plot(rb.y, rb.rice_eq_000t, color=ACC, lw=2, label="Rice-equivalent production")
    b2.plot(rb.y, rb.fao_rice_imp_000t, color=EXPL, lw=2, label="Rice imports (FAOSTAT)")
    b2.set_ylabel("'000 tonnes", fontsize=10); style_axes(b2); b2.legend(frameon=False, fontsize=10)
    fig.text(0.58, 0.77, "Production vs imports: r = −0.79 (n = 15); −0.46 without 2017 and 2022", fontsize=10.5, color=MUTED)
    save(fig, 14)


def p15():
    rb = pd.read_csv(D / "rice_annual_balance.csv"); rb = rb[(rb.y >= 2010) & (rb.y <= 2025)]
    fig = frame(15, "Rice imports: an apparent import share, not self-sufficiency",
                "FAOSTAT production and trade; UN Comtrade (gap 2018, partial 2025); research_audit/derived/rice_annual_balance.csv",
                "Apparent import share = imports / (rice-equivalent production + imports). Stocks, feed, seed, waste not modelled.")
    a = fig.add_axes([0.08, 0.1, 0.5, 0.64])
    share = rb.fao_rice_imp_000t / (rb.rice_eq_000t + rb.fao_rice_imp_000t) * 100
    a.bar(rb.y, share, color=EXPL, width=0.7); a.set_ylabel("apparent import share, %", fontsize=10); style_axes(a)
    t = fig.add_axes([0.63, 0.1, 0.33, 0.64]); t.axis("off")
    t.text(0, 0.95, "Cautions", fontsize=13, fontweight="bold", va="top")
    t.text(0, 0.86, "• Paddy → milled rice needs a\n  conversion assumption.\n\n• Comtrade has no 2018 annual\n  data; 2025 is partial.\n\n• FAO and Comtrade overlap —\n  agreement is cross-checking,\n  not independent confirmation.\n\n• Partner-concentration view\n  still to be built (S3).",
           fontsize=11.5, va="top", linespacing=1.4)
    save(fig, 15)


def p16():
    fx = pd.read_csv(WORK / "raw/pdf/Indicative Rate of the USD_LKR SPOT Exchange Rate.csv", parse_dates=["Date"]).set_index("Date")["Exchange Rate"].resample("MS").mean()
    fig = frame(16, "Exchange-rate exposure: co-movement is visible, pass-through is not yet measured",
                "CBSL USD/LKR; research_audit/_profiles/prices_out.txt (section C); rice vs FX correlations at lag 0–1",
                "Provisional: needs CPI/NCPI to deflate prices. FX is not a predictor in the S1+ model.")
    a = fig.add_axes([0.07, 0.1, 0.5, 0.64]); a.plot(fx.index, fx.values, color=EXPL, lw=2); a.set_ylabel("USD/LKR, monthly mean", fontsize=10); style_axes(a)
    a.axvspan(pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31"), color=GRID, lw=0)
    b = fig.add_axes([0.66, 0.1, 0.29, 0.64])
    names = ["Samba 1", "Nadu 1", "Raw Red", "Raw White", "Keeri Samba"]; vals = [0.36, 0.36, 0.34, 0.30, 0.13]
    b.barh(names[::-1], vals[::-1], color=BASE); b.set_xlim(0, 0.5); b.set_xlabel("corr(Δlog rice price, Δlog USD/LKR), lag 0", fontsize=9.5); style_axes(b, False)
    for i, v in enumerate(vals[::-1]): b.text(v + 0.01, i, f"{v:.2f}", va="center", fontsize=10.5)
    save(fig, 16)


def p17():
    fig = frame(17, "Vulnerability has several dimensions — shown side by side, never summed",
                "S1+/S2 forecasts and paddy; S3 rice balance; S4 exchange rates", "No weighted composite score: the evidence behind each dimension differs in strength.")
    ax = blank(fig)
    heads = ["Dimension", "Evidence", "What it measures", "Strength"]
    xs = [0.01, 0.2, 0.45, 0.82]
    for x, h in zip(xs, heads): ax.text(x, 0.92, h.upper(), fontsize=10.5, color=MUTED, fontweight="bold")
    rows = [("Weather sensitivity", "S1+ forecasts · S2 paddy", "Predictive relationship with vegetable prices; rain vs paddy outcomes", "Strongest: 62 out-of-sample months (exploratory)", ACC),
            ("Import exposure", "S3 rice balance", "Apparent import share; partner concentration (to build)", "Moderate: n ≈ 15 years, sensitive to 2017/2022", EXPL),
            ("Exchange-rate exposure", "S4 FX vs prices", "Co-movement; pass-through after CPI/NCPI deflation", "Provisional: no deflator yet", BASE)]
    for i, (a, b, c, d, col) in enumerate(rows):
        y = 0.62 - i * 0.3
        ax.add_patch(Rectangle((0, y - 0.04), 1, 0.25, fc="white", ec=GRID))
        ax.add_patch(Rectangle((0, y - 0.04), 0.008, 0.25, fc=col, ec="none"))
        ax.text(xs[0] + 0.015, y + 0.08, a, fontsize=14, fontweight="bold", va="center")
        ax.text(xs[1], y + 0.08, b, fontsize=12, va="center")
        ax.text(xs[2], y + 0.08, c.replace("; ", ";\n"), fontsize=11.5, va="center", linespacing=1.4)
        ax.text(xs[3], y + 0.08, d.replace(": ", ":\n"), fontsize=11.5, va="center", color=col, linespacing=1.4)
    save(fig, 17)


def p18():
    fig = frame(18, "Rainfall carries short-term price information for some vegetables — not all, not precisely",
                "Synthesis of pages 1–17")
    ax = blank(fig)
    ax.text(0.01, 0.95, "THREE FINDINGS", fontsize=11, fontweight="bold", color=ACC)
    ax.text(0.52, 0.95, "THREE LIMITATIONS", fontsize=11, fontweight="bold", color=BAD)
    fnd = ["Observed rainfall improves one-month-ahead forecasts for selected vegetables, most for cabbage and brinjal.",
           "Predictive value is commodity-specific: snake gourd, pumpkin and beans show little or none.",
           "Paddy, rice imports and exchange rates are distinct, context-setting dimensions of vulnerability."]
    lim = ["The test window was seen in the pilot: exploratory, not independent confirmation.",
           "Rain series are geographic proxies, not rainfall in the actual growing areas.",
           "Context analyses: short series, crisis confounding, incomplete trade data, no deflator yet."]
    import textwrap
    for i, (f, l) in enumerate(zip(fnd, lim)):
        y = 0.82 - i * 0.2
        ax.text(0.01, y, f"{i+1}", fontsize=22, color=ACC, fontweight="bold", va="top")
        ax.text(0.045, y, "\n".join(textwrap.wrap(f, 46)), fontsize=13, va="top", linespacing=1.4)
        ax.text(0.52, y, f"{i+1}", fontsize=22, color=BAD, fontweight="bold", va="top")
        ax.text(0.555, y, "\n".join(textwrap.wrap(l, 46)), fontsize=13, va="top", linespacing=1.4)
    ax.add_patch(Rectangle((0, 0.02), 1, 0.15, fc="white", ec=GRID))
    ax.text(0.015, 0.095, "Research finding, not a deployable forecasting tool. The contribution is where rainfall adds information — and where it does not.",
            fontsize=12.5, va="center", fontweight="bold")
    save(fig, 18)


PAGES = {i: globals()[f"p{i:02d}"] for i in range(1, 19)}

if __name__ == "__main__":
    for d in [OUT / f"{n:02d}_{s}" for n, s in SLUGS.items()]:
        (d / "assets").mkdir(parents=True, exist_ok=True)
    todo = [int(a) for a in sys.argv[1:]] or list(PAGES)
    for n in todo:
        PAGES[n]()
